import pygame
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2()

    def update(self, target, screen_width, screen_height):
        # Center the PLAYER, not its top-left corner
        self.offset.x = target.position.x + target.width / 2 - screen_width / 2
        self.offset.y = target.position.y + target.height / 2 - screen_height / 2

    def apply(self, rect):
        return pygame.Rect(
            rect.x - self.offset.x,
            rect.y - self.offset.y,
            rect.width,
            rect.height,
        )