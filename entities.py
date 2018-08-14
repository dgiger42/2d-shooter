import pygame
from colordict import THECOLORS
from constants import *
from random import randint
from math import degrees, atan2, cos, sin, radians
from shots import Shot, FollowShot
from laser import Laser


class Entity(pygame.sprite.Sprite):

    def __init__(self, dimensions, color, location, level):
        pygame.sprite.Sprite.__init__(self)
        self.image_surface = pygame.surface.Surface(dimensions)
        self.image_surface.fill(color)
        self.image = self.image_surface.convert()
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.location = location
        self.level = level

    def shootAngle(self, colour, theta, speed=3, dimensions=[10, 3]):
        velocity = [speed * cos(radians(theta)), speed * sin(radians(theta))]
        self.shots.append(Shot(self.location, dimensions, velocity, colour))

    def shootTarget(self, endPoint, colour, speed = 7, dimensions = [10,3]):
        theta = degrees(atan2(endPoint[1] - self.location[1], endPoint[0] - self.location[0]))
        self.shootAngle(colour, theta, speed, dimensions)

    def shootGroup(self, colour, startAngle, angleBtwShots, noShots, speed = 5, size=[10, 3]):
        for i in range(noShots):
            # Shot.shootAngle(shotList, startPoint, colour, startAngle - (i * (angleBtwShots)), speed, size)
            self.shootAngle(colour, startAngle - (i * angleBtwShots), speed, size)


class Player(Entity):
    shots = []

    def __init__(self):
        Entity.__init__(self, [15, 15], THECOLORS["black"], [0,0], 1)
        self.lives = 6
        pygame.time.set_timer(USEREVENT + 2, 400)  # bob's shot timer
        self.invincible = False
        self.hasLaser = False

    def getHit(self):
        if not self.invincible:
            self.image_surface.fill([255, 100, 100])
            self.image = self.image_surface.convert()
            self.lives -= 1
            self.invincible = True
            pygame.time.set_timer(USEREVENT + 1, 1500)  # gives player 1.5 sec after hit

    def recolor(self):
        self.image_surface.fill([0, 0, 0])
        self.image = self.image_surface.convert()
        self.invincible = False
        pygame.time.set_timer(USEREVENT + 1, 0)  # bob invincibility timer

    def fire(self, screen):
        nShots = self.level
        spreadAngle = 40 - int(30/ pow(self.level, .4))
        angleBtwShots = spreadAngle / float(nShots + 1)
        # self.shootGroup(THECOLORS["black"], -75, 3, 11, 15) #original shooting
        self.shootGroup(THECOLORS["black"], -((90 - spreadAngle/2) + angleBtwShots), angleBtwShots, nShots, 15, size = [5, 5])
        self.laserAttack(screen)

    def levelUp(self):
        self.level += 1
        if self.level == 4:
            self.hasLaser = True

    def showLaser(self, screen):
        if len(Foe.foes) > 0 and self.hasLaser:
            pygame.draw.line(screen, THECOLORS["gold"], self.location, Foe.foes[0].location, 6)

    def laserAttack(self, screen):
        if len(Foe.foes) > 0 and self.hasLaser:
            Foe.foes[0].hp -= .1




