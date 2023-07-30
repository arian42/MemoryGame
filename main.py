# Example file showing a circle moving on screen
import pygame
from itertools import product
from enum import Enum
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

class GameMode(Enum):
    QUIT = 0
    WAIT_FOR_PLAYER = 1
    SHOW_SEQ = 2
    GET_CLICK = 3
    GAME_OVER = 4

class obj():
    def __init__(self, rect, id):
        self.rect = rect
        self.time = 0
        self.id = id

class Game():
    def __init__(self):
        self.objects = []
        self.running = True
        self.s_len = 50
        self.s_gap = 10
        self.grid = pygame.Vector2(4, 4)

        self.rect_color = (0, 10, 100)
        self.rect_active_color = (255, 255, 255)

        self.animation_duration = 300
        self.time_between_struck = 600

        self.game_mode = GameMode.WAIT_FOR_PLAYER
        self.seq = []
        self.counter = 0
        self.start_play_time = 0

        self.create_rects()

        if pygame.font:
            self.font = pygame.font.Font(None, 24)
        self.click = []


    def create_rects(self):
        center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        starting_point = pygame.Vector2(0, 0)
        starting_point.x = center.x - self.grid.x / 2 * (self.s_len + self.s_gap)
        starting_point.y = center.y - self.grid.y / 2 * (self.s_len + self.s_gap)
        for id, (x, y) in enumerate(product(range(int(self.grid.x)), range(int(self.grid.y)))):
            rect_x = starting_point.x + x * (self.s_len + self.s_gap)
            rect_y = starting_point.y + y * (self.s_len + self.s_gap)
            r = pygame.Rect(rect_x, rect_y, self.s_len, self.s_len)
            self.objects.append(obj(r, id))

    def flash_cells(self):
        t = pygame.time.get_ticks()
        for ob in self.objects:
            ob.time = t

    def color_update_curve(self, color_a, color_b, current_time_delta):
        if current_time_delta > self.animation_duration:
            return color_b
        # for bezier time or x axise is range from 0 to 1
        t = current_time_delta / self.animation_duration

        # also the v value or y axies is ranged from 0 to 1
        v = t * t * (3.0 - 2.0 * t)  # Bezier fourmula

        color = [0, 0, 0]
        for i in range(3):
            # convert the colors
            color[i] = round(color_a[i] + v * (color_b[i] - color_a[i]))
        return tuple(color)



    def draw(self):
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")
        time = pygame.time.get_ticks()
        for id, ob in enumerate(self.objects):
            color = self.color_update_curve(self.rect_active_color, self.rect_color, time - ob.time)
            pygame.draw.rect(screen, color, ob)

        l1 = self.font.render(f"Game mode: {self.game_mode}", True, 'white')
        l2 = self.font.render(f"SEQ len: {len(self.seq)}", True, 'white')
        l3 = self.font.render(f"counter: {self.counter}", True, 'white')
        screen.blit(l1, (0, 0))
        screen.blit(l2, (0, 25))
        screen.blit(l3, (0, 50))

        # flip() the display to put your work on screen
        pygame.display.flip()


    def loop(self):
        while self.game_mode is not GameMode.QUIT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_mode = GameMode.QUIT
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for id, ob in enumerate(self.objects):
                        if ob.rect.collidepoint(event.pos):
                            self.click.append(id)
            match self.game_mode:
                case GameMode.WAIT_FOR_PLAYER:
                    if pygame.time.get_ticks() - self.start_play_time > 1000:
                        new_cell = random.randint(0, len(self.objects)-1)
                        self.seq.append(new_cell)
                        self.start_play_time = pygame.time.get_ticks()
                        self.game_mode = GameMode.SHOW_SEQ
                case GameMode.SHOW_SEQ:
                    if self.counter < len(self.seq):
                        t1 = pygame.time.get_ticks()
                        if t1 - self.start_play_time >= (self.counter + 1) * self.time_between_struck:
                            self.objects[self.seq[self.counter]].time = t1
                            self.counter += 1
                    else:
                        # if pygame.time.get_ticks() - start_play_time >= counter * time_between_struck:
                        #     flash_cell()
                        self.counter = 0
                        self.click = []
                        self.game_mode = GameMode.GET_CLICK
                case GameMode.GET_CLICK:
                    if self.counter >= len(self.seq):
                        self.game_mode = GameMode.SHOW_SEQ
                        continue
                    if self.click:
                        ob_id = self.click.pop(0)
                        self.objects[ob_id].time = pygame.time.get_ticks()
                        if ob_id == self.seq[self.counter]:
                            # correct
                            self.counter += 1
                            if self.counter >= len(self.seq):
                                self.game_mode = GameMode.SHOW_SEQ
                                new_cell = random.randint(0, len(self.objects) - 1)
                                self.start_play_time = pygame.time.get_ticks()
                                self.seq.append(new_cell)
                                self.counter = 0
                        else:
                            self.counter = 0
                            self.game_mode = self.game_mode.GAME_OVER
                case GameMode.GAME_OVER:
                    self.objects[random.randint(0, len(self.objects)-1)].time = pygame.time.get_ticks()

            self.draw()
            clock.tick(60)

game = Game()
game.loop()
pygame.quit()
