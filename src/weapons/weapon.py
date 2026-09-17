class Weapon:
    def __init__(self, fire_rate, magazine_size=12, reload_time=1.2):
        self.fire_rate = fire_rate
        self.cooldown = 0

        self.magazine_size = magazine_size
        self.ammo = magazine_size

        self.reload_time = reload_time
        self.reload_timer = 0.0
        self.reloading = False

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt

        if self.reloading:
            self.reload_timer -= dt

            if self.reload_timer <= 0:
                self.ammo = self.magazine_size
                self.reloading = False

    def can_fire(self):
        return (
            self.cooldown <= 0
            and self.ammo > 0
            and not self.reloading
        )

    def fire(self):
        if not self.can_fire():
            return False

        self.cooldown = self.fire_rate
        self.ammo -= 1

        if self.ammo <= 0:
            self.reload()

        return True

    def reload(self):
        if self.reloading:
            return

        if self.ammo >= self.magazine_size:
            return

        self.reloading = True
        self.reload_timer = self.reload_time