class Foe(Entity):
    shots = []
    foes = []
    nextLevel = 0
    nextCanAim = True
    nFoes = 10

    def __init__(self, level , canAim, target):
        self.size = [3 * level + 20] * 2
        Entity.__init__(self, self.size, [200,0,0], [randint(20, 1200), 0], level)
        self.yLimit = randint(1, 450)  # sets place where foe stops moving
        self.speed =  [0, 1 + randint(1,7) * 30 / FRAMERATE]
        self.maxHP = level + 2  #the right one
        # self.maxHP = level/3 + 1
        self.hp = self.maxHP
        self.canAim = canAim
        self.target = target

    @staticmethod
    def addFoe(target):
        if Foe.nextLevel < Foe.nFoes:
            Foe.nextLevel += 1
            Foe.foes.append(Foe(Foe.nextLevel, Foe.nextCanAim, target))
            Foe.nextCanAim = not Foe.nextCanAim
        elif not Boss.defeated and len(Foe.foes) == 0:
            Foe.foes.append(Boss(target))

    def updatePos(self):
        '''moves foe and makes it stop at its yLimit'''
        if self.location[1] < self.yLimit:
            self.location[0] += self.speed[0]
            self.location[1] += self.speed[1]
            self.rect = self.rect.move(self.speed)

    def show(self, screen):
        screen.blit(self.image, self.rect)
        x = self.rect.left
        y = self.rect.bottom + 4
        width = self.rect.right - self.rect.left
        hpRatio = (float(self.hp) / float(self.maxHP))
        pygame.draw.rect(screen, THECOLORS["red"], [[x, y], [int(hpRatio * width), 10]])

    def fire(self):
        if self.canAim:
            # Shot.shootTarget(Foe.shots, self.location, self.target.location, THECOLORS["blue"])
            self.shootTarget(self.target.location, THECOLORS["blue"])
        else:
            nShots = 5 + int(self.level ** .6)
            self.shootGroup(THECOLORS["red"], randint(1, 360), (360 / nShots), nShots)
            # Shot.shootGroup(Foe.shots, THECOLORS["red"], self.location, randint(1, 360), (360 / nShots), nShots)


class Boss(Foe):
    defeated = False

    def __init__(self, target):
        Foe.__init__(self, 80, False, target)
        pygame.time.set_timer(FOE_SHOT_TIMER, 100)
        self.hp = self.maxHP = 200  # should be more ###################################################################
        self.attackIntervals = (100000, 100, 300, 400, 1000) # timers for each attack
        self.attacks = (self.laserAttack, self.attack1, self.attack2, self.attack3, self.attack4)
        self.numAttacks = len(self.attacks)
        self.shotAngle = 0
        self.shotIncrement = 5.32
        self.rect.centerx, self.rect.centery = self.location = [700, 0]
        self.yLimit = 210
        self.curAttackNum = 0
        self.laser = None

    def switchAttacks(self):
        self.curAttackNum += 1
        self.laser = None
        Foe.shots = []
        pygame.time.set_timer(FOE_SHOT_TIMER, self.attackIntervals[self.curAttackNum])
        self.fire()

    def show(self, screen):
        super(Boss, self).show(screen)
        if self.laser:
            self.laser.show(screen)

    def updatePos(self):
        super(Boss, self).updatePos()
        if self.laser:
            self.laser.move(self.location)

    def fire(self):
        self.attacks[self.curAttackNum]()

    def laserAttack(self):
        if not self.laser:
            self.laser = Laser(self.location, self.target)

    def attack1(self):
        nShots = 7
        self.shotAngle += self.shotIncrement
        if abs(self.shotAngle) > 50:
            self.shotIncrement *= -1
        self.shootGroup(THECOLORS["red"], self.shotAngle, 360 / nShots, nShots, 10, [20, 4])

    def attack2(self):
        speed = 8
        self.shootTarget(self.target.location, THECOLORS["blue"], speed)
        nShots = 4
        speed = 15
        size = [5, 40]
        self.shootGroup(THECOLORS["red"], self.shotAngle, 360 / nShots, nShots, speed, size)
        self.shotAngle += 15

    def attack3(self):
        speed = randint(4, 8)
        Foe.shots.append(FollowShot(self.location, [10,3], [speed, 0], self.target))
        size = [30, 5]
        nShots = 4
        speed = 15
        self.shootGroup(THECOLORS["red"], self.shotAngle, 360 / nShots, nShots, speed, size)
        self.shotAngle += 15

    def attack4(self):
        nShots = 20
        for i in xrange(3):
            self.shotAngle += 120
            # Shot.shootGroup(Foe.shots, THECOLORS["red"], self.location, self.shotAngle, 120 / (nShots + 2), nShots, 15, [30, 4])
            self.shootGroup(THECOLORS["red"], self.shotAngle, 120 / (nShots + 2), nShots, 15, [30, 4])
        self.shotAngle += randint(1, 120)