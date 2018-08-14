from math import atan2, sin, cos, pi, radians, degrees
import pygame
from colordict import THECOLORS
from constants import *

class Laser():

    def __init__(self, startPoint, target, direction = 90):
        self.startPoint = startPoint
        self.target = target
        self.direction = direction
        self.color = THECOLORS["violetred"][:2] + (100,)
        self.rotateSpeed = 1.0 * 30 / FRAMERATE
        self.deathAngle = 3.5 #degrees

    def show(self, screen):
        n = 10000
        directionRadians = radians(self.direction)
        endPoint = self.startPoint[0] + n * cos(directionRadians), self.startPoint[1] + n * sin(directionRadians)
        pygame.draw.line(screen, self.color, self.startPoint, endPoint, 8)
        # pygame.draw.aaline(screen, self.color, self.startPoint, endPoint)

    def move(self, startPoint):  #collision detection - check if the angles are the same
        self.startPoint = startPoint
        targetPoint = self.target.location
        y = targetPoint[1] - startPoint[1]
        x = targetPoint[0] - startPoint[0]
        targetDirection = (degrees(atan2(y, x)) + 360) % 360

        directionDif = (targetDirection - self.direction) % 360
        if directionDif > 180:
            directionDif -= 360

        if directionDif > self.rotateSpeed:
            self.direction += self.rotateSpeed
        elif directionDif < -self.rotateSpeed:
            self.direction -= self.rotateSpeed
        else:
            self.direction = targetDirection
        self.direction %= 360
        if abs(self.direction - targetDirection) < self.deathAngle:
            self.target.getHit()