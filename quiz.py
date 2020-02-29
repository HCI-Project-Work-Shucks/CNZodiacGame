# -*- coding: utf-8 -*-
import collections
import random


def load():
    quiz = collections.defaultdict(dict)

    with open('quiz.dat') as f:
        for line in f:
            part = line.split('|')
            if len(part) != 3:
                raise ValueError('invalid content: %s' % line)

            ani, topic, answer = part
            quiz[ani][topic] = answer

    return quiz


class Quiz(object):

    quizzes = load()

    def __init__(self, animal, topic, answers):
        self.animal = animal
        self.topic = topic
        self.answers = answers
        random.shuffle(self.answers)

    def resp_obj(self):
        return dict(
            animal=self.animal,
            topic=self.topic,
            answers=self.answers,
        )

    @classmethod
    def get_answer(cls, animal, topic):
        aq = cls.quizzes.get(animal)
        return aq.get(topic) if aq else None

    @classmethod
    def random(cls, animal, traps_count=3):
        quizzes = cls._random(animal, count=1+traps_count)
        topic = quizzes[0][0]
        answers = [q[1] for q in quizzes]
        return Quiz(animal, topic, answers)

    @classmethod
    def _random(cls, animal, count):
        topics = list(cls.quizzes[animal].keys())
        random.shuffle(topics)
        return [(topic, cls.quizzes[animal][topic]) for topic in topics[:count]]
