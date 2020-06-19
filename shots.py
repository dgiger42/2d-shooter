import pygame
from colordict import THECOLORS
from time import time
from math import sqrt
from constants import *


class Shot(pygame.sprite.Sprite):

    def __init__(self, location, dimensions, velocity, colour):
        super().__init__()
        image_surface = pygame.surface.Surface(dimensions)
        image_surface.fill(colour)
        self.image = image_surface.convert()
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = location
        self.location = location
        self.velocity = [v_i * 30.0 / FRAMERATE for v_i in velocity]

    def move(self):
        self.location = [self.location[0] + self.velocity[0], self.location[1] + self.velocity[1]]
        self.rect.centerx, self.rect.centery = map(int, self.location)

    def isOffScreen(self):
        return self.rect.left > 1350 or self.rect.right < 0 or self.rect.top > 700 or self.rect.bottom < 0


class FollowShot(Shot):

    duration = 4

    def __init__(self, location, dimensions, velocity, target):
        super().__init__(location, dimensions, velocity, THECOLORS["yellow"])
        self.target = target
        self.timeFired = time()

    def aim(self):
        targetPos = self.target.location
        vec = [targetPos[0] - self.location[0], targetPos[1] - self.location[1]]
        dist = sqrt(vec[0] ** 2 + vec[1] ** 2)
        speed = sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        self.velocity = [component / dist * speed for component in vec]

    def move(self):
        self.aim()
        super().move()
