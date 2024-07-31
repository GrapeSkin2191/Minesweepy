import json
import os
from pathlib import Path

import pygame


class ConfigManager:
    def __init__(self, path: Path | str):
        self.path = path if isinstance(path, Path) else Path(path)
        self.data: dict = json.loads(self.path.read_text('utf-8'))

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def write(self):
        self.path.write_text(json.dumps(self.data), 'utf-8')


def load_images(name: str, scale: tuple[int, int] | float = 1.0) -> list[pygame.Surface]:
    path = Path('./data/images') / name
    file_list = os.listdir(path)
    result_list = []
    for i in range(len(file_list)):
        result_list.append(pygame.image.load(path / f'{name}_{i}.png').convert_alpha())
        if isinstance(scale, tuple):
            result_list[-1] = pygame.transform.scale(result_list[-1], scale)
        elif (isinstance(scale, float) or isinstance(scale, int)) and scale != 1:
            result_list[-1] = pygame.transform.scale_by(result_list[-1], scale)
    return result_list


def load_sounds(name: str, volume: float = 1.0) -> list[pygame.mixer.Sound]:
    path = Path('./data/sounds') / name
    file_list = os.listdir(path)
    result_list = []
    for i in range(len(file_list)):
        result_list.append(pygame.mixer.Sound(path / f'{name}{i}.ogg'))
        result_list[-1].set_volume(volume)
    return result_list
