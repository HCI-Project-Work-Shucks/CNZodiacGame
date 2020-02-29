# -*- coding: utf-8 -*-

RAT = "rat"
OX = "ox"
TIGER = "tiger"
RABBIT = "rabbit"
DRAGON = "dragon"
SNAKE = "snake"
HORSE = "horse"
GOAT = "goat"
MONKEY = "monkey"
ROOSTER = "rooster"
DOG = "dog"
PIG = "pig"

ANIMALS = [
    RAT,
    OX,
    TIGER,
    RABBIT,
    DRAGON,
    SNAKE,
    HORSE,
    GOAT,
    MONKEY,
    ROOSTER,
    DOG,
    PIG,
]

def round(index):
    return ANIMALS[index % len(ANIMALS)]
