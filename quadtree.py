from collections import deque

from pygame import Rect

from constants import *


class QTNode:
    def __init__(self, region: Rect):
        self.child_nodes: list[QTNode] = []
        self.region: Rect = region
        self.rects: list[Rect] = []

    def print_nodes(self):
        print(f'printing nodes... ')
        frontier = deque([self])
        while len(frontier) > 0:
            cur_node = frontier.popleft()
            print(f'cur_node.region: {str(cur_node.region):<27}  {cur_node.rects = }')
            for child in cur_node.child_nodes:
                frontier.append(child)

    def split(self):
        assert len(self.rects) > 0
        assert len(self.child_nodes) == 0
        print(f'splitting nodes... ')
        sub_w = self.region.width / 2
        sub_h = self.region.height / 2
        top_left = QTNode(Rect(self.region.left, self.region.top, sub_w, sub_h))
        top_right = QTNode(Rect(self.region.centerx, self.region.top, sub_w, sub_h))
        bottom_left = QTNode(Rect(self.region.left, self.region.centery, sub_w, sub_h))
        bottom_right = QTNode(Rect(self.region.centerx, self.region.centery, sub_w, sub_h))
        self.child_nodes = [top_left, top_right, bottom_left, bottom_right]

        remaining_rects = []
        for rect in self.rects:
            is_contained = False
            for child in self.child_nodes:
                if child.region.contains(rect):
                    is_contained = True
                    child.insert_rect(rect)
                    break
            if not is_contained:
                remaining_rects.append(rect)

        self.rects = remaining_rects



    def insert_rect(self, rect: Rect):
        if len(self.child_nodes) == 0 and len(self.rects) == 0:  # not split yet, and empty
            self.rects.append(rect)
        else:
            if len(self.child_nodes) == 0:
                self.split()

            # raise NotImplementedError('need to add to right box(es)')

class QuadTree:
    def __init__(self):
        self.root = QTNode(Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
