import pygame
from src.entities.entity import Entity
class Drone(Entity):
    PATROL = "PATROL"
    CHASE = "CHASE"
    ATTACK = "ATTACK"
    SEARCH = "SEARCH"

    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.start_x = x
        self.distance = 120
        self.speed = 120
        self.direction = 1
        self.health = 100
        self.dead = False
        self.death_timer = 0.0
        self.state = self.PATROL
        self.detection_range = 400
        self.attack_range = 210
        self.chase_speed = 150
        self.search_timer = 0.0
        self.search_duration = 3.0
        self.path = []
        self.path_index = 0
        self.path_timer = 0.0
        self.velocity = pygame.Vector2()
        self.attack_cooldown = 0.0
        self.attack_delay = 0.35
        self.attack_damage = 10
        self.damage_flash = 0.0
        self.color = (100, 100, 255)
        self.explosion_timer = 0.0
        self.preferred_attack_distance = 170
        self.strafe_direction = 1
        self.strafe_speed = 45
        self.strafe_timer = 0.0
        self.strafe_change_time = 1.5
        self.strafe_direction = 1
        self.strafe_speed = 45
        self.strafe_timer = 0.0
        self.strafe_change_time = 1.5
        self.aim_direction = pygame.Vector2(1, 0)

    def take_damage(self, amount):
        if self.dead:
            return
        self.health -= amount
        self.damage_flash = 0.12
        if self.health <= 0:
            self.health = 0
            self.dead = True
            self.death_timer = 2.0
            self.explosion_timer = 0.35

    def update(self, dt, player, world):
        if self.damage_flash > 0:
            self.damage_flash -= dt
        if self.explosion_timer > 0:
            self.explosion_timer -= dt
        if self.dead:
            return False 
        distance = pygame.Vector2(self.rect.center).distance_to(player.rect.center)
        if self.state == self.PATROL:
            if (
                distance <= self.detection_range
                and world.has_line_of_sight(
                    self.position,
                    player.position
                )
            ):
                self.state = self.CHASE
        elif self.state == self.CHASE:
            if distance <= self.attack_range:
                self.state = self.ATTACK
                self.attack_cooldown = 0
            elif distance > self.detection_range:
                self.state = self.SEARCH
                self.search_timer = self.search_duration
        elif self.state == self.ATTACK:
            if distance > self.detection_range:
                self.state = self.SEARCH
                self.search_timer = self.search_duration
            elif distance > self.attack_range:
                self.state = self.CHASE
            elif not world.has_line_of_sight(
                self.position,
                player.position
            ):
                self.state = self.CHASE
                self.path = []
                self.path_index = 0
                self.path_timer = 0
        elif self.state == self.SEARCH:
            self.search_timer -= dt
            if (
                distance <= self.detection_range
                and world.has_line_of_sight(
                    self.position,
                    player.position
                )
            ):
                self.state = self.CHASE
                self.path = []
                self.path_index = 0
                self.path_timer = 0
            elif self.search_timer <= 0:
                self.state = self.PATROL
                self.path = []
                self.path_index = 0
                self.velocity = pygame.Vector2()

        if self.state == self.PATROL:
            self.update_patrol(dt, world)
        elif self.state == self.CHASE:
            self.update_chase(dt, player, world)
        elif self.state == self.ATTACK:
            return self.update_attack(dt, player, world)
        elif self.state == self.SEARCH:
            self.update_search(dt, world)
        return False

    def update_patrol(self, dt, world):
        movement = self.direction * self.speed * dt
        new_x = self.position.x + movement
        new_rect = pygame.Rect(
            new_x,
            self.position.y,
            self.width,
            self.height
        )
        if not world.is_rect_colliding(new_rect):
            self.position.x = new_x
        else:
            self.direction *= -1

    def update_chase(self, dt, player, world):
        self.path_timer -= dt
        if self.path_timer <= 0:
            new_path = world.find_path(
                self.position,
                player.position
            )
            if new_path:
                self.path = new_path
                closest_index = 0
                closest_distance = float("inf")
                for i, (tile_x, tile_y) in enumerate(self.path):
                    target = pygame.Vector2(
                        tile_y * world.TILE_SIZE
                        + world.TILE_SIZE / 2
                        - self.width / 2,
                        tile_x * world.TILE_SIZE
                        + world.TILE_SIZE / 2
                        - self.height / 2
                    )
                    distance = self.position.distance_squared_to(target)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_index = i
                self.path_index = closest_index
            self.path_timer = 0.5
        if not self.path:
            return
        if self.path_index >= len(self.path):
            self.path = []
            return
        tile_x, tile_y = self.path[self.path_index]
        target = pygame.Vector2(
            tile_x * world.TILE_SIZE
            + world.TILE_SIZE / 2
            - self.width / 2,

            tile_y * world.TILE_SIZE
            + world.TILE_SIZE / 2
            - self.height / 2
        )
        direction = target - self.position
        
        desired = target - self.position
        if desired.length_squared() < 100:
            self.path_index += 1
            return
        desired = desired.normalize() * self.chase_speed
        steering = desired - self.velocity
        MAX_FORCE = 900
        MAX_SPEED = self.chase_speed
        if steering.length() > MAX_FORCE:
            steering.scale_to_length(MAX_FORCE)
        self.velocity += steering * dt
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)


        movement = self.velocity * dt

        new_x = self.position.x + movement.x
        x_rect = pygame.Rect(new_x, self.position.y, self.width, self.height)

        if not world.is_rect_colliding(x_rect):
            self.position.x = new_x
        else:
            self.velocity.x = 0

        new_y = self.position.y + movement.y
        y_rect = pygame.Rect(self.position.x, new_y, self.width, self.height)

        if not world.is_rect_colliding(y_rect):
            self.position.y = new_y
        else:
            self.velocity.y = 0

    def update_attack(self, dt, player, world):
        drone_center = pygame.Vector2(self.rect.center)
        player_center = pygame.Vector2(player.rect.center)
        direction = player_center - drone_center
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.aim_direction = direction
        distance = drone_center.distance_to(player_center)
        if distance < self.preferred_attack_distance - 30:
            movement = -direction * self.chase_speed * dt
        elif distance > self.preferred_attack_distance + 30:
            movement = direction * self.chase_speed * dt
        else:
            self.strafe_timer -= dt
            if self.strafe_timer <= 0:
                self.strafe_timer = self.strafe_change_time
                self.strafe_direction *= -1
            strafe = pygame.Vector2(
                -direction.y,
                direction.x
            )
            movement = (
                strafe
                * self.strafe_direction
                * self.strafe_speed
                * dt
            )
        new_x = self.position.x + movement.x
        x_rect = pygame.Rect(
            new_x,
            self.position.y,
            self.width,
            self.height
        )
        if not world.is_rect_colliding(x_rect):
            self.position.x = new_x
        new_y = self.position.y + movement.y
        y_rect = pygame.Rect(
            self.position.x,
            new_y,
            self.width,
            self.height
        )
        if not world.is_rect_colliding(y_rect):
            self.position.y = new_y
        if not world.has_line_of_sight(
            self.position,
            player.position
        ):
            return False
        self.attack_cooldown -= dt
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_delay
            return True
        return False 
        new_x = self.position.x + movement.x
        x_rect = pygame.Rect(
            new_x,
            self.position.y,
            self.width,
            self.height
        )
        if not world.is_rect_colliding(x_rect):
            self.position.x = new_x
        else:
            self.strafe_direction *= -1
            self.strafe_timer = 0
        new_y = self.position.y + movement.y
        y_rect = pygame.Rect(
            self.position.x,
            new_y,
            self.width,
            self.height
        )
        if not world.is_rect_colliding(y_rect):
            self.position.y = new_y
        
    def update_search(self, dt, world):
        self.velocity = pygame.Vector2()
        movement = (
            self.direction *
            self.speed *
            0.5 *
            dt
        )
        new_x = self.position.x + movement
        new_rect = pygame.Rect(
            new_x,
            self.position.y,
            self.width,
            self.height
        )
        if not world.is_rect_colliding(new_rect):
            self.position.x = new_x
        else:
            self.direction *= -1

    def draw(self, screen, camera):
        rect = camera.apply(self.rect)
        if self.dead:
            if self.explosion_timer <= 0:
                return
            progress = 1.0 - (
                self.explosion_timer / 0.35
            )
            radius = int(
                15 + progress * 35
            )
            pygame.draw.circle(
                screen,
                (255, 140, 40),
                rect.center,
                radius,
                3
            )
            pygame.draw.circle(
                screen,
                (255, 220, 100),
                rect.center,
                max(3, radius // 3)
            )
            return
        if self.damage_flash > 0:
            color = (255, 80, 80)
        else:
            color = self.color
        pygame.draw.circle(
            screen,
            color,
            rect.center,
            15
        )
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            rect.center,
            5
        )
        