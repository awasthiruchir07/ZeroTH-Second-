import pygame
class DebugOverlay:

    def __init__(self):
        self.visible = False
        self.font = pygame.font.SysFont("Consolas", 20)

    def toggle(self):
        self.visible = not self.visible
        print("Toggle",self.visible)

    def draw(self, screen, game):   
        if self.visible:
            for obstacle in game.world.obstacles:
                rect = game.camera.apply(obstacle)
                pygame.draw.rect(
                    screen,
                    (255, 150, 0),
                    rect,
                    2
                )

        if not self.visible:
            return
        lines = [
            f"FPS : {game.clock.get_fps():.1f}",
            f"Time Scale : {game.timer.scale:.2f}",
            f"Player : ({game.player.position.x:.1f}, {game.player.position.y:.1f})",
            f"Camera : ({game.camera.offset.x:.1f}, {game.camera.offset.y:.1f})",
            f"Drone : ({game.drone.position.x:.1f}, {game.drone.position.y:.1f})",
            f"Bullets : {len(game.bullets)}",
            f"Drone HP : {game.drone.health}",
            f"Player HP : {game.player.health}",
            f"Drone State : {'DEAD' if game.drone.dead else 'ACTIVE'}",
            f"Drone State : {game.drone.state}",
        ]
        y = 10
        for line in lines:
            surface = self.font.render(line, True, (0,255,0))
            screen.blit(surface, (10,y))
            y += 24
        hitbox = game.camera.apply(game.player.hitbox)
        pygame.draw.rect(screen, (255,0,0), hitbox, 2)

        if game.drone.path:
            for tile_x, tile_y in game.drone.path:
                world_position = pygame.Vector2(
                    tile_y * game.world.TILE_SIZE
                    + game.world.TILE_SIZE / 2,

                    tile_x * game.world.TILE_SIZE
                    + game.world.TILE_SIZE / 2
                )
                screen_position = game.camera.apply(
                    pygame.Rect(
                        world_position.x,
                        world_position.y,
                        1,
                        1
                    )
                ).center
                pygame.draw.circle(
                    screen,
                    (0, 255, 255),
                    screen_position,
                    4
                )



    