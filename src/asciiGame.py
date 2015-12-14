'''
Created on 15 déc. 2015

@author: denis
'''


import random

class Screen:
    def __init__(self, l, h):
        self.l = l
        self.h = h
        self.elements = {}
    def add(self, x, y, e):
        self.elements[(x, y)] = e
    def clear(self, x, y):
        del self.elements[(x, y)]
    def clearAll(self):
        self.elements.clear()
    def __str__(self):
        l = ['+']
        l.append('-' * self.l)
        l.append('+\n')
        for i in range(self.h):
            l.append('|')
            for j in range(self.l):
                if (j,i) in self.elements:
                    l.append(self.elements[(j, i)])
                else:
                    l.append(' ')
            l.append('|\n')
        l.append('+')
        l.append('-' * self.l)
        l.append('+\n')
        return ''.join(l)

class Character:
    def __init__(self, screen):
        self.screen = screen
        self.x = 0
        self.y = 0
        self.horizontal = True
        self.positive = True
        self.screen.add(self.x, self.y, ">")
    def turnRight(self):
        if self.horizontal:
            self.horizontal = False
            if self.positive:
                self.screen.add(self.x, self.y, "v")
            else:
                self.screen.add(self.x, self.y, "^")
        else:
            self.horizontal = True
            if self.positive:
                self.positive = False
                self.screen.add(self.x, self.y, "<")
            else:
                self.positive = True
                self.screen.add(self.x, self.y, ">")
        return self
    def turnLeft(self):
        if self.horizontal:
            self.horizontal = False
            if self.positive:
                self.positive = False
                self.screen.add(self.x, self.y, "^")
            else:
                self.positive = True
                self.screen.add(self.x, self.y, "v")
        else:
            self.horizontal = True
            if self.positive:
                self.screen.add(self.x, self.y, ">")
            else:
                self.screen.add(self.x, self.y, "<")
        return self
    def move(self):
        self.screen.clear(self.x, self.y)
        if self.horizontal:
            if self.positive:
                if self.x < self.screen.l - 1:
                    self.x += 1
                else:
                    print('you hurt a wall')
                self.screen.add(self.x, self.y, ">")
            else:
                if self.x > 0:
                    self.x -= 1
                else:
                    print('you hurt a wall')
                self.screen.add(self.x, self.y, "<")
        else:
            if self.positive:
                if self.y < self.screen.h - 1:
                    self.y += 1
                else:
                    print('you hurt a wall')
                self.screen.add(self.x, self.y, "v")
            else:
                if self.y > 0:
                    self.y -= 1
                else:
                    print('you hurt a wall')
                self.screen.add(self.x, self.y, "^")
        return self
    def __repr__(self):
        return '\n' + str(self.screen)

def randomPilot(character, stepNumber):
    for i in range(stepNumber):
        n = random.randint(1,3)
        if n == 1:
            character.move()
        elif n == 2:
            character.turnRight()
        else:
            character.turnLeft()
        print(character)

if __name__ == '__main__':
    c = Character(Screen(7,5))
    randomPilot(c, 10)
