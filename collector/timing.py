from time import time, sleep

class Timing(object):
    
    def __init__(self, time_window):
        self.time_window = time_window
        self.start = 0
        self.now = 0
    
    def new_window(self):
        self.start = time()
        
    def wait_nextwindow(self):
        self.now = time()
        if self.now - self.start < self.time_window:
            sleep(self.time_window - (self.now - self.start) + 1)
        self.start = time()
        