import sys

import pygame
import pygame_gui

from scripts.menu_bar import MenuBar
from scripts.mine_table import MineTable2D
from scripts.utils import ConfigManager, load_images, load_sounds


class Game:
    def __init__(self):
        self.config = ConfigManager('data/config.json')
        self.data = ConfigManager('./data/game.dat')
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        pygame.display.set_caption(self.config['Graphics']['caption'])
        pygame.display.set_icon(pygame.image.load('./data/images/' + self.config['Graphics']['icon']))
        self.screen = pygame.display.set_mode(
            self.config['Graphics']['size'],
            pygame.DOUBLEBUF | pygame.RESIZABLE,
        )
        self.clock = pygame.time.Clock()
        self.fps = self.config['Graphics']['fps']
        self.ui_manager = pygame_gui.UIManager(self.config['Graphics']['size'])

        self.assets = {
            'background': pygame.image.load('./data/images/background.png').convert(),
            'tile': pygame.image.load('./data/images/tile.png').convert_alpha(),
            'flag': pygame.image.load('./data/images/flag.png').convert_alpha(),
            'mine': pygame.image.load('./data/images/mine.png').convert_alpha(),
            'explosion': load_images('explosion'),
        }
        self.sfx = {
            'explode': load_sounds('explode', 0.75)
        }
        self.font = pygame.font.Font('./data/Mojangles.ttf', 512)

        self.mine_table = MineTable2D(self, self.data['size'], self.data['mines'])
        self.menu_bar = MenuBar(self)

    def check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.data.write()
                pygame.mixer.quit()
                pygame.font.quit()
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.mine_table.right_clicked_on(event.pos)
                elif event.button == 2:
                    self.mine_table.wheel_clicked_on(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mine_table.left_clicked_on(event.pos)
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == 'button_new':
                    self.mine_table.restart()
                elif event.ui_object_id == 'button_again':
                    self.mine_table.restart(False)
            self.ui_manager.process_events(event)

    def run(self) -> None:
        # main loop
        while True:
            time_delta = self.clock.tick(self.fps) / 1000

            # draw background
            self.screen.fill('black')
            for i in range(0, self.screen.get_size()[0], self.assets['background'].get_size()[0]):
                for j in range(0, self.screen.get_size()[1], self.assets['background'].get_size()[1]):
                    self.screen.blit(self.assets['background'], (i, j))
            self.ui_manager.draw_ui(self.screen)

            self.mine_table.update()
            self.menu_bar.update()
            self.ui_manager.update(time_delta)

            self.check_events()

            pygame.display.flip()


if __name__ == '__main__':
    Game().run()
