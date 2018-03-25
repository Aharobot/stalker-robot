import collections
import threading
import time


class TimerThread(threading.Thread):
    def __init__(self):
        self.time = collections.deque()
        self.ended = False
        self.offset = time.time()
        super(TimerThread, self).__init__()

    def run(self):
        while (True):
            if self.ended:
                break
            self.time.appendleft((time.time() - self.offset) % 10)
            time.sleep(0.1)

    def end(self):
        self.ended = True


if __name__ == '__main__':
    time_thread = TimerThread()
    time_thread.start()
    time_thread.offset = time.time()
    print('Initial Offset = {:f}'.format(time_thread.offset))
    for i in range(1, 11):
        time.sleep(0.1 * i)
        times = []
        while time_thread.time:
            times.append(time_thread.time.pop())
        times = ', '.join(['{:.3f}'.format(t) for t in times])
        print('Current Times =', times)
    time_thread.end()
