import pygame

from src.entities.entity import Entity
from src.world.world import World
from src.engine.settings import PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_SPEED
from src.weapons.weapon_manager import WeaponManager


class Player(Entity):
    def __init__(self, position):
        # Match the gameplay hitbox to the visual player sprite.
        self.player_width = 40
        self.player_height = 56

        super().__init__(
            position.x,
            position.y,
            self.player_width,
            self.player_height
        )

        self.speed = PLAYER_SPEED
        self.rotation = 0
        self.weapon = WeaponManager()

        self.health = 100
        self.max_health = 100
        self.dead = False
        self.damage_flash = 0.0
        self.color = (255, 255, 255)
        self.muzzle_flash = 0.0
        self.aim_direction = pygame.Vector2(1, 0)

        # =========================
        # PLAYER ANIMATION
        # =========================

        self.sprite_sheet = pygame.image.load(
            "assets/sprites/player_sheet.png"
        ).convert()

        self.facing = "front"
        self.animation = "idle"
        self.animation_frame = 0
        self.animation_timer = 0.0

        # These are deliberately short because the game sets
        # muzzle_flash = 0.06 when the player shoots and
        # damage_flash = 0.12 when the player is hit.
        self.walk_speed = 0.12
        self.shoot_speed = 0.02
        self.hurt_speed = 0.06

        # Visual sprite size matches the collision rectangle.
        self.sprite_width = self.width
        self.sprite_height = self.height

        self.load_animations()

    def take_damage(self, amount):
        if self.dead:
            return

        self.health -= amount
        self.damage_flash = 0.12

        # Start the hurt animation immediately.
        self.animation = "hurt"
        self.animation_frame = 0
        self.animation_timer = 0.0

        if self.health <= 0:
            self.health = 0
            self.dead = True

    def set_rotation(self, angle):
        self.rotation = angle

    def update(self, dt, movement, world):
        if self.damage_flash > 0:
            self.damage_flash -= dt
            if self.damage_flash < 0:
                self.damage_flash = 0

        if self.dead:
            return

        # Store movement for animation/debugging.
        self.velocity = pygame.Vector2(movement)

        if movement.length_squared() > 0:
            movement = movement.normalize()

        # Collision-safe X movement.
        new_x = self.position.x + movement.x * self.speed * dt

        x_rect = pygame.Rect(
            round(new_x),
            round(self.position.y),
            self.width,
            self.height
        )

        if not world.is_rect_colliding(x_rect):
            self.position.x = new_x

        # Collision-safe Y movement.
        new_y = self.position.y + movement.y * self.speed * dt

        y_rect = pygame.Rect(
            round(self.position.x),
            round(new_y),
            self.width,
            self.height
        )

        if not world.is_rect_colliding(y_rect):
            self.position.y = new_y

        # Keep the actual collision rect synchronized.
        self.rect.topleft = (
            round(self.position.x),
            round(self.position.y)
        )

        if self.muzzle_flash > 0:
            self.muzzle_flash -= dt
            if self.muzzle_flash < 0:
                self.muzzle_flash = 0

        self.weapon.update(dt)
        self.update_animation(dt, movement)

    def _remove_checkerboard(self, surface):
        """
        The generated sprite sheet contains a light checkerboard
        instead of real alpha in some exported versions.
        Remove only light, low-saturation background pixels.
        Dark sprite pixels remain intact.
        """
        surface = surface.convert_alpha()

        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                r, g, b, _ = surface.get_at((x, y))

                if (
                    max(r, g, b) - min(r, g, b) < 12
                    and (r + g + b) / 3 > 100
                ):
                    surface.set_at(
                        (x, y),
                        (r, g, b, 0)
                    )

        return surface

    def _make_frame(self, rect):
        # Clamp the crop to the actual sprite-sheet dimensions.
        rect = rect.clip(self.sprite_sheet.get_rect())

        frame = self.sprite_sheet.subsurface(rect).copy()
        frame = self._remove_checkerboard(frame)

        # Preserve aspect ratio instead of vertically compressing
        # every character into a square.
        scale = min(
            self.sprite_width / frame.get_width(),
            self.sprite_height / frame.get_height()
        )

        new_size = (
            max(1, round(frame.get_width() * scale)),
            max(1, round(frame.get_height() * scale))
        )

        frame = pygame.transform.scale(
            frame,
            new_size
        )

        # Put the sprite into a fixed-size transparent canvas.
        # This keeps every animation frame aligned.
        canvas = pygame.Surface(
            (self.sprite_width, self.sprite_height),
            pygame.SRCALPHA
        )

        canvas.blit(
            frame,
            frame.get_rect(center=canvas.get_rect().center)
        )

        return canvas

    def load_animations(self):
        sheet = self.sprite_sheet

        # Coordinates are kept in the same coordinate system used
        # for the current player sprite sheet.
        self.animations = {
            "idle": {
                "front": [
                    pygame.Rect(205, 100, 145, 180)
                ],
                "right": [
                    pygame.Rect(450, 100, 125, 180)
                ],
                "back": [
                    pygame.Rect(670, 100, 145, 180)
                ],
                "left": [
                    pygame.Rect(910, 100, 125, 180)
                ],
            },

            "walk": {
                "front": [
                    pygame.Rect(101, 410, 81, 150),
                    pygame.Rect(188, 410, 81, 150),
                    pygame.Rect(276, 410, 81, 150),
                ],

                "right": [
                    pygame.Rect(389, 409, 89, 160),
                    pygame.Rect(477, 409, 87, 160),
                    pygame.Rect(563, 409, 87, 160),
                ],

                "back": [
                    pygame.Rect(681, 410, 91, 162),
                    pygame.Rect(776, 410, 82, 162),
                    pygame.Rect(861, 409, 91, 163),
                ],

                "left": [
                    pygame.Rect(980, 409, 82, 160),
                    pygame.Rect(1065, 410, 83, 159),
                    pygame.Rect(1153, 410, 88, 159),
                ],
            },

            "shoot": {
                "front": [
                    pygame.Rect(101, 680, 95, 175),
                    pygame.Rect(190, 680, 100, 175),
                    pygame.Rect(280, 680, 115, 175),
                ],

                "right": [
                    pygame.Rect(390, 680, 100, 175),
                    pygame.Rect(490, 680, 100, 175),
                    pygame.Rect(585, 680, 110, 175),
                ],

                "back": [
                    pygame.Rect(700, 680, 100, 175),
                    pygame.Rect(795, 680, 100, 175),
                    pygame.Rect(890, 680, 105, 175),
                ],

                "left": [
                    pygame.Rect(985, 680, 100, 175),
                    pygame.Rect(1080, 680, 100, 175),
                    pygame.Rect(1175, 680, 115, 175),
                ],
            },

            "hurt": {
                "front": [
                    pygame.Rect(110, 945, 115, 180),
                    pygame.Rect(225, 945, 125, 180),
                ],

                "right": [
                    pygame.Rect(410, 945, 110, 185),
                    pygame.Rect(525, 945, 115, 185),
                ],

                "back": [
                    pygame.Rect(690, 945, 125, 185),
                    pygame.Rect(815, 945, 120, 185),
                ],

                "left": [
                    pygame.Rect(985, 945, 110, 185),
                    pygame.Rect(1095, 945, 110, 185),
                ],
            },
        }

        # Convert all source rectangles into actual, aligned images.
        for animation in self.animations:
            for direction in self.animations[animation]:
                self.animations[animation][direction] = [
                    self._make_frame(rect)
                    for rect in self.animations[animation][direction]
                ]

    def _set_animation(self, animation):
        if animation != self.animation:
            self.animation = animation
            self.animation_frame = 0
            self.animation_timer = 0.0

    def update_animation(self, dt, movement):
        # Determine facing from mouse aim.
        if abs(self.aim_direction.x) > abs(self.aim_direction.y):
            if self.aim_direction.x > 0:
                self.facing = "right"
            else:
                self.facing = "left"
        else:
            if self.aim_direction.y > 0:
                self.facing = "front"
            else:
                self.facing = "back"

        # Animation priority:
        # HURT > SHOOT > WALK > IDLE
        if self.damage_flash > 0:
            animation = "hurt"
        elif self.muzzle_flash > 0:
            animation = "shoot"
        elif movement.length_squared() > 0:
            animation = "walk"
        else:
            animation = "idle"

        self._set_animation(animation)

        # Idle is a single frame.
        if animation == "idle":
            self.animation_frame = 0
            self.animation_timer = 0.0
            return

        if animation == "walk":
            frame_time = self.walk_speed
        elif animation == "shoot":
            frame_time = self.shoot_speed
        else:
            frame_time = self.hurt_speed

        self.animation_timer += dt

        while self.animation_timer >= frame_time:
            self.animation_timer -= frame_time

            frames = self.animations[
                animation
            ][self.facing]

            self.animation_frame += 1

            if animation == "hurt":
                # Play both hurt frames once.
                if self.animation_frame >= len(frames):
                    self.animation_frame = len(frames) - 1
            else:
                # Walk and shoot loop through their frames.
                self.animation_frame %= len(frames)

    def draw(self, screen, camera):
        screen_rect = camera.apply(self.rect)

        frames = self.animations[
            self.animation
        ][self.facing]

        frame_index = min(
            self.animation_frame,
            len(frames) - 1
        )

        image = frames[frame_index]

        # Anchor the character by the feet instead of putting
        # the larger visual sprite at the collision rect's top-left.
        sprite_rect = image.get_rect(
            midbottom=screen_rect.midbottom
        )

        screen.blit(
            image,
            sprite_rect
        )

        # Muzzle flash only. The old cyan aiming rod is removed.
        if self.muzzle_flash > 0:
            center = pygame.Vector2(
                sprite_rect.center
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
