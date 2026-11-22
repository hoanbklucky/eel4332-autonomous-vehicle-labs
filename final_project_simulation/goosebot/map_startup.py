#!/usr/bin/env python3
"""Configure/activate the campus map and verify retained data before Nav2 starts.

Timeouts use wall time, so a paused/slow simulation cannot freeze startup.
This process owns only map_server lifecycle; Nav2 manages its other nodes.
"""
import argparse
import math
from pathlib import Path
import time


def expected_map(path):
    import yaml
    from PIL import Image
    path=Path(path).expanduser().resolve()
    data=yaml.safe_load(path.read_text())
    with Image.open(path.parent/data['image']) as raster:
        width,height=raster.size
    resolution=float(data['resolution']);origin=list(map(float,data['origin']))
    if (width<1 or height<1 or not math.isfinite(resolution) or resolution<=0
            or len(origin)!=3 or not all(map(math.isfinite,origin))):
        raise ValueError('Invalid expected campus map geometry')
    return dict(width=width,height=height,resolution=resolution,origin=origin)


def check_map(message, expected):
    info=message.info;p=info.origin.position;q=info.origin.orientation
    if (message.header.frame_id!='map' or info.width!=expected['width']
            or info.height!=expected['height']
            or not math.isclose(info.resolution,expected['resolution'],abs_tol=1e-7)
            or len(message.data)!=info.width*info.height):
        raise ValueError('Received /map geometry/frame does not match the selected campus map')
    values=[p.x,p.y,p.z,q.x,q.y,q.z,q.w]
    if not all(map(math.isfinite,values)):
        raise ValueError('Non-finite /map origin')
    angle=expected['origin'][2]
    wanted=[expected['origin'][0],expected['origin'][1],0.,0.,0.,math.sin(angle/2),math.cos(angle/2)]
    if any(abs(a-b)>1e-6 for a,b in zip(values,wanted)):
        raise ValueError('Received /map origin does not match the selected campus map')


def activate_and_wait(get_state, change_state, received, pump, deadline, clock=time.monotonic):
    """Testable lifecycle/data gate. Never start navigation on lifecycle alone."""
    def remaining():
        value=deadline-clock()
        if value<=0:
            raise TimeoutError('Campus map startup timed out; inspect map_server logs. Nav2 was not started.')
        return value
    remaining();state=get_state()
    while state!=3:  # lifecycle PRIMARY_STATE_ACTIVE
        remaining()
        if state in (1,2):
            transition=1 if state==1 else 3  # CONFIGURE / ACTIVATE
            if not change_state(transition,remaining()):
                raise RuntimeError('Map-server lifecycle transition failed; inspect its first error. Nav2 was not started.')
        elif state in (10,13):  # configuring / activating
            pump()
        else:
            raise RuntimeError(f'Unexpected map-server lifecycle state {state}; restart this launch')
        state=get_state()
    while not received():
        remaining();pump()
    remaining()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map-yaml',required=True)
    parser.add_argument('--startup-timeout',type=float,default=300.)
    args=parser.parse_args()
    if not math.isfinite(args.startup_timeout) or args.startup_timeout<=0:
        parser.error('startup-timeout must be positive')
    expected=expected_map(args.map_yaml)
    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.signals import SignalHandlerOptions
    from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy
    from lifecycle_msgs.srv import GetState,ChangeState
    from nav_msgs.msg import OccupancyGrid
    rclpy.init(args=[],signal_handler_options=SignalHandlerOptions.NO)
    node=Node('course_map_startup',parameter_overrides=[Parameter('use_sim_time',value=True)])
    status={'received':False,'error':None}
    def on_map(message):
        try:
            check_map(message,expected);status['received']=True
        except ValueError as exc:status['error']=str(exc)
    qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,
                   reliability=ReliabilityPolicy.RELIABLE)
    subscription=node.create_subscription(OccupancyGrid,'/map',on_map,qos)
    state_client=node.create_client(GetState,'/map_server/get_state')
    change_client=node.create_client(ChangeState,'/map_server/change_state')
    def pump():
        rclpy.spin_once(node,timeout_sec=.1)
        if status['error']:raise ValueError(status['error'])
        if node.get_node_names().count('map_server')>1:
            raise RuntimeError('Duplicate map_server nodes; stop the other navigation launch')
    def rpc(client,request,timeout):
        future=client.call_async(request)
        end=time.monotonic()+timeout
        while not future.done() and time.monotonic()<end:pump()
        if not future.done():
            future.cancel()
            raise TimeoutError('Map-server lifecycle request timed out; Nav2 startup remains blocked')
        result=future.result()
        if result is None:raise RuntimeError('Map-server lifecycle service returned no response')
        return result
    def get_state():return rpc(state_client,GetState.Request(),10.).current_state.id
    def change_state(transition,timeout):
        label='CONFIGURE (large map loading)' if transition==1 else 'ACTIVATE'
        print(f'Campus map: {label}; waiting for completion before Nav2.',flush=True)
        request=ChangeState.Request();request.transition.id=transition
        return rpc(change_client,request,min(240.,timeout)).success
    try:
        deadline=time.monotonic()+args.startup_timeout
        print('Campus map: waiting for map_server; Nav2 has not started.',flush=True)
        for client in [state_client,change_client]:
            while not client.wait_for_service(timeout_sec=.2):
                pump()
                if time.monotonic()>deadline:raise TimeoutError('map_server services unavailable; Nav2 was not started')
        activate_and_wait(get_state,change_state,lambda:status['received'],pump,deadline)
        pump()
        if get_state()!=3:raise RuntimeError('map_server is no longer active')
        print(f"CAMPUS_MAP_READY: active map_server and validated /map {expected['width']} x {expected['height']} at {expected['resolution']} m/cell.",flush=True)
        # Keep supervising lifecycle/data. A failure exits this process; the
        # launch then stops Nav2 and the GPS command gate together.
        next_check=time.monotonic()+2.
        while rclpy.ok():
            pump()
            if time.monotonic()>=next_check:
                if get_state()!=3:raise RuntimeError('map_server left active state; stopping GPS navigation')
                next_check=time.monotonic()+2.
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__=='__main__':main()
