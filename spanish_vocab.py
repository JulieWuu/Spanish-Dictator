import pygame
import random
import time
from vocab_utilities import Button, SoundTrack, load_audio_paths, select

pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_mode((626, 417))

background = pygame.image.load("spanish_assets/background.jpg").convert()
background.set_alpha(180)
play_img = pygame.image.load("spanish_assets/buttons/black_play.png")
play_img.set_colorkey((255, 255, 255))
play_img.convert_alpha()


class Dictator:
    def __init__(self, days):
        self.screen = pygame.display.set_mode((626, 417))
        pygame.display.set_caption("Spanish_Vocab")
        self.clock = pygame.time.Clock()
        self.days = days
        self.audio_paths = load_audio_paths("audios")   # list of file names

        # {int (number of learnt day): [files of audio] (ESP & ENG)}
        self.all_words = {}     # for "select" calculation, ESP/ ENG choice
        self.assets = {"background": background,
                       "audios": [pygame.mixer.Sound(path) for path in self.audio_paths],  # list of Sound objects
                       }

        # load audios into all_words, two audios per group number
        for i in range(len(self.audio_paths)):
            key = str(i // 2 + 1)
            if key not in self.all_words:
                self.all_words[key] = []
            self.all_words[key].append(self.audio_paths[i])

        self.play_button = []   # gets its length from audio_of_today, has standard length for many other objects
        self.soundtracks = []   # controls time display and drag points

        self.start_time = 0.0
        self.offset = 0

    def window_update(self):
        self.screen.fill((100, 100, 100))
        self.screen.blit(background, (0, 0))

        title = pygame.font.SysFont("Consolas", 60).render("Spanish Dictator", False, (0, 0, 0))
        self.screen.blit(title, (50, 30 - self.offset))
        guide = pygame.font.SysFont("Consolas", 40).render("revise day " + str(self.days), False, (0, 0, 0))
        self.screen.blit(guide, (180, 100 - self.offset))

        for button in self.play_button:
            button.draw(self.screen)
        for rect in [pygame.Rect(185, 191 + 80 * i - self.offset, 300, 5) for i in range(len(self.play_button))]:
            pygame.draw.rect(self.screen, (0, 0, 0), rect)
        for soundtrack in self.soundtracks:
            soundtrack.handle.draw(self.screen, self.offset)

        # updating length and current pos of the soundtrack
        for i in range(len(self.play_button)):
            self.soundtracks[i].show_update(self.screen, self.offset, (500, 183 + 80 * i), (120, 183 + 80 * i))

    def run(self):
        audio_of_today = []     # list of displayed audios
        for seq in select(self.all_words, self.days):
            audio_of_today.append(random.choice(self.all_words[seq]))   # for every selected day, choose from ENG/ ESP

        # only load length and current pos of audios of today
        for i, audio in enumerate([pygame.mixer.Sound(audio) for audio in audio_of_today]):
            self.soundtracks.append(SoundTrack(round(audio.get_length()), (185, 193 + 80 * i)))

        self.play_button = [Button(40, 165 + 80 * i, play_img, 0.25) for i in range(len(audio_of_today))]

        while True:

            for i, play_button in enumerate(self.play_button):
                # update only when playing
                if play_button.state:
                    elapsed_time = time.time() - self.start_time
                    self.soundtracks[i].current = round(elapsed_time + self.soundtracks[i].pos)

            for i, soundtrack in enumerate(self.soundtracks):
                if soundtrack.handle.drag and soundtrack.loaded:
                    soundtrack.handle.x = min(max(pygame.mouse.get_pos()[0], 185), 485)
                    soundtrack.current = (soundtrack.handle.x - 185) * soundtrack.length // 300
                else:
                    soundtrack.handle.x = 185 + 300 * soundtrack.current / soundtrack.length

            for i in range(len(self.play_button)):  # checking every line individually
                if not self.play_button[i].state and self.play_button[i].pressed():
                    if self.soundtracks[i].loaded:
                        pygame.mixer.music.unpause()
                        self.play_button[i].state = True
                        self.start_time = time.time()
                    else:
                        pygame.mixer.music.load(audio_of_today[i])
                        self.soundtracks[i].loaded = True   # variable to monitor whether to pause or load
                        pygame.mixer.music.play()
                        pygame.mixer.music.set_pos(self.soundtracks[i].pos)
                        self.play_button[i].state = True    # variable to monitor whether it is playing

                        for soundtrack in self.soundtracks[:i] + self.soundtracks[i + 1:]:
                            soundtrack.loaded = False   # updating play state for the rest
                            soundtrack.pos = (soundtrack.handle.x - 185) * soundtrack.length / 300
                        for button in self.play_button[:i] + self.play_button[i + 1:]:
                            button.state = False

                        self.start_time = time.time()   # start timing for showing current soundtrack pos

                elif self.play_button[i].state and self.play_button[i].pressed():
                    pygame.mixer.music.pause()
                    self.soundtracks[i].pos = (self.soundtracks[i].handle.x - 185) * self.soundtracks[i].length / 300
                    self.play_button[i].state = False

                if self.soundtracks[i].current > self.soundtracks[i].length:
                    pygame.mixer.music.stop()
                    self.play_button[i].state = False
                    self.soundtracks[i].loaded = False
                    self.soundtracks[i].current = 0
                    self.soundtracks[i].pos = 0

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = list(pygame.mouse.get_pos())
                    mouse_pos[1] += self.offset
                    if event.button == 4 and self.offset >= -100:
                        for button in self.play_button:
                            button.rect.y += 20
                        self.offset -= 20
                    if event.button == 5 and self.offset <= 80 * len(self.play_button) - 80:
                        self.offset += 20
                        for button in self.play_button:
                            button.rect.y -= 20

                    for soundtrack in self.soundtracks:
                        if soundtrack.handle.distance(mouse_pos) <= soundtrack.handle.radius and event.button == 1:
                            soundtrack.handle.drag = True

                if event.type == pygame.MOUSEBUTTONUP:
                    for soundtrack in self.soundtracks:
                        if soundtrack.handle.drag and event.button == 1:
                            soundtrack.handle.drag = False
                            soundtrack.pos = soundtrack.current
                            if soundtrack.loaded:
                                pygame.mixer.music.rewind()
                                pygame.mixer.music.set_pos(soundtrack.current)
                                self.start_time = time.time()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.window_update()
            pygame.display.update()
            self.clock.tick(60)


Dictator(6).run()
