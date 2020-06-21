import pygame
from colordict import THECOLORS
from constants import *
from random import randint
from math import degrees, atan2, cos, sin, radians, sqrt
from shots import Shot, FollowShot
from laser import Laser
from util import dist
import util


class Entity(pygame.sprite.Sprite):
    shots = []

    def __init__(self, dimensions, color, location, level):
        super().__init__()
        self.image_surface = pygame.surface.Surface(dimensions)
        self.image_surface.fill(color)
        self.image = self.image_surface.convert()
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.level = level

    def shootAngle(self, colour, theta, speed=3, dimensions=(10, 3)):
        velocity = [speed * cos(radians(theta)), speed * sin(radians(theta))]
        self.shots.append(Shot(self.rect.center, dimensions, velocity, colour))

    def shootTarget(self, endPoint, colour, speed=7, dimensions=(10, 3)):
        theta = degrees(atan2(endPoint[1] - self.rect.centery, endPoint[0] - self.rect.centerx))
        self.shootAngle(colour, theta, speed, dimensions)

    def shootGroup(self, colour, startAngle, angleBtwShots, noShots, speed=5, size=(10, 3)):
        for i in range(noShots):
            self.shootAngle(colour, startAngle - (i * angleBtwShots), speed, size)


class Player(Entity):
    shots = []
    MAX_LIVES = 5 if not DEBUG else 42

    def __init__(self):
        super().__init__([15, 15], THECOLORS["black"], [0, 0], 1)
        self.lives = self.MAX_LIVES
        self.invincible = False
        self.hasLaser = False

    def getHit(self):
        if not self.invincible:
            self.image_surface.fill([255, 100, 100])
            self.image = self.image_surface.convert()
            self.lives -= 1
            self.invincible = True
            pygame.time.set_timer(INVINC_EVENT, 1500)  # gives player 1.5 sec after hit

    def recolor(self):
        self.image_surface.fill([0, 0, 0])
        self.image = self.image_surface.convert()
        self.invincible = False
        pygame.time.set_timer(INVINC_EVENT, 0)

    def fire(self):
        nShots = self.level
        shotSpeed = 15
        if nShots == 1:
            self.shootAngle(THECOLORS["black"], -90, shotSpeed, (5, 5))
        else:
            spreadAngle = min(30, self.level * 5)
            angleBtwShots = spreadAngle / max(nShots - 1, 1)
            startAngle = -(90 - spreadAngle/2)
            self.shootGroup(THECOLORS["black"], startAngle, angleBtwShots, nShots, shotSpeed, size=[5, 5])

        #do laser
        if len(Foe.foes) > 0 and self.hasLaser:
            self.getTarget().hp -= .3

    def levelUp(self):
        self.level += 1
        if self.level >= (4 if not DEBUG else 2):
            self.hasLaser = True

    def getTarget(self):
        def key(foe):
            return (self.rect.centerx - foe.rect.centerx) ** 2 + (self.rect.centery - foe.rect.centery) ** 2
        return min(Foe.foes, key=key)

    def showLaser(self, screen):
        if len(Foe.foes) > 0 and self.hasLaser:
            pygame.draw.line(screen, THECOLORS["gold"], self.rect.center, self.getTarget().rect.center, 6)


