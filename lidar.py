import collections
import threading
import time
from typing import Tuple, List

import serial


class LIDARBuffer(threading.Thread):
    def __init__(self, rpm: float, lidar: serial.Serial):
        self.data = collections.deque()
        self.ended = False
        self.serial = lidar
        self.set_rpm(rpm)

        super(LIDARBuffer, self).__init__()

    def __bool__(self) -> bool:
        # True if data in buffer, false otherwise
        return bool(self.data)

    def __len__(self) -> int:
        # Elements in the buffer
        return len(self.data)

    def run(self):
        # Continuously poll the LIDAR, pushing data to the queue
        while (True):
            if self.ended:
                break

            if self.serial.in_waiting >= 9:
                # Nine bytes are transmitted for every piece of data
                # First two bytes are the identifying header ('YY')
                # Next two are the low and high byte of the distance
                # Last five are ignored for our purposes (see datasheet)
                if b'Y' == self.serial.read() and b'Y' == self.serial.read():
                    angle = (time.time() % self.rot_time) * 360 / self.rot_time
                    distance = ord(self.serial.read()) + \
                               ord(self.serial.read()) << 8
                    for i in range(5):
                        self.serial.read()
                    self.data.append((distance, angle))

    def set_rpm(self, rpm: float):
        # Sets the current rpm that the motor is believed to be running at
        self.rot_time = 60 / rpm

    def pop(self, wait: bool = False) -> Tuple[float, float]:
        # Return the next data element (oldest in buffer)
        # If wait is true, will wait for the next available data
        if wait:
            self.wait()
        try:
            return self.data.popleft()
        except IndexError:
            raise IndexError('pop from an empty buffer')

    def next_rot(self, wait: bool = True) -> List[Tuple[float, float]]:
        # Return the next data corresponding to a full rotation
        # If wait is true, will wait for the next available data
        reading = self.pop(wait)
        start_angle = reading[1]
        last_angle = 0
        data = []
        # Iterate through data until angle exceeds limit
        while (reading[1] - start_angle) % 360 > last_angle - 1e-3:
            last_angle = (reading[1] - start_angle) % 360
            data.append(reading)
            reading = self.pop(wait)
        self.data.appendleft(reading)
        return data

    def wait(self):
        # Wait until the next data is available
        while not self:
            time.sleep(0.01)

    def popall(self) -> List[Tuple[float, float]]:
        # Return all current data, ordered oldest to newest
        data = list(self.data)
        self.reset()
        return data

    def reset(self):
        # Removes all existing data in the queue
        self.data = collections.deque()

    def end(self):
        # Ends the continuous polling of the sensor
        self.ended = True


def initialize_lidar() -> serial.Serial:
    # Initialize the serial connection to the LIDAR
    lidar = serial.Serial('/dev/serial0', 115200, timeout=1)
    lidar.write(bytes(b'B'))
    lidar.write(bytes(b'W'))
    lidar.write(bytes(2))
    lidar.write(bytes(0))
    lidar.write(bytes(0))
    lidar.write(bytes(0))
    lidar.write(bytes(1))
    lidar.write(bytes(6))
    return lidar


if __name__ == '__main__':
    lidar = initialize_lidar()
    lidar_buffer = LIDARBuffer(100, lidar)
    lidar_buffer.start()
