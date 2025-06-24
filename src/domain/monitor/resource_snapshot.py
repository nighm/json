class ResourceSnapshot:
    def __init__(self, timestamp, cpu=None, memory=None, disk=None):
        self.timestamp = timestamp
        self.cpu = cpu
        self.memory = memory
        self.disk = disk 