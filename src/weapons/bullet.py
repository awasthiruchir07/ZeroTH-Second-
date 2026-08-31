import pygame
from src.entities.entity import Entity
class Bullet(Entity):
    SPEED = 900
    LIFE_TIME = 2.0
    SIZE = 8

    def __init__(self, position, direction, owner):
        super().__init__( position.x, position.y, self.SIZE, self.SIZE)
        self.velocity = direction.normalize() * self.SPEED
        self.life = self.LIFE_TIME
        self.damage = 25
        self.dead = False
        self.owner = owner

    def update(self, dt, world):
        self.position += self.velocity * dt
        self.life -= dt
        if self.life <= 0:
            self.dead = True
        if world.is_rect_colliding(self.hitbox):
            self.dead = True

    def draw(self, screen, camera):
        pygame.draw.circle(screen, (255,255,0), camera.apply(self.rect).center, self.SIZE//2)