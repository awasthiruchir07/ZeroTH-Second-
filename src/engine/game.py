import pygame 
from src.engine.settings import *
from src.entities.player import Player
from src.engine.timer import TimeEngine
from src.engine.camera import Camera
from src.world.world import World
from src.entities.drone import Drone
from src.engine.input import InputManager
from src.ui.debug import DebugOverlay
from src.weapons.bullet import Bullet

class Game :
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "MENU"

        self.play_button = pygame.Rect(0, 0, 300, 70)
        self.play_button.center = (WIDTH // 2, 385)

        self.quit_button = pygame.Rect(0, 0, 300, 70)
        self.quit_button.center = (WIDTH // 2, 485)
        self.timer = TimeEngine()
        self.input = InputManager()
        self.camera = Camera()
        self.world = World()
        self.debug = DebugOverlay()
        self.pistol_icon = pygame.image.load(
            "assets/sprites/pistol.png"
        ).convert()
        # Crop the empty space around the pistol
        pistol_crop = pygame.Rect(
            270,   # left
            190,   # top
            1030,  # width
            700    # height
        )
        self.pistol_icon = self.pistol_icon.subsurface(
            pistol_crop
        ).copy()
        # Remove the dark background
        for x in range(self.pistol_icon.get_width()):
            for y in range(self.pistol_icon.get_height()):
                r, g, b, a = self.pistol_icon.get_at((x, y))

                # Make dark background transparent
                if r < 25 and g < 25 and b < 25:
                    self.pistol_icon.set_at(
                        (x, y),
                        (r, g, b, 0)
                    )
        # Scale while preserving the original aspect ratio
        original_width = self.pistol_icon.get_width()
        original_height = self.pistol_icon.get_height()

        scale = 64 / max(original_width, original_height)

        new_size = (
            int(original_width * scale),
            int(original_height * scale)
        )

        self.pistol_icon = pygame.transform.scale(
            self.pistol_icon,
            new_size
        )
        self.bullets = []
        self.hit_effects = []
        player_position = self.world.find_valid_position(40, 56)
        if player_position is None :
            raise RuntimeError("Could not find a valid player spawn position")
        self.player = Player(player_position)
        self.drones = []
        self.wave = 1
        self.wave_clear_timer = 0.0
        self.wave_delay = 2.0
        self.score = 0
        self.game_over = False
        self.wave_message = ""
        self.wave_message_timer = 0.0
        self.spawn_wave()  
        self.wave_message = f"WAVE {self.wave}"
        self.wave_message_timer = 2.0   

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.game_state = "GAME"
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.collidepoint(event.pos):
                    self.game_state = "GAME"
                elif self.quit_button.collidepoint(event.pos):
                    self.running = False

    def draw_menu(self):
        self.screen.fill((0, 0, 0))

        title_font = pygame.font.SysFont("Consolas", 76, bold=True)
        subtitle_font = pygame.font.SysFont("Consolas", 24, bold=True)
        button_font = pygame.font.SysFont("Consolas", 38, bold=True)
        small_font = pygame.font.SysFont("Consolas", 16)

        title = title_font.render("ZEROTH SECOND", True, (235, 245, 255))
        self.screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 170))
        )

        subtitle = subtitle_font.render(
            "TIME IS YOUR WEAPON",
            True,
            (100, 180, 220)
        )
        self.screen.blit(
            subtitle,
            subtitle.get_rect(center=(WIDTH // 2, 235))
        )

        # Sci-fi divider
        pygame.draw.line(
            self.screen,
            (70, 120, 150),
            (WIDTH // 2 - 220, 275),
            (WIDTH // 2 + 220, 275),
            2
        )

        mouse_pos = pygame.mouse.get_pos()

        for rect, label in (
            (self.play_button, "PLAY"),
            (self.quit_button, "QUIT")
        ):
            hovered = rect.collidepoint(mouse_pos)

            pygame.draw.rect(
                self.screen,
                (28, 38, 48) if hovered else (15, 20, 27),
                rect,
                border_radius=10
            )
            pygame.draw.rect(
                self.screen,
                (150, 220, 245) if hovered else (80, 150, 185),
                rect,
                2,
                border_radius=10
            )

            text = button_font.render(label, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=rect.center))

        controls = small_font.render(
            "ENTER / SPACE  PLAY     ESC  QUIT",
            True,
            (100, 110, 120)
        )
        self.screen.blit(
            controls,
            controls.get_rect(center=(WIDTH // 2, HEIGHT - 45))
        )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug.toggle()
                elif event.key == pygame.K_r:
                    if self.game_over or self.player.dead:
                        self.restart()
                    else:
                        self.player.weapon.reload()

    def spawn_wave(self):
        self.drones = []
        drone_types = ["basic", "scout", "tank"]
        drone_count = 2 + self.wave
        for i in range(drone_count):
            drone_type = drone_types[i % len(drone_types)]
            drone_position = self.world.find_valid_position(
                30,
                30,
                min_distance=250,
                origin=self.player.position
            )
            if drone_position is not None:
                self.drones.append(
                    Drone(
                        drone_position.x,
                        drone_position.y,
                        drone_type
                    )
                )

    def update(self):
        real_dt = self.clock.get_time() / 1000
        movement = self.input.get_movement()
        self.timer.update(self.input.is_moving())
        game_dt = self.timer.delta(real_dt)
        if self.wave_message_timer > 0:
            self.wave_message_timer -= game_dt
        if self.game_over:
            return
        self.player.update(real_dt, movement, self.world)
        mouse = self.input.get_mouse_position()
        player_screen = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        direction = mouse - player_screen
        if direction.length_squared() > 0:
            self.player.set_rotation(direction.angle_to(pygame.Vector2(1, 0)))
            self.player.aim_direction = direction.normalize()
        for drone in self.drones:
            drone_firing = drone.update(
                game_dt,
                self.player,
                self.world
            )
            if drone_firing:
                spawn_position = (
                    drone.position +
                    pygame.Vector2(
                        drone.width / 2,
                        drone.height / 2
                    )
                )
                self.bullets.append(
                    Bullet(
                        spawn_position,
                        drone.aim_direction,
                        "drone"
                    )
                )
        if self.player.health <= 0:
            self.game_over = True
        if self.drones and all(drone.dead for drone in self.drones):
            self.wave_clear_timer += game_dt
            if self.wave_clear_timer >= self.wave_delay:
                self.wave += 1
                self.wave_clear_timer = 0.0
                self.spawn_wave()
                self.wave_message = f"WAVE {self.wave}"
                self.wave_message_timer = 2.0
        self.camera.update(self.player, WIDTH, HEIGHT)
        if self.input.is_shooting():
            if self.player.weapon.can_fire():
                self.player.weapon.fire()
                self.player.muzzle_flash = 0.06
                spawn_position = (
                    self.player.position +
                    pygame.Vector2(
                        self.player.width / 2,
                        self.player.height / 2
                    )
                )
                self.bullets.append(
                    Bullet(
                        spawn_position,
                        self.player.aim_direction,
                        "player"
                    )
                )                
        for bullet in self.bullets:
            bullet.update(game_dt, self.world)
            if bullet.dead:
                continue
            if bullet.owner == "player":
                for drone in self.drones:
                    if drone.dead:
                        continue
                    if bullet.hitbox.colliderect(drone.hitbox):
                        was_alive = not drone.dead
                        drone.take_damage(bullet.damage)
                        if was_alive and drone.dead:
                            if drone.drone_type == "basic":
                                self.score += 100
                            elif drone.drone_type == "scout":
                                self.score += 150
                            elif drone.drone_type == "tank":
                                self.score += 250
                        self.hit_effects.append(
                            [
                                pygame.Vector2(bullet.position),
                                0.12
                            ]
                        )
                        bullet.dead = True
                        break

            if (
                bullet.owner == "drone"
                and not self.player.dead
            ):

                if bullet.hitbox.colliderect(
                    self.player.hitbox
                ):
                    self.player.take_damage(
                        bullet.damage
                    )
                    self.hit_effects.append(
                        [
                            pygame.Vector2(
                                bullet.position
                            ),
                            0.12
                        ]
                    )
                    bullet.dead = True
                    continue
        for effect in self.hit_effects:
            effect[1] -= game_dt
        self.hit_effects = [
            effect
            for effect in self.hit_effects
            if effect[1] > 0
        ]
        self.bullets = [
            bullet
            for bullet in self.bullets
            if not bullet.dead
        ]
            
    def draw(self):
        self.screen.fill(BACKGROUND)
        self.world.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        for drone in self.drones:
            drone.draw(self.screen, self.camera)
        self.debug.draw(self.screen, self)
        for bullet in self.bullets:
            bullet.draw(self.screen, self.camera)
        # =========================
        # GRAPHICAL HUD
        # =========================

        hud = pygame.Surface((360, 170), pygame.SRCALPHA)

        # Panel background
        pygame.draw.rect(
            hud,
            (15, 18, 24, 220),
            pygame.Rect(0, 0, 360, 170),
            border_radius=14
        )

        # Outer border
        pygame.draw.rect(
            hud,
            (100, 180, 220, 255),
            pygame.Rect(0, 0, 360, 170),
            2,
            border_radius=14
        )
        pygame.draw.rect(
            hud,
            (180, 220, 240, 255),
            pygame.Rect(8, 8, 30, 3)
        )
        pygame.draw.rect(
            hud,
            (180, 220, 240, 255),
            pygame.Rect(8, 8, 3, 30)
        )
        pygame.draw.rect(
            hud,
            (180, 220, 240, 255),
            pygame.Rect(322, 159, 30, 3)
        )

        pygame.draw.rect(
            hud,
            (180, 220, 240, 255),
            pygame.Rect(349, 132, 3, 30)
        )

        # -------------------------
        # HEALTH
        # -------------------------

        pygame.draw.rect(
            hud,
            (40, 45, 52, 255),
            pygame.Rect(20, 20, 320, 25),
            border_radius=6
        )

        health_ratio = max(
            0,
            self.player.health / self.player.max_health
        )

        health_width = int(320 * health_ratio)

        if health_width > 0:
            pygame.draw.rect(
                hud,
                (50, 210, 80, 255),
                pygame.Rect(
                    20,
                    20,
                    health_width,
                    25
                ),
                border_radius=6
            )

        hud_font = pygame.font.SysFont(
            "Consolas",
            20,
            bold=True
        )

        small_font = pygame.font.SysFont(
            "Consolas",
            18,
            bold=True
        )

        health_text = hud_font.render(
            f"HP  {self.player.health}/{self.player.max_health}",
            True,
            (255, 255, 255)
        )

        hud.blit(
            health_text,
            (30, 21)
        )

        # -------------------------
        # SCORE
        # -------------------------

        score_text = hud_font.render(
            f"SCORE: {self.score}",
            True,
            (255, 255, 255)
        )

        hud.blit(
            score_text,
            (20, 60)
        )

        # -------------------------
        # WAVE
        # -------------------------

        wave_text = hud_font.render(
            f"WAVE: {self.wave}",
            True,
            (255, 255, 255)
        )

        hud.blit(
            wave_text,
            (235, 60)
        )

        # Divider
        pygame.draw.line(
            hud,
            (70, 80, 90, 255),
            (20, 92),
            (340, 92),
            2
        )

        # -------------------------
        # PISTOL ICON
        # -------------------------

        hud.blit(
            self.pistol_icon,
            (20, 100)
        )

        # -------------------------
        # AMMO
        # -------------------------

        ammo = self.player.weapon.weapon.ammo
        magazine = self.player.weapon.weapon.magazine_size

        ammo_text = hud_font.render(
            f"{ammo} / {magazine}",
            True,
            (255, 255, 255)
        )

        hud.blit(
            ammo_text,
            (95, 117)
        )

        # -------------------------
        # RELOADING
        # -------------------------

        if self.player.weapon.weapon.reloading:
            reload_text = small_font.render(
                "RELOADING...",
                True,
                (255, 210, 80)
            )

            hud.blit(
                reload_text,
                (205, 117)
            )

        # Put HUD on screen
        self.screen.blit(
            hud,
            (20, HEIGHT - 190)
        )
        
        for position, timer in self.hit_effects:
            screen_position = self.camera.apply(
                pygame.Rect(
                    position.x,
                    position.y,
                    1,
                    1
                )
            ).center
            radius = int(
                4 + (0.12 - timer) * 40
            )
            pygame.draw.circle(
                self.screen,
                (255, 180, 60),
                screen_position,
                radius,
                2
            )
            if self.wave_message_timer > 0 and not self.game_over:
                announcement_font = pygame.font.SysFont(
                    "Consolas",
                    56,
                    bold=True
                )

                wave_message = announcement_font.render(
                    self.wave_message,
                    True,
                    (255, 255, 255)
                )

                wave_rect = wave_message.get_rect(
                    center=(WIDTH // 2, 100)
                )

                self.screen.blit(
                    wave_message,
                    wave_rect
                )
        if self.game_over:
            font = pygame.font.SysFont("Consolas", 48)
            game_over_text = font.render(
                "GAME OVER",
                True,
                (255, 80, 80)
            )
            score_text = font.render(
                f"Score: {self.score}",
                True,
                (255, 255, 255)
            )
            restart_text = font.render(
                "Press R to restart",
                True,
                (255, 255, 255)
            )
            center_x = self.screen.get_width() // 2
            self.screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(center_x, 250)
                )
            )
            self.screen.blit(
                score_text,
                score_text.get_rect(
                    center=(center_x, 310)
                )
            )
            self.screen.blit(
                restart_text,
                restart_text.get_rect(
                    center=(center_x, 370)
                )
            )
            # =========================
            # CROSSHAIR
            # =========================

            mouse_pos = self.input.get_mouse_position()

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                mouse_pos,
                10,
                1
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (mouse_pos.x - 16, mouse_pos.y),
                (mouse_pos.x - 5, mouse_pos.y),
                2
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (mouse_pos.x + 5, mouse_pos.y),
                (mouse_pos.x + 16, mouse_pos.y),
                2
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (mouse_pos.x, mouse_pos.y - 16),
                (mouse_pos.x, mouse_pos.y - 5),
                2
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (mouse_pos.x, mouse_pos.y + 5),
                (mouse_pos.x, mouse_pos.y + 16),
                2
            ) 
        pygame.display.flip()                                                           

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            if self.game_state == "MENU":
                self.handle_menu_events()
                self.draw_menu()
            else:
                self.handle_events()
                self.update()
                self.draw()

        pygame.quit()

    def set_rotation(self, angle):
        self.rotation = angle

    def restart(self):
        player_position = self.world.find_valid_position(
            40,
            56
        )
        if player_position is None:
            return
        self.player = Player(player_position)
        self.drones = []
        self.wave = 1
        self.wave_clear_timer = 0.0
        self.score = 0
        self.game_over = False
        self.bullets.clear()
        self.hit_effects.clear()
        self.spawn_wave()