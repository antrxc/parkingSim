# Live metrics for parking lot
class Metrics:
    def __init__(self):
        self.parked = 0
        self.failed = 0
        self.wait_times = []
        self.rewards = 0

    def record_park(self, wait_time):
        self.parked += 1
        self.wait_times.append(wait_time)
        self.rewards += 1

    def record_fail(self):
        self.failed += 1
        self.rewards -= 1

    def avg_wait(self):
        return sum(self.wait_times)/len(self.wait_times) if self.wait_times else 0
