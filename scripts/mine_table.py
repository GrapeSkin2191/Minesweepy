from enum import Enum, unique
import math
from random import choice, randint, random, uniform

import pygame

from scripts.animation import SimpleAnimation, Explosion


@unique
class TileState(Enum):
    none = 0
    cleared = 1
    flagged = 2
    mine_visible = 3


class MineTable2D:
    def __init__(self, game, grid_size: tuple[int, int], mine_total: int):
        self.game = game
        self.grid_size = grid_size
        self.mine_total = mine_total
        self.grid = []  # -1 for mine; positive values for the number of nearby mines
        self.grid_state = []  # default 0; 1 for cleared; 2 for flagged; 3 for visible mines
        self.tile_cleared = 0
        for i in range(self.grid_size[0]):
            self.grid.append([0] * self.grid_size[1])
            self.grid_state.append([TileState.none] * self.grid_size[1])
        self.pos: list[int] = [0, 0]
        self.tile_size: int = 0
        self.over = False

        self.border: int = 10
        self.default_top_border = 80
        self.top_border = self.default_top_border
        self.font = pygame.font.Font('./data/Mojangles.ttf', 512)
        self.default_numbers = [self.font.render(str(i), True, pygame.Color(c))
                                for i, c in enumerate(self.game.config['Color'], 1)]
        self.anim_dict: dict[tuple[int, int], tuple[SimpleAnimation, tuple[float, float]]] = {}

        self.generated = False

        self.double_click_dict: dict[tuple[int, int], int] = {}
        self.double_click_time = 30  # 0.5s under 60fps

    def pixel_to_grid(self, x: int, y: int) -> tuple[int, int]:
        return math.floor((x - self.pos[0]) / self.tile_size), math.floor((y - self.pos[1]) / self.tile_size)

    def grid_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        return self.pos[0] + self.tile_size * x, self.pos[1] + self.tile_size * y

    def is_in_grid(self, x: int, y: int) -> bool:
        return 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]

    def generate(self, clicked_pos: tuple[int, int]) -> None:
        for _ in range(self.mine_total):
            x = randint(0, self.grid_size[0] - 1)
            y = randint(0, self.grid_size[1] - 1)
            while self.grid[x][y] == -1 or (x, y) == clicked_pos:
                x = randint(0, self.grid_size[0] - 1)
                y = randint(0, self.grid_size[1] - 1)
            self.grid[x][y] = -1
        directions = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if self.grid[i][j] != -1:
                    for dx, dy in directions:
                        if 0 <= i + dx < self.grid_size[0] and 0 <= j + dy < self.grid_size[1] \
                                and self.grid[i + dx][j + dy] == -1:
                            self.grid[i][j] += 1

    def right_clicked_on(self, pos: tuple[int, int]) -> None:  # right click to flag
        if self.over:
            return
        x, y = self.pixel_to_grid(*pos)
        if self.is_in_grid(x, y) and (self.grid_state[x][y] == TileState.none or
                                      self.grid_state[x][y] == TileState.flagged):
            if self.grid_state[x][y] == TileState.none:
                self.grid_state[x][y] = TileState.flagged
            elif self.grid_state[x][y] == TileState.flagged:
                self.grid_state[x][y] = TileState.none

    def left_clicked_on(self, pos: tuple[int, int], player_click: bool = True) -> None:  # left click to clear
        if self.over:
            return
        x, y = self.pixel_to_grid(*pos)
        if self.is_in_grid(x, y):
            # normal left-click-to-clear
            if self.grid_state[x][y] == TileState.none:
                if not self.generated:
                    self.generate((x, y))
                    self.generated = True
                if self.grid[x][y] == -1:
                    self.game_over()
                elif self.grid[x][y] == 0:  # bfs
                    directions = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
                    queue: list[tuple[int, int]] = [(x, y)]
                    visited = []
                    for i in range(self.grid_size[0]):
                        visited.append([False] * self.grid_size[1])
                    while len(queue):
                        sx, sy = queue.pop(0)
                        visited[sx][sy] = True

                        if self.grid[sx][sy] != -1 and self.grid_state[sx][sy] != TileState.cleared:
                            self.grid_state[sx][sy] = TileState.cleared
                            self.tile_cleared += 1
                        if self.grid[sx][sy] > 0:
                            continue
                        for dx, dy in directions:
                            ex, ey = sx + dx, sy + dy
                            if (0 <= ex < self.grid_size[0] and 0 <= ey < self.grid_size[1]) and not visited[ex][ey]:
                                if self.grid[ex][ey] >= 0:
                                    queue.append((ex, ey))
                                    visited[ex][ey] = True
                else:
                    self.grid_state[x][y] = TileState.cleared
                    self.tile_cleared += 1
                if player_click and self.tile_cleared + self.mine_total == self.grid_size[0] * self.grid_size[1]:
                    self.all_clear()
            # double-click to automatically clear nearby tiles
            elif player_click and self.grid_state[x][y] == TileState.cleared:
                if (x, y) in self.double_click_dict:
                    del self.double_click_dict[(x, y)]
                    count = 0
                    directions = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
                    for dx, dy in directions:
                        ex, ey = x + dx, y + dy
                        if (0 <= ex < self.grid_size[0] and 0 <= ey < self.grid_size[1] and
                                self.grid_state[ex][ey] == TileState.flagged):
                            count += 1
                    if count == self.grid[x][y]:
                        for dx, dy in directions:
                            ex, ey = x + dx, y + dy
                            if self.grid_state[x][y] != 2:
                                self.left_clicked_on(self.grid_to_pixel(ex, ey), False)
                    if self.tile_cleared + self.mine_total == self.grid_size[0] * self.grid_size[1]:
                        self.all_clear()
                else:
                    self.double_click_dict[(x, y)] = 0

    def game_over(self) -> None:
        self.over = True
        print('game over')
        choice(self.game.sfx['explode']).play(fade_ms=100)
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if self.grid[i][j] == -1:
                    self.grid_state[i][j] = TileState.mine_visible
                    self.anim_dict[(i, j)] = (
                        Explosion(self.game.assets['explosion'], 3).scale_by(uniform(0.75, 1.25)),
                        (random(), random())
                    )

    def all_clear(self) -> None:
        self.over = True
        print('all clear')
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if self.grid[i][j] == -1:
                    self.grid_state[i][j] = TileState.flagged

    def wheel_clicked_on(self, pos: tuple[int, int]) -> None:  # TODO only for debugging
        x, y = self.pixel_to_grid(*pos)
        print(f'Tile({x},{y}): {self.grid[x][y]}, {self.grid_state[x][y]}')

    def update(self) -> None:
        # handle double clicks
        delete = set()
        for key in self.double_click_dict:
            self.double_click_dict[key] += 1
            if self.double_click_dict[key] > self.double_click_time:
                delete.add(key)
        for key in delete:
            del self.double_click_dict[key]
        del delete

        # draw the grid
        screen_size: tuple[int, int] = self.game.screen.get_size()
        self.top_border = (round(self.default_top_border * screen_size[1] / self.game.config['Graphics']['size'][1])
                           + self.border)
        grid_size = (screen_size[0] - self.border * 2, screen_size[1] - self.border - self.top_border)
        if grid_size[0] / self.grid_size[0] <= grid_size[1] / self.grid_size[1]:
            self.tile_size = round(grid_size[0] / self.grid_size[0])
            self.pos = [
                self.border + 1,
                round((self.top_border + 1) + grid_size[1] / 2 - self.grid_size[1] * self.tile_size / 2),
            ]
        else:
            self.tile_size = round(grid_size[1] / self.grid_size[1])
            self.pos = [
                round((self.border + 1) + grid_size[0] / 2 - self.grid_size[0] * self.tile_size / 2),
                self.top_border + 1,
            ]
        tile = pygame.transform.scale(self.game.assets['tile'], (self.tile_size, self.tile_size))
        flag = pygame.transform.scale(self.game.assets['flag'], (self.tile_size, self.tile_size))
        mine = pygame.transform.scale(self.game.assets['mine'], (self.tile_size, self.tile_size))
        numbers = [pygame.transform.scale_by(sf, self.tile_size / sf.get_size()[1]) for sf in self.default_numbers]
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                pos = self.grid_to_pixel(i, j)
                if self.grid_state[i][j] == TileState.cleared:
                    if self.grid[i][j] > 0:
                        text = numbers[self.grid[i][j] - 1]
                        self.game.screen.blit(text, (
                            pos[0] + self.tile_size / 2 - text.get_size()[0] * self.tile_size / text.get_size()[1] / 2,
                            pos[1]
                        ))
                else:
                    self.game.screen.blit(tile, pos)
                    if self.grid_state[i][j] == TileState.flagged:
                        self.game.screen.blit(flag, pos)
                    elif self.grid_state[i][j] == TileState.mine_visible:
                        self.game.screen.blit(mine, pos)

        # 显示左键按下效果
        if not self.over:
            x, y = self.pixel_to_grid(*pygame.mouse.get_pos())
            if self.is_in_grid(x, y):
                pygame.draw.rect(
                    self.game.screen,
                    'white',
                    pygame.Rect(
                        *self.grid_to_pixel((x - 1) if x > 0 else 0, (y - 1) if y > 0 else 0),
                        self.tile_size * ((x > 0) + (x < self.grid_size[0] - 1) + 1),
                        self.tile_size * ((y > 0) + (y < self.grid_size[1] - 1) + 1),
                    ),
                    2,
                )

        # update animations
        delete = set()
        for pos, (anim, offset) in self.anim_dict.items():
            pixel_pos = self.grid_to_pixel(*pos)
            anim.update(
                self.game.screen,
                (
                    pixel_pos[0] + round(offset[0] * self.tile_size - self.tile_size),
                    pixel_pos[1] + round(offset[1] * self.tile_size - self.tile_size)
                ),
                (self.tile_size * 2, self.tile_size * 2),
            )
            if anim.done:
                delete.add(pos)
        for key in delete:
            del self.anim_dict[key]
        del delete
