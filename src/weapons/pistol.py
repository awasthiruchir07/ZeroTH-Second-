from src.weapons.weapon import Weapon

class Pistol(Weapon):
    def __init__(self):
        super().__init__(
            fire_rate=0.25,
            magazine_size=12,
            reload_time=1.2
        )