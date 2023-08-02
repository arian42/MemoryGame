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
    SHOW_PTR = 2
    GET_CLICK = 3
    GAME_OVER = 4

class obj():
    def __init__(self, rect, id):
        self.rect = rect
        self.time = 0
        self.clicked = False
        self.correct = False
        self.id = id

class Game():
    def __init__(self):
        # game size
        self.objects = []
        self.s_len = 50
        self.s_gap = 10
        self.grid = pygame.Vector2(3, 3)

        # color
        self.rect_base_color = (0, 10, 100)
        self.rect_active_color = (255, 255, 255)
        self.rect_wrong_color = (0, 30, 50)
        self.rect_correct_color = (10, 255, 10)

        # timings
        self.start_play_time = 0
        self.animation_duration = 400
        self.show_time = 600
        self.grace_time_before_level = 300

        # game modes
        self.game_mode = GameMode.WAIT_FOR_PLAYER
        self.level = 0
        self.no_of_obj = 2
        self.life = 3
        self.harts_per_level = 3

        # self.create_rects()

        if pygame.font:
            self.font = pygame.font.Font(None, 24)
        self.click = []

    def next_level(self):
        self.level += 1
        self.no_of_obj += 1
        if self.no_of_obj > self.grid.x * self.grid.y * 0.6:
            # it is greater than half
            if self.grid.x < self.grid.y:
                self.grid.x += 1
            else:
                self.grid.y += 1

        self.create_rects()
        # select bunch of random squres
        for i in random.sample(range(0, len(self.objects) - 1), self.no_of_obj):
            self.objects[i].correct = True

    def create_rects(self):
        self.objects = []
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
        for id, ob in enumerate(self.objects):
            if ob.clicked:
                if ob.correct:
                    pygame.draw.rect(screen, self.rect_active_color, ob)
                else:
                    pygame.draw.rect(screen, self.rect_wrong_color, ob)
            else:
                pygame.draw.rect(screen, self.rect_base_color, ob)

        l1 = self.font.render(f"Game mode: {self.game_mode}", True, 'white')
        l2 = self.font.render(f"level: {self.level}", True, 'white')
        l3 = self.font.render(f"start time: {self.start_play_time}", True, 'white')
        l4 = self.font.render(f"time: {pygame.time.get_ticks()}", True, 'white')
        l3 = self.font.render(f"life: {self.life}", True, 'white')
        screen.blit(l1, (0, 0))
        screen.blit(l2, (0, 25))
        screen.blit(l3, (0, 50))
        screen.blit(l4, (0, 75))
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
                        self.next_level()
                        self.start_play_time = pygame.time.get_ticks()
                        self.game_mode = GameMode.SHOW_PTR
                case GameMode.SHOW_PTR:
                    if pygame.time.get_ticks() - self.start_play_time > self.grace_time_before_level:
                        # show all rectangles
                        for ob in self.objects:
                            if ob.correct:
                                ob.clicked = True
                        if pygame.time.get_ticks() - self.start_play_time > self.grace_time_before_level + self.show_time:
                            # deactivate and start the game
                            for ob in self.objects:
                                if ob.correct:
                                    ob.clicked = False
                            self.game_mode = GameMode.GET_CLICK
                            self.click = []
                case GameMode.GET_CLICK:
                    if self.click:
                        ob_id = self.click.pop(0)
                        ob = self.objects[ob_id]
                        ob.clicked = True

                    fails = 0
                    for shape in self.objects:
                        if not shape.correct and shape.clicked:
                            fails += 1  # this counts the mistakes
                    if fails >= self.harts_per_level:
                        self.life -= 1
                        if self.life <= 0:
                            self.game_mode = GameMode.GAME_OVER
                        else:
                            for shape in self.objects:
                                shape.clicked = False
                            self.game_mode = GameMode.SHOW_PTR
                            self.start_play_time = pygame.time.get_ticks()

                    # check for win
                    for shape in self.objects:
                        if shape.correct and not shape.clicked:
                            break  # this checks if all corrects cells are selected
                    else:
                        # its a win !!!
                        self.next_level()
                        self.start_play_time = pygame.time.get_ticks()
                        self.game_mode = GameMode.SHOW_PTR
                case GameMode.GAME_OVER:
                    pass

            self.draw()
            clock.tick(60)

game = Game()
game.loop()
pygame.quit()
