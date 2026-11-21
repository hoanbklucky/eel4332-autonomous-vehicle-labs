"""Measured four-wheel skid-steer odometry; no ROS, commands, GPS or truth."""
import math
import xml.etree.ElementTree as ET

WHEELS = ('front_left_wheel_joint', 'front_right_wheel_joint',
          'rear_left_wheel_joint', 'rear_right_wheel_joint')


def model_geometry(description):
    try:
        root = ET.fromstring(description)
    except ET.ParseError as exc:
        raise ValueError('Invalid expanded robot description') from exc
    radii, lateral = [], []
    for name in WHEELS:
        joint = root.find(f"joint[@name='{name}']")
        if joint is None or joint.find('axis') is None:
            raise ValueError(f'Missing wheel joint/axis: {name}')
        axis = [float(v) for v in joint.find('axis').get('xyz', '').split()]
        if len(axis) != 3 or not all(map(math.isfinite, axis)) or any(abs(a-b) > 1e-8 for a, b in zip(axis, [0, 1, 0])):
            raise ValueError('Wheel odometry supports the supplied +y wheel axes only')
        parent = joint.find('parent')
        if parent is not None and parent.get('link') != 'base_link':
            raise ValueError('Wheel joints must attach directly to base_link')
        link = joint.find('child')
        cylinder = None if link is None else root.find(
            f"link[@name='{link.get('link')}']/collision/geometry/cylinder")
        if cylinder is None:
            raise ValueError('Wheel collision must be a cylinder')
        radius = float(cylinder.get('radius'))
        if not math.isfinite(radius) or not .005 <= radius <= .2:
            raise ValueError('Invalid wheel radius')
        radii.append(radius)
        origin = joint.find('origin')
        if origin is None:
            lateral.append(None)
        else:
            xyz = [float(v) for v in origin.get('xyz', '').split()]
            rpy = [float(v) for v in origin.get('rpy', '0 0 0').split()]
            if (len(xyz) != 3 or len(rpy) != 3 or not all(map(math.isfinite, xyz+rpy))
                    or any(abs(v) > 1e-8 for v in rpy)):
                raise ValueError('Wheel joint origins must be finite and aligned with base_link')
            lateral.append(xyz[1])
    return radii, lateral


def wheel_geometry(description):
    """Radii-only interface shared by the optional offline encoder activity."""
    return model_geometry(description)[0]


def track_width(description):
    _, y = model_geometry(description)
    if any(v is None for v in y):
        raise ValueError('Wheel odometry requires wheel joint origin positions')
    left, right = (y[0]+y[2])/2, (y[1]+y[3])/2
    if (left <= right or abs(y[0]-y[2]) > .005 or abs(y[1]-y[3]) > .005
            or not .03 <= left-right <= 1):
        raise ValueError('Invalid left/right wheel track geometry')
    return left-right


def wheel_twist(names, velocities, radii, track):
    """Wheel angular rates [rad/s] -> base forward/yaw velocity [m/s, rad/s]."""
    if len(radii) != 4 or not math.isfinite(track) or track <= 0:
        raise ValueError('Expected four wheel radii and a positive track width')
    speeds = []
    for name, radius in zip(WHEELS, radii):
        if names.count(name) != 1:
            raise ValueError(f'/joint_states is missing or duplicates {name}')
        i = names.index(name)
        if i >= len(velocities) or not math.isfinite(velocities[i]):
            raise ValueError('Wheel joint velocities are missing/non-finite; no command fallback')
        speeds.append(float(velocities[i]) * radius)
    if max(map(abs, speeds)) > 3:
        raise ValueError('Implausible wheel speed; inspect wheel units and model')
    left, right = (speeds[0]+speeds[2])/2, (speeds[1]+speeds[3])/2
    return (left+right)/2, (right-left)/track


def wheel_speed(names, velocities, radii):
    # Forward velocity does not depend on the track width.
    return wheel_twist(names, velocities, radii, 1.)[0]


class WheelOdometry:
    """Integrate measured twist for diagnostics; publish no TF or pseudo-lateral speed."""
    def __init__(self):
        self.pose = [0., 0., 0.]
        self.previous_t = None
        self.previous_twist = None
        self.variance = [1e-6, 1e-6, 1e-6]

    def update(self, stamp, velocity, yaw_rate):
        if not all(map(math.isfinite, [stamp, velocity, yaw_rate])):
            raise ValueError('Non-finite wheel odometry measurement')
        if self.previous_t is not None:
            dt = stamp-self.previous_t
            if dt == 0:
                return False
            if dt < 0 or dt > .5:
                raise ValueError('Wheel clock reset/gap; restart the complete simulation')
            v = (self.previous_twist[0]+velocity)/2
            omega = (self.previous_twist[1]+yaw_rate)/2
            angle = omega*dt
            distance = v*dt
            sinc = 1. if abs(angle) < 1e-9 else math.sin(angle/2)/(angle/2)
            self.pose[0] += distance*sinc*math.cos(self.pose[2]+angle/2)
            self.pose[1] += distance*sinc*math.sin(self.pose[2]+angle/2)
            self.pose[2] = math.atan2(math.sin(self.pose[2]+angle), math.cos(self.pose[2]+angle))
            # Conservative teaching-model random-walk uncertainty, not hardware
            # calibration. Raw pose is diagnostic; the EKF fuses forward speed only.
            self.variance[0] += .0025*dt + .01*abs(distance)
            self.variance[1] += .0025*dt + .01*abs(distance)
            self.variance[2] += .01*dt + .02*abs(angle)
        self.previous_t, self.previous_twist = stamp, (velocity, yaw_rate)
        return True
