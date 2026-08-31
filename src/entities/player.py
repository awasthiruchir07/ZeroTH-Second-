import pygame 
from src.entities.entity import Entity
from src.world.world import World
from src.engine.settings import PLAYER_SIZE, PLAYER_SPEED
from src.weapons.weapon_manager import WeaponManager

class Player(Entity):
    def __init__(self, position):
        super().__init__(position.x, position.y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.rotation = 0
        self.weapon = WeaponManager()
        self.health = 100
        self.max_health = 100
        self.dead = False
        self.damage_flash = 0.0
        self.color = (255, 255, 255)
        self.muzzle_flash = 0.0

    def take_damage(self, amount):

        if self.dead:
            return
        self.health -= amount
        self.damage_flash = 0.12
        if self.health <= 0:
            self.health = 0
            self.dead = True
            
    def set_rotation(self, angle):
        self.rotation = angle

    def update(self, dt, movement, world):
        if self.damage_flash > 0:
            self.damage_flash -= dt
        if self.dead:
            return
        if movement.length_squared() > 0 :
            movement = movement.normalize()
        new_x = self.position.x + movement.x * self.speed * dt
        x_rect = pygame.Rect(new_x, self.position.y, self.width, self.height)
        if not world.is_rect_colliding(x_rect):
            self.position.x = new_x
        new_y = self.position.y + movement.y * self.speed * dt
        y_rect = pygame.Rect(self.position.x, new_y, self.width, self.height)
        if not world.is_rect_colliding(y_rect):
            self.position.y = new_y
        if self.muzzle_flash > 0:
            self.muzzle_flash -= dt
        self.weapon.update(dt)

    def draw(self, screen, camera):
        if self.damage_flash > 0:
            color = (255, 80, 80)
        else:
            color = self.color
        rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(screen, color, screen_rect)
        center = pygame.Vector2(camera.apply(self.rect).center)
        end = center + self.aim_direction * 30
        pygame.draw.line(screen, (0, 255, 255), center, end, 3)
        if self.muzzle_flash > 0:
            center = pygame.Vector2(
                camera.apply(self.rect).center
            )
            flash_position = (
                center +
                self.aim_direction * 25
            )
            pygame.draw.circle(
                screen,
                (255, 220, 80),
                flash_position,
                7
            )
        

    @property
    def hitbox(self):
        padding = 6
        return pygame.Rect(self.position.x + padding, self.position.y + padding, self.width - padding * 2, self.height - padding * 2)
