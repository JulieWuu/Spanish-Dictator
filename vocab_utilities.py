import pygame
import math
import os
pygame.init()


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.state = False

    def draw(self, window, offset=0):
        window.blit(self.image, (self.rect.x, self.rect.y - offset))

    def pressed(self):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                self.state = not self.state
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action


class DragPoint:
    def __init__(self, pos, radius=7):
        self.x, self.y = pos
        self.radius = radius
        self.drag = False

    def draw(self, window, offset):
        pygame.draw.circle(window, (0, 0, 0), (self.x, self.y - offset), self.radius)

    def distance(self, pos):
        return math.sqrt((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2)


class SoundTrack:
    def __init__(self, length, handle_pos, current=0):
        self.length = length    # in seconds
        self.minute = int(self.length // 60)
        self.second = self.length - 60 * self.minute
        self.current = current  # in seconds
        self.current_min = int(self.current // 60)
        self.current_sec = self.current - 60 * self.current_min
        self.loaded = False
        self.pos = 0    # start off position in float seconds, updated when dragging the handle or pausing
        self.handle_pos = handle_pos

        self.handle = DragPoint(handle_pos)

    def show_update(self, window, offset, len_pos, cur_pos):
        self.current_min = int(self.current // 60)
        self.current_sec = self.current - 60 * self.current_min

        length_text = pygame.font.SysFont("Consolas", 24).render(
            f"{self.minute}:{self.second}" if self.second >= 10 else f"{self.minute}:0{self.second}", False, (0, 0, 0))
        current_text = pygame.font.SysFont("Consolas", 24).render(
            f"{self.current_min}:{self.current_sec}" if self.current_sec >= 10 else f"{self.current_min}:0{self.current_sec}", False, (0, 0, 0))

        window.blit(length_text, (len_pos[0], len_pos[1] - offset))
        window.blit(current_text, (cur_pos[0], cur_pos[1] - offset))


def load_audio_paths(path):
    audios = []
    # list of Sound objects
    for audio in sorted(os.listdir("spanish_assets/" + path)):
        audios.append("spanish_assets/" + path + "/" + audio)
    return audios


# which groups should I revise today
def select(groups, day, repeat=10):
    answer = []

    # maximum occurring times for each group
    for i in range(repeat):
        for group in sorted(groups):
            if group == str(day - int(0.25 * i ** 2)):
                if group not in answer:
                    answer.append(group)

    return answer
