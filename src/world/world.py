import pygame
import random
import heapq 
class World:
    def __init__(self):
        self.TILE_SIZE = 64
        self.MAP =self.generate_map()
        self.obstacles = []

    def generate_map(self, width=28, height=15):
        while True:
            grid = [
                ["#" for _ in range(width)]
                for _ in range(height)
            ]

            for y in range(1, height - 1):
                for x in range(1, width - 1):

                    grid[y][x] = "."

            for _ in range(12):
                obstacle_width = random.randint(2, 6)
                obstacle_height = random.randint(1, 3)
                x = random.randint(
                    2,
                    width - obstacle_width - 2
                )
                y = random.randint(
                    2,
                    height - obstacle_height - 2
                )
                spawn_x = width // 2
                spawn_y = height // 2
                if (
                    abs(x - spawn_x) < 4
                    and abs(y - spawn_y) < 3
                ):
                    continue
                for oy in range(obstacle_height):
                    for ox in range(obstacle_width):
                        grid[y + oy][x + ox] = "#"
            if self.is_map_connected(grid):

                return [
                    "".join(row)
                    for row in grid
                ]

    def draw(self, screen, camera):
        for row_index, row in enumerate(self.MAP):
            for col_index, tile in enumerate(row):
                world_x = col_index * self.TILE_SIZE
                world_y = row_index * self.TILE_SIZE
                rect = pygame.Rect(world_x, world_y, self.TILE_SIZE, self.TILE_SIZE)
                rect = camera.apply(rect)

                if tile == "#":
                    color = (80, 80, 80)

                else:
                    color = (30, 30, 30)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (45, 45, 45), rect, 1)   

    def is_wall(self, row, col):
        if row < 0 or row >= len(self.MAP):
            return True
        if col < 0 or col >= len(self.MAP[0]):
            return True
        return self.MAP[row][col] == "#"

    def is_rect_colliding(self, rect):
        left = int(rect.left // self.TILE_SIZE)
        right = int((rect.right - 1) // self.TILE_SIZE)
        top = int(rect.top // self.TILE_SIZE)
        bottom = int((rect.bottom - 1) // self.TILE_SIZE)
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if self.is_wall(row, col):
                    return True
        return False

    def is_position_valid(self, x, y, width, height):
        rect = pygame.Rect(
            x,
            y,
            width,
            height
        )
        return not self.is_rect_colliding(rect)

    def find_valid_position(self, width, height, min_distance=0, origin=None):
        valid_positions = []
        for row in range(1, len(self.MAP) - 1):
            for col in range(1, len(self.MAP[0]) - 1):
                x = (
                    col * self.TILE_SIZE
                    + self.TILE_SIZE / 2
                    - width / 2
                )
                y = (
                    row * self.TILE_SIZE
                    + self.TILE_SIZE / 2
                    - height / 2
                )
                if not self.is_position_valid(
                    x,
                    y,
                    width,
                    height
                ):
                    continue
                position = pygame.Vector2(x, y)
                if origin is not None:
                    if position.distance_to(origin) < min_distance:
                        continue
                valid_positions.append(position)
        if not valid_positions:
            return None
        return random.choice(valid_positions)

    def is_map_connected(self, grid):
        height = len(grid)
        width = len(grid[0])
        start = None
        for y in range(height):
            for x in range(width):
                if grid[y][x] == ".":
                    start = (x, y)
                    break
            if start is not None:
                break
        if start is None:
            return False
        visited = {start}
        stack = [start]
        while stack:
            x, y = stack.pop()
            neighbours = (
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            )
            for nx, ny in neighbours:
                if nx < 0 or nx >= width:
                    continue
                if ny < 0 or ny >= height:
                    continue
                if grid[ny][nx] != ".":
                    continue
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                stack.append((nx, ny))
        walkable_tiles = sum(
            row.count(".")
            for row in grid
        )
        return len(visited) == walkable_tiles

    def find_path(self, start, goal):
        start_x = int(start.x // self.TILE_SIZE)
        start_y = int(start.y // self.TILE_SIZE)
        goal_x = int(goal.x // self.TILE_SIZE)
        goal_y = int(goal.y // self.TILE_SIZE)
        start = (start_x, start_y)
        goal = (goal_x, goal_y)
        if self.is_wall(start_y, start_x):
            return []
        if self.is_wall(goal_y, goal_x):
            return []
        if start == goal:
            return []
        open_set = []
        heapq.heappush(
            open_set,
            (0, start)
        )
        came_from = {}
        cost_so_far = {
            start: 0
        }
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                break
            current_x, current_y = current
            neighbours = (
                (current_x + 1, current_y),
                (current_x - 1, current_y),
                (current_x, current_y + 1),
                (current_x, current_y - 1)
            )
            for next_x, next_y in neighbours:
                if self.is_wall(next_y, next_x):
                    continue
                next_tile = (next_x, next_y)
                new_cost = cost_so_far[current] + 1
                if (
                    next_tile not in cost_so_far
                    or new_cost < cost_so_far[next_tile]
                ):
                    cost_so_far[next_tile] = new_cost
                    heuristic = (
                        abs(next_x - goal_x) +
                        abs(next_y - goal_y)
                    )
                    priority = new_cost + heuristic
                    heapq.heappush(
                        open_set,
                        (priority, next_tile)
                    )
                    came_from[next_tile] = current
        if goal not in came_from:
            return []
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path