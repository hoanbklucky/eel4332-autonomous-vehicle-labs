import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from map_startup import activate_and_wait, check_map

class MapStartupTests(unittest.TestCase):
    def test_lifecycle_and_data_both_required(self):
        state=[1]; received=[False]; transitions=[]
        def change(value, timeout):
            transitions.append(value); state[0]=2 if value==1 else 3
            return True
        def pump(): received[0]=True
        activate_and_wait(lambda:state[0],change,lambda:received[0],pump,time.monotonic()+5)
        self.assertEqual(transitions,[1,3])
        self.assertTrue(received[0])

    def test_inactive_activates_only(self):
        state=[2]; transitions=[]
        def change(value, timeout):
            transitions.append(value);state[0]=3;return True
        activate_and_wait(lambda:state[0],change,lambda:True,lambda:None,time.monotonic()+5)
        self.assertEqual(transitions,[3])

    def test_no_retained_map_times_out(self):
        clock=[0.]
        def pump():clock[0]+=1
        with self.assertRaises(TimeoutError):
            activate_and_wait(lambda:3,lambda *_:True,lambda:False,pump,3,lambda:clock[0])

    def test_transition_failure_blocks_navigation(self):
        with self.assertRaises(RuntimeError):
            activate_and_wait(lambda:2,lambda *_:False,lambda:True,lambda:None,time.monotonic()+5)

    def test_geometry_validation(self):
        expected=dict(width=2,height=2,resolution=.25,origin=[-500,-733.5,0])
        pose=NS(position=NS(x=-500,y=-733.5,z=0),orientation=NS(x=0,y=0,z=0,w=1))
        message=NS(header=NS(frame_id='map'),info=NS(width=2,height=2,resolution=.25,origin=pose),data=[0]*4)
        check_map(message,expected)
        message.info.width=20
        with self.assertRaises(ValueError):check_map(message,expected)
        message.info.width=2;message.header.frame_id='odom'
        with self.assertRaises(ValueError):check_map(message,expected)
