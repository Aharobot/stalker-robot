from lidar import LIDARBuffer
from scipy.optimize import minimize_scalar

def rpm_error(rpm: float, lidar_buffer: LIDARBuffer) -> float:
    # return the normalized square error between the
    # measured values across two rotations
    lidar_buffer.set_rpm(rpm)
    lidar_buffer.reset()
    rot1 = list(zip(*lidar_buffer.next_rot()))[1]
    rot2 = list(zip(*lidar_buffer.next_rot()))[1]
    error = sum([(d[0] - d[1]) ** 2 for d in zip(rot1, rot2)])
    return error / min(len(rot1), len(rot2))


def optimize_RPM(lidar_buffer: LIDARBuffer) -> float:
    res = minimize_scalar(rpm_error, args=(lidar_buffer,))
    return res.x