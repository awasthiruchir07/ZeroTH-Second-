import pygame
class InputManager:
    def get_movement(self):
        movement = pygame.Vector2()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_d]:
            movement.x += 1
        if movement.length_squared() > 0:
            movement = movement.normalize()
        return movement

    def is_moving(self):
        return self.get_movement().length_squared() > 0

    def get_mouse_position(self):
        return pygame.Vector2(pygame.mouse.get_pos())

    def is_shooting(self):
        return pygame.mouse.get_pressed()[0]