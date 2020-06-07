from colordict import THECOLORS
import pygame
from math import atan2, cos, sin, radians, degrees, sqrt
from random import randint
from shots import FollowShot, Shot
from time import time
from entities import *
from constants import *


def doCollisions():
    if pygame.sprite.spritecollideany(bob, Foe.shots) or pygame.sprite.spritecollide(bob, Foe.foes, False):
        bob.getHit()
    for foe in Foe.foes:
        if pygame.sprite.spritecollideany(foe, Player.shots):
            foe.hp -= 1
            if type(foe) is Boss and int(foe.hp) in (foe.maxHP * i // foe.numAttacks for i in range(1, foe.numAttacks)):  #switch attacks
                foe.switchAttacks()
        if foe.hp <= 0:
            if type(foe) is Boss:
                Boss.defeated = True
            Foe.foes.remove(foe)
            bob.levelUp()
    Player.shots = [shot for shot in Player.shots if not pygame.sprite.spritecollideany(shot, Foe.foes)]


def animate():
    screen.fill([200, 200, 255])
    # pygame.draw.line(screen, THECOLORS["red"], (0,0), (300,300), 30)
    for i in range(bob.lives):
        screen.blit(bob.image, [1280 - (30 * i), 30])
    if len(Foe.foes) > 0:
        bob.showLaser(screen)
    for foe in Foe.foes:  # move foes, draw along w/ health bars
        foe.updatePos()
        foe.show(screen)
    for shot in Player.shots + Foe.shots:
        shot.move()
        screen.blit(shot.image, shot.rect)
    if Boss.defeated:
        showWinMsg()
        Foe.shots = []
    screen.blit(bob.image, bob.rect)
    pygame.display.flip()

def removeDeadShots():  #has bug - doesn't kill ALL of the shots that are offscreen
    '''stop moving shots if they're off the screen or past duration'''
    for shot in Player.shots:
        if shot.rect.left > 1350 or shot.rect.right < 0 \
                or shot.rect.top > 700 or shot.rect.bottom < 0:
            Player.shots.remove(shot)
    for shot in Foe.shots:
        if shot.rect.left > 1350 or shot.rect.right < 0 \
                or shot.rect.top > 700 or shot.rect.bottom < 0 \
                or (type(shot) is FollowShot and time() - shot.firedTime > FollowShot.duration):
            Foe.shots.remove(shot)


def showWinMsg():
    fontSize = pygame.font.Font(None, 300)  # sets fontSize
    winMsg = fontSize.render('YOU WON!!!', 1, THECOLORS["white"])
    screen.blit(winMsg, [20, 100])

def initGame():
    global screen, clock, bob

    pygame.init()
    width, height = 1300, 680  # sets window size to 1300, 680
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    screen.fill([170, 170, 250])
    bob = Player()

def start():
    pygame.time.set_timer(FOE_ENTER_EVENT, FOE_INTERVAL)  # sets time between foe entry
    pygame.time.set_timer(FOE_SHOOT_EVENT, 500)
    Foe.addFoe(bob)


if __name__ == "__main__":
    initGame()
    running = True
    started = False


    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                started = True
                start()
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:  # move
                bob.rect.centerx, bob.rect.centery = bob.location = event.pos
            if started:
                if event.type == INVINC_EVENT:  # bob invincible timer
                    bob.recolor()
                elif event.type == BOB_SHOOT_EVENT:
                    bob.fire(screen)
                elif event.type == FOE_ENTER_EVENT:
                    Foe.addFoe(bob)
                elif event.type == FOE_SHOOT_EVENT:
                    for foe in Foe.foes:
                        foe.fire()

        animate()
        if started:
            doCollisions()
            removeDeadShots()
            if bob.lives <= 0:
                print ("you lose")
                running = False
        clock.tick(FRAMERATE)
        # print ("fps = ", str(clock.get_fps()))
    pygame.quit()
