import pygame
from math import cos, sin, radians, degrees, atan2
from colordict import THECOLORS
from time import time
from math import sqrt
from constants import *


class Shot(pygame.sprite.Sprite):

    def __init__(self, location, dimensions, velocity, colour):
        pygame.sprite.Sprite.__init__(self)
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


class FollowShot(Shot):

    duration = 4

    def __init__(self, location, dimensions, velocity, target):
        Shot.__init__(self, location, dimensions, velocity, THECOLORS["yellow"])
        self.target = target
        self.firedTime = time()

    def aim(self):
        targetPos = self.target.location
        v = [targetPos[0] - self.location[0], targetPos[1] - self.location[1]]
        size = sqrt(v[0] ** 2 + v[1] ** 2)
        speed = sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        self.velocity = [v[i] / size * speed for i in range(len(v))]

    def move(self):
        self.aim()
        super(FollowShot, self).move()