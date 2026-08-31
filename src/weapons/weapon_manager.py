from src.weapons.pistol import Pistol
class WeaponManager:
    def __init__(self):
        self.weapon = Pistol()

    def update(self, dt):
        self.weapon.update(dt)

    def can_fire(self):
        return self.weapon.can_fire()

    def fire(self):
        self.weapon.fire()