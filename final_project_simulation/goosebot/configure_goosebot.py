#!/usr/bin/env python3
"""Install the supplied course sensor defaults without replacing custom models.

Adds only missing LiDAR/joint-state blocks and bridges. Existing complete LiDAR
settings are retained; incomplete/conflicting edits stop before either write.
"""
import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml


def prepare(package):
    model = package / 'urdf/robot.urdf.xacro'
    bridge = package / 'config/ros_gz_bridge.yaml'
    text = model.read_text()
    root = ET.fromstring(text)
    if root.tag != 'robot':
        raise ValueError('Expected a robot root element')
    for tag in ('link', 'joint'):
        names = [e.get('name') for e in root.findall(tag)]
        if len(names) != len(set(names)):
            raise ValueError(f'Duplicate {tag} names; preserve/fix your edits first')
    links = root.findall("link[@name='lidar_link']")
    sensors = root.findall("gazebo[@reference='lidar_link']/sensor")
    joints = root.findall("joint[@name='lidar_joint']")
    additions = []
    if not links and not sensors and not joints:
        if 'lidar_link' in text or 'lidar_sensor' in text or 'lidar_x_offset' in text:
            raise ValueError('Partial LiDAR edits found; complete or reconcile them before setup')
        template = Path(__file__).with_name('provided_lidar.xml').read_text()
        ET.fromstring('<robot xmlns:xacro="http://www.ros.org/wiki/xacro">' + template + '</robot>')
        additions.append(template)
    else:
        if len(links) != 1 or len(joints) != 1 or len(sensors) != 1:
            raise ValueError('Incomplete LiDAR; expected one lidar_link, lidar_joint and sensor')
        s, j = sensors[0], joints[0]
        if (s.get('type') != 'gpu_lidar' or s.findtext('topic', '').strip('/') != 'scan'
                or s.findtext('gz_frame_id') != 'lidar_link'
                or j.get('type') != 'fixed'
                or j.find('parent').get('link') != 'base_link'
                or j.find('child').get('link') != 'lidar_link'):
            raise ValueError('Custom LiDAR uses different interfaces; reconcile manually, not overwritten')
        print('Keeping existing LiDAR mount and scan settings.')
    plugins = root.findall('.//plugin')
    joint_plugins = [p for p in plugins if 'joint-state-publisher' in p.get('filename', '')
                     or p.get('name', '').endswith('::JointStatePublisher')]
    if joint_plugins:
        if len(joint_plugins) != 1 or joint_plugins[0].findtext('topic', '').strip('/') != 'joint_states':
            raise ValueError('Existing joint publisher topic differs; reconcile manually')
    else:
        additions.append('''<gazebo>
  <plugin filename="gz-sim-joint-state-publisher-system"
          name="gz::sim::systems::JointStatePublisher">
    <topic>joint_states</topic>
    <joint_name>front_left_wheel_joint</joint_name>
    <joint_name>front_right_wheel_joint</joint_name>
    <joint_name>rear_left_wheel_joint</joint_name>
    <joint_name>rear_right_wheel_joint</joint_name>
  </plugin>
</gazebo>''')
    bridge_text = bridge.read_text()
    entries = yaml.safe_load(bridge_text)
    if not isinstance(entries, list):
        raise ValueError('Bridge config must be a YAML list')
    for topic, ros_type, gz_type in [('scan', 'sensor_msgs/msg/LaserScan', 'gz.msgs.LaserScan'),
                                      ('joint_states', 'sensor_msgs/msg/JointState', 'gz.msgs.Model')]:
        matches = [e for e in entries if str(e.get('ros_topic_name', '')).strip('/') == topic]
        expected = dict(ros_topic_name='/' + topic, gz_topic_name='/' + topic,
                        ros_type_name=ros_type, gz_type_name=gz_type, direction='GZ_TO_ROS')
        if matches:
            if len(matches) != 1 or any(str(matches[0].get(k, '')).strip('/') != str(v).strip('/')
                                       for k, v in expected.items()):
                raise ValueError(f'Existing {topic} bridge conflicts; reconcile manually')
        else:
            bridge_text += '\n# Supplied course baseline\n' + yaml.safe_dump([expected], sort_keys=False)
    if additions:
        text, count = re.subn(r'</robot>\s*$', lambda _: '\n'.join(additions) + '\n</robot>\n', text)
        if count != 1:
            raise ValueError('Expected one final closing robot tag')
    ET.fromstring(text)
    yaml.safe_load(bridge_text)
    # All validation precedes writes; retain the original formatting/comments.
    if text != model.read_text():
        model.write_text(text)
    if bridge_text != bridge.read_text():
        bridge.write_text(bridge_text)
    print('Course baseline ready: LiDAR /scan and wheel joint-state publisher/bridge.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    try:
        prepare(args.package.resolve())
    except (ValueError, OSError, ET.ParseError, yaml.YAMLError) as error:
        parser.exit(1, f'Configuration stopped: {error}\nNo custom settings were replaced.\n')
