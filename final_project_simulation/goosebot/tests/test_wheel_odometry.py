"""Measured-wheel math and course wiring, runnable without ROS/Gazebo."""
import ast
import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import yaml

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from wheel_odometry_core import WHEELS, wheel_geometry, track_width, wheel_twist, WheelOdometry


def description():
    return '<robot>'+''.join(
        f'<joint name="{name}"><parent link="base_link"/><child link="w{i}"/>'
        f'<axis xyz="0 1 0"/><origin xyz="0 {(.085 if i%2==0 else -.085)} 0"/></joint>'
        f'<link name="w{i}"><collision><geometry><cylinder radius=".03"/></geometry></collision></link>'
        for i,name in enumerate(WHEELS))+'</robot>'


class WheelTests(unittest.TestCase):
    def test_world_launch_constructs_wheel_process_and_stops_on_exit(self):
        class Action:
            def __init__(self,*args,**kwargs): self.args,self.kwargs=args,kwargs
        class Configuration:
            def __init__(self,name): self.name=name
            def perform(self,context): return context[self.name]
        exports={
            'xacro':{'process_file':lambda _:types.SimpleNamespace(toxml=lambda:'<robot/>')},
            'ament_index_python.packages':{'get_package_share_directory':lambda _:'/installed'},
            'launch':{'LaunchDescription':Action},
            'launch.actions':{n:Action for n in ['AppendEnvironmentVariable','DeclareLaunchArgument','EmitEvent','ExecuteProcess','LogInfo','OpaqueFunction','RegisterEventHandler','TimerAction']},
            'launch.event_handlers':{'OnProcessExit':Action},'launch.events':{'Shutdown':Action},
            'launch.substitutions':{'LaunchConfiguration':Configuration},'launch_ros.actions':{'Node':Action},
            'launch_ros.parameter_descriptions':{'ParameterValue':Action},
            'gps_profiles':{'apply_profile':lambda s,p:s}}
        modules={}
        for name,attrs in exports.items():
            m=types.ModuleType(name);m.__dict__.update(attrs);modules[name]=m
        with tempfile.TemporaryDirectory() as temp,patch.dict(sys.modules,modules):
            world=Path(temp)/'world.sdf';world.write_text('<sdf><world name="test"/></sdf>')
            (Path(temp)/'mission.json').write_text('{"stops":[{"xy":[0,0],"yaw":0}]}')
            spec=importlib.util.spec_from_file_location('wheel_launch_test',HERE/'world.launch.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.existing_servers=lambda:[]
            actions=module.start({'world':str(world),'gps_profile':'comparison'})
            ekf=next(a for a in actions if a.kwargs.get('executable')=='ekf_node')
            self.assertEqual(ekf.kwargs['parameters'][0],str(HERE/'ekf_wheel.yaml'))
            wheel=next(a for a in actions if a.kwargs.get('cmd',[None])[-1:]==[str(HERE/'wheel_joint_odometry.py')])
            handlers=[a.args[0] for a in actions if a.args and isinstance(a.args[0],Action) and a.args[0].kwargs.get('target_action') is wheel]
            self.assertEqual(len(handlers),1)
            self.assertEqual(len(handlers[0].kwargs['on_exit'](None,None)),2)

    def test_geometry_and_reordered_measurements(self):
        d=description()
        self.assertAlmostEqual(track_width(d), .17)
        names=list(reversed(WHEELS))
        v,w=wheel_twist(names,[10]*4,wheel_geometry(d),track_width(d))
        self.assertAlmostEqual(v,.3)
        self.assertAlmostEqual(w,0)

    def test_rotation_and_reverse(self):
        v,w=wheel_twist(list(WHEELS),[-1,1,-1,1],[.03]*4,.17)
        self.assertEqual(v,0)
        self.assertAlmostEqual(w,.06/.17)
        v,w=wheel_twist(list(WHEELS),[-10]*4,[.03]*4,.17)
        self.assertAlmostEqual(v,-.3)
        self.assertEqual(w,0)

    def test_missing_and_nonfinite_are_not_commands(self):
        for rates in ([], [1,1,1], [1,float('nan'),1,1]):
            with self.assertRaises(ValueError):
                wheel_twist(list(WHEELS),rates,[.03]*4,.17)
        with self.assertRaises(ValueError):
            wheel_twist([WHEELS[0]]*4,[1]*4,[.03]*4,.17)
        self.assertEqual(wheel_twist(list(WHEELS),[0]*4,[.03]*4,.17),(0,0))

    def test_geometry_failures(self):
        for d in (description().replace('0 1 0','1 0 0'),description().replace('radius=".03"','radius="nan"'),description().replace('.085','0')):
            with self.assertRaises(ValueError):
                track_width(d)

    def test_arc_integration_and_stop(self):
        o=WheelOdometry()
        for i in range(11): o.update(i*.1,1,1)
        self.assertAlmostEqual(o.pose[0],math.sin(1))
        self.assertAlmostEqual(o.pose[1],1-math.cos(1))
        self.assertAlmostEqual(o.pose[2],1)
        self.assertFalse(o.update(1,99,99))
        with self.assertRaises(ValueError): o.update(.9,0,0)
        with self.assertRaises(ValueError): o.update(2,0,0)

    def test_forward_speed_only_and_one_tf_owner(self):
        p=yaml.safe_load((HERE/'ekf_wheel.yaml').read_text())['ekf_filter_node']['ros__parameters']
        self.assertEqual(p['odom0'],'/wheel/odometry')
        self.assertEqual([i for i,v in enumerate(p['odom0_config']) if v],[6])
        self.assertEqual([i for i,v in enumerate(p['imu0_config']) if v],[11])
        self.assertTrue(p['publish_tf'])
        self.assertEqual(p['world_frame'],'odom')
        source=(HERE/'wheel_joint_odometry.py').read_text()
        tree=ast.parse(source)
        subs=[n.args[1].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='create_subscription']
        self.assertCountEqual(subs,['/joint_states','/robot_description'])
        self.assertNotIn('TransformBroadcaster',source)
        launch=(HERE/'world.launch.py').read_text()
        self.assertNotIn("executable='cmd_vel_to_odom.py'",launch)
        self.assertIn("str(here / 'ekf_wheel.yaml')",launch)
        self.assertIn('target_action=wheel_odom',launch)
        ast.parse(launch)

if __name__=='__main__': unittest.main()
