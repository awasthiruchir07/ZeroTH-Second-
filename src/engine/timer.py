class TimeEngine:

    def __init__(self):
        self.scale = 0.0

    def update(self, moving):
        if moving:
            self.scale = 1.0
        else:
            self.scale = 0.0

    def delta(self, dt):
        return dt * self.scale