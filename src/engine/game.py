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
        self.timer = TimeEngine()
        self.input = InputManager()
        self.camera = Camera()
        self.world = World()
        self.debug = DebugOverlay()
        self.bullets = []
        self.hit_effects = []
        player_position = self.world.find_valid_position(32, 32)
        if player_position is None :
            raise RuntimeError("Could not find a valid player spawn position")
        self.player = Player(player_position)
        self.drones = []
        for _ in range(3):
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
                        drone_position.y
                    )
                )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug.toggle()
                elif event.key == pygame.K_r:
                    if self.player.dead:
                        self.restart()

    def update(self):
        real_dt = self.clock.get_time() / 1000
        movement = self.input.get_movement()
        self.timer.update(self.input.is_moving())
        game_dt = self.timer.delta(real_dt)
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
                        drone.take_damage(bullet.damage)
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
            if not drone.dead:
                drone.draw(self.screen, self.camera)
        self.debug.draw(self.screen, self)
        for bullet in self.bullets:
            bullet.draw(self.screen, self.camera)
        pygame.draw.rect(
            self.screen,
            (60, 60, 60),
            pygame.Rect(20, 20, 200, 20)
        )

        health_width = int(
            200 * (
                self.player.health /
                self.player.max_health
            )
        )

        pygame.draw.rect(
            self.screen,
            (0, 200, 0),
            pygame.Rect(20, 20, health_width, 20)
        )
        if self.player.dead:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 160))

            self.screen.blit(
                overlay,
                (0, 0)
            )
            font = pygame.font.Font(None, 64)
            text = font.render(
                "YOU DIED",
                True,
                (255, 255, 255)
            )
            text_rect = text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 30)
            )
            self.screen.blit(
                text,
                text_rect
            )
            font_small = pygame.font.Font(None, 32)

            restart_text = font_small.render(
                "Press R to restart",
                True,
                (200, 200, 200)
            )
            restart_rect = restart_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 30)
            )
            self.screen.blit(
                restart_text,
                restart_rect
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
        pygame.display.flip()                                                           


    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def set_rotation(self, angle):
        self.rotation = angle

    def restart(self):
        player_position = self.world.find_valid_position(
            32,
            32
        )
        if player_position is None:
            return
        self.player = Player(player_position)
        self.drones = []
        for _ in range(3):
            drone_position = self.world.find_valid_position(                    
                30,
                30,
                min_distance=250,
                origin=self.player.position)
            if drone_position is not None:
                self.drones.append(
                    Drone(
                            drone_position.x,                            drone_position.y
                    )
                )
        self.bullets.clear()