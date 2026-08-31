import pygame
class Spinner:

    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.angle = 0

    def update(self, dt):
        self.angle += 180 * dt

    def draw(self, screen, camera):
        center = self.position - camera.offset
        length = 30
        end = pygame.Vector2(length, 0).rotate(self.angle)
        pygame.draw.circle(screen, (0, 200, 255), center, 5)
        pygame.draw.line(screen, (0, 200, 255), center, center + end, 4)