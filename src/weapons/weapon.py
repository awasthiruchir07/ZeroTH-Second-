class Weapon:
    def __init__(self, fire_rate):
        self.fire_rate = 0.25
        self.cooldown = 0

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt

    def can_fire(self):
        return self.cooldown <= 0

    def fire(self):
        self.cooldown = self.fire_rate