import pygame
class Entity:
    def __init__(self, x, y, width, height):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2()
        self.width = width
        self.height = height

    @property
    def rect(self):
        return pygame.Rect(
            self.position.x,
            self.position.y,
            self.width,
            self.height
        )

    @property
    def hitbox(self):
        padding = 6
        return pygame.Rect(
            self.position.x + padding,
            self.position.y + padding,
            self.width - padding * 2,
            self.height - padding * 2
        )