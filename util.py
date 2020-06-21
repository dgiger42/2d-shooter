import pygame
from math import sqrt


def dist(p1, p2):
    """compute distance between 2 points"""
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def move(obj):
    obj.location = [obj.location[0] + obj.velocity[0], obj.location[1] + obj.velocity[1]]
    obj.rect.center = tuple(map(int, obj.location))