class Foe(Entity):
    shots = []
    foes = []
    nextLevel = 0
    nextCanAim = True
    nFoes = 10 if not DEBUG else 30

    def __init__(self, level , canAim, target):
        self.size = [3 * level + 20] * 2
        super().__init__(self.size, [185, 0, 0], [randint(20, 1220), 0], level)
        self.location = self.rect.center
        self.velocity = [0, randint(70, 150) / FRAMERATE]
        self.maxHP = 2 + int(1.1 * level ** 1.4)
        self.hp = self.maxHP
        self.canAim = canAim
        self.goalPos = (self.rect.centerx, randint(1, 450))
        self.target = target
        self.alwaysMove = True

    @property
    def speed(self):
        return sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

    @staticmethod
    def addFoe(target):
        if Foe.nextLevel < Foe.nFoes:
            Foe.nextLevel += 1
            Foe.foes.append(Foe(Foe.nextLevel, Foe.nextCanAim, target))
            Foe.nextCanAim = not Foe.nextCanAim
        elif not Boss.defeated and len(Foe.foes) == 0:
            Foe.foes.append(Boss(target))

    def updatePos(self):
        """moves foe and makes it stop at its goal"""
        while dist(self.goalPos, self.rect.center) <= 1 + self.speed and self.alwaysMove:
            self.goalPos = (randint(20, 1200), randint(1, 450))

        if dist(self.goalPos, self.rect.center) > 1 + self.speed:
            dx = self.goalPos[0] - self.rect.centerx
            dy = self.goalPos[1] - self.rect.centery
            mag = sqrt(dx ** 2 + dy ** 2)
            self.velocity = [self.speed * dx / mag, self.speed * dy / mag]
            util.move(self)

    def show(self, screen):
        screen.blit(self.image, self.rect)
        x = self.rect.left
        y = self.rect.bottom + 4
        width = self.rect.right - self.rect.left
        hpRatio = (float(self.hp) / float(self.maxHP))
        pygame.draw.rect(screen, THECOLORS["red"], [[x, y], [int(hpRatio * width), 10]])

    def fire(self):
        if self.canAim:
            self.shootTarget(self.target.rect.center, THECOLORS["blue"])
        else:
            nShots = 5 + int(self.level ** .6)
            self.shootGroup(THECOLORS["red"], randint(1, 360), (360 / nShots), nShots)


class Boss(Foe):
    defeated = False

    def __init__(self, target):
        super().__init__(80, False, target)
        pygame.time.set_timer(FOE_SHOOT_EVENT, 100)
        self.hp = self.maxHP = 1100 if not DEBUG else 100
        self.attackIntervals = (-1, 100, 300, 400, 1000)  # timers for each attack
        self.attacks = (self.laserAttack, self.spiralAttack, self.attack2, self.attack3, self.wallOfDeath)
        self.shotAngle = 0
        self.shotIncrement = 5.32
        self.rect.center = self.location = [700, 0]
        self.curAttackNum = 0
        self.laser = None
        self.alwaysMove = False
        self.goalPos = (self.rect.centerx, 220)

    @property
    def numAttacks(self):
        return len(self.attacks)

    def show(self, screen):
        super().show(screen)
        if self.laser:
            self.laser.show(screen)

    def updatePos(self):
        super().updatePos()
        if self.laser:
            self.laser.move(self.rect.center)

    def fire(self):
        hpLost = self.maxHP - self.hp
        if hpLost > (1 + self.curAttackNum) * (self.maxHP / self.numAttacks):
            self.curAttackNum += 1
            self.laser = None
            Foe.shots = []
            pygame.time.set_timer(FOE_SHOOT_EVENT, self.attackIntervals[self.curAttackNum])
        self.attacks[self.curAttackNum]()

    def laserAttack(self):
        if not self.laser:
            self.laser = Laser(self.rect.center, self.target)


    def spiralAttack(self):
        nShots = 7
        self.shotAngle += self.shotIncrement
        if abs(self.shotAngle) > 50:
            self.shotIncrement *= -1
        self.shootGroup(THECOLORS["red"], self.shotAngle, 360 / nShots, nShots, 10, [20, 4])

    def attack2(self):
        speed = 8
        self.shootTarget(self.target.rect.center, THECOLORS["blue"], speed)
        nShots = 4
        speed = 15
        size = [5, 40]
        self.shootGroup(THECOLORS["red"], self.shotAngle, 360 / nShots, nShots, speed, size)
        self.shotAngle += 15

    def attack3(self):
        speed = randint(4, 8)
        Foe.shots.append(FollowShot(self.rect.center, [10,3], [speed, 0], self.target))
        size = [30, 5]
        nShots = 4
        speed = 15
        self.shootGroup(THECOLORS["red"], self.shotAngle, 360 / nShots, nShots, speed, size)
        self.shotAngle += 15

    def wallOfDeath(self):
        nShots = 20
        for i in range(3):
            self.shotAngle += 120
            self.shootGroup(THECOLORS["red"], self.shotAngle, 120 / (nShots + 2), nShots, 15, [30, 4])
        self.shotAngle += randint(1, 120)
