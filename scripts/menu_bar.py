import pygame
import pygame_gui


class MenuBar:
    def __init__(self, game):
        self.game = game

        self.default_height = 70
        self.height: int = 0
        self.border: int = 10

        self.button_new = pygame_gui.elements.UIButton(pygame.Rect(0, 0, 0, 0), 'New Game',
                                                       self.game.ui_manager, object_id='button_new')
        self.button_again = pygame_gui.elements.UIButton(pygame.Rect(0, 0, 0, 0), 'Play Again',
                                                         self.game.ui_manager, object_id='button_again')

    def update(self) -> None:
        screen_size: tuple[int, int] = self.game.screen.get_size()
        self.height = round(self.default_height * screen_size[1] / self.game.config['Graphics']['size'][1])

        # draw texts
        text_time: pygame.Surface = self.game.font.render(f'Time: {self.game.mine_table.game_time / 60:.3f}s',
                                                              True, 'white')
        text_time = pygame.transform.scale_by(text_time, self.height / 2 / text_time.get_size()[1])
        self.game.screen.blit(text_time, (
            (screen_size[0] - text_time.get_size()[0]) / 2, self.border
        ))
        text_mine: pygame.Surface = self.game.font.render(
            f'Mines Left: {self.game.mine_table.mine_total - self.game.mine_table.tile_flagged}'
            f'/{self.game.mine_table.mine_total}',
            True,
            'white',
        )
        text_mine = pygame.transform.scale_by(text_mine, self.height / 2 / text_mine.get_size()[1])
        self.game.screen.blit(text_mine, (
            (screen_size[0] - text_mine.get_size()[0]) / 2, self.border + self.height / 2
        ))

        # change the size and pos of buttons
        button_space = (screen_size[0] - max(text_time.get_size()[0], text_mine.get_size()[0])) / 2 - self.border
        self.button_new.set_dimensions((button_space * 2 / 7, self.height * 2 / 3))
        self.button_new.set_position((button_space * 4 / 35, self.border + self.height / 6))
        self.button_again.set_dimensions((button_space * 2 / 7, self.height * 2 / 3))
        self.button_again.set_position((button_space * 2 / 5 + self.border * 2, self.border + self.height / 6))
