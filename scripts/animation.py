import pygame


class SimpleAnimation:
    def __init__(self, frames: list[pygame.Surface], img_dur: int, loop: bool = False):
        self.img_dur = img_dur
        self.frame_count: int = 0
        self.frames = frames
        self.loop = loop
        self.done = False

    def scale_by(self, scale: float):
        self.frames = [pygame.transform.scale_by(frame, scale) for frame in self.frames]
        return self

    def update(self, screen: pygame.Surface, pos: tuple[int, int] | pygame.Rect,
               size: tuple[int, int] | float = 1.0) -> None:
        if self.loop:
            self.frame_count = (self.frame_count + 1) % (len(self.frames) * self.img_dur)
        else:
            if not self.done and self.frame_count < len(self.frames) * self.img_dur - 1:
                self.frame_count += 1
                if self.frame_count == len(self.frames) * self.img_dur - 1:
                    self.done = True


class Explosion(SimpleAnimation):
    def update(self, screen: pygame.Surface, pos: tuple[int, int] | pygame.Rect,
               size: tuple[int, int] | float = 1.0) -> None:
        super().update(screen, pos, size)
        frame = self.frames[self.frame_count // self.img_dur]
        if isinstance(size, tuple):
            frame = pygame.transform.scale(frame, size)
        elif (isinstance(size, float) or isinstance(size, int)) and size != 1:
            frame = pygame.transform.scale_by(frame, size)
        screen.blit(frame, pos)
