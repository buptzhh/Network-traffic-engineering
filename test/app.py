class App:
    def __init__(self, type, latency, jitter, lost):
        self.type = type
        self.latency = latency
        self.jitter = jitter
        self.lost = lost
