"""Idealized GNSS noise profiles; no RTK correction links/fix states modeled."""
import copy
import math
import xml.etree.ElementTree as ET

PROFILES = {
    'ordinary': {'horizontal_std_deg': 0.000015, 'vertical_std_m': 3.0},
    'rtk': {'horizontal_std_deg': 0.0000002, 'vertical_std_m': 0.03},
}


def apply_profile(description, profile):
    if profile == 'model':
        return description
    if profile not in ('ordinary', 'rtk', 'comparison'):
        raise ValueError(f'Unknown GPS profile: {profile}')
    root = ET.fromstring(description)
    matches = [(parent, s) for parent in root.findall('gazebo')
               for s in parent.findall("sensor[@name='gps_sensor']")]
    if len(matches) != 1 or matches[0][1].get('type') != 'navsat':
        raise ValueError('Expected one supplied gps_sensor of type navsat')
    if root.findall(".//sensor[@name='rtk_sensor']"):
        raise ValueError('Custom rtk_sensor exists; reconcile rather than duplicating it')
    parent, sensor = matches[0]
    if sensor.findtext('gz_frame_id') != 'gps_link':
        raise ValueError('Expected centered gps_link sensor frame')

    def set_noise(element, name):
        settings = PROFILES[name]
        for axis, value in [('horizontal', settings['horizontal_std_deg']),
                            ('vertical', settings['vertical_std_m'])]:
            noise = element.find(f'navsat/position_sensing/{axis}/noise')
            if noise is None or noise.get('type') != 'gaussian':
                raise ValueError('Expected supplied Gaussian GPS position noise')
            for field, text in [('mean', '0.0'), ('stddev', str(value))]:
                child = noise.find(field)
                if child is None:
                    raise ValueError('Incomplete GPS noise declaration')
                child.text = text
        element.find('update_rate').text = '5.0'

    set_noise(sensor, 'ordinary' if profile == 'comparison' else profile)
    if profile == 'comparison':
        extra = copy.deepcopy(sensor)
        extra.set('name', 'rtk_sensor')
        extra.find('topic').text = 'gps/rtk_fix'
        set_noise(extra, 'rtk')
        parent.append(extra)
    return ET.tostring(root, encoding='unicode')


def validate_profile(description, profile, sensor_name='gps_sensor'):
    root = ET.fromstring(description)
    sensors = root.findall(f".//sensor[@name='{sensor_name}']")
    if len(sensors) != 1:
        raise ValueError(f'Expected exactly one {sensor_name}; check world gps_profile')
    sensor = sensors[0]
    for axis, key in [('horizontal', 'horizontal_std_deg'), ('vertical', 'vertical_std_m')]:
        value = float(sensor.findtext(f'navsat/position_sensing/{axis}/noise/stddev'))
        if not math.isclose(value, PROFILES[profile][key], rel_tol=1e-6, abs_tol=1e-12):
            raise ValueError(f'{sensor_name} noise does not match {profile} profile; '
                             'restart world with the matching gps_profile argument')
    expected_topic = 'gps/rtk_fix' if sensor_name == 'rtk_sensor' else 'gps/fix'
    if sensor.findtext('topic', '').strip('/') != expected_topic:
        raise ValueError(f'Unexpected {sensor_name} topic')
