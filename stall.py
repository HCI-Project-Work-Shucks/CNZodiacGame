# -*- coding: utf-8 -*-
import random

import animal
import quiz


class Stall(object):

    def __init__(self, index, animal):
        self.index = index
        self.animal = animal

    def new_quiz(self):
        return quiz.Quiz.random(self.animal)


stalls_animals = [
    animal.OX,
    animal.PIG,
    animal.GOAT,
    animal.RAT,
    animal.MONKEY,
    animal.ROOSTER,
    animal.DOG,
    animal.RABBIT,
    animal.GOAT,
    animal.DOG,
    animal.TIGER,
    animal.SNAKE,
    animal.RAT,
    animal.GOAT,
    animal.DRAGON,
    animal.TIGER,
    animal.PIG,
    animal.SNAKE,
    animal.OX,
    animal.DRAGON,
    animal.SNAKE,
    animal.PIG,
    animal.HORSE,
    animal.DRAGON,
    animal.MONKEY,
    animal.ROOSTER,
    animal.RABBIT,
    animal.DOG,
    animal.HORSE,
    animal.TIGER,
    animal.OX,
    animal.HORSE,
    animal.MONKEY,
    animal.RABBIT,
    animal.SNAKE,
    animal.ROOSTER,
]


class Stalls(object):

    def __init__(self, animals=stalls_animals):
        self.count = len(animals)
        self.stalls = [Stall(i, anim) for i, anim in enumerate(animals)]

    def round(self, index):
        return self.stalls[index % self.count]

    def random(self, exclude_indexes):
        while 1:
            stall = random.choice(self.stalls)
            if stall.index not in exclude_indexes:
                return stall
