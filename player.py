# -*- coding: utf-8 -*-
import logging
import random

import dice
import event
import quiz

MAX_CHESSERS_COUNT = 4
INIT_SCORE = 1000
CORRECT_SCORE = 100
INCORRECT_SCORE = -100
LOST_SCORE = 0
WIN_SCORE = 2000


class Player(object):

    def __init__(self, ws):
        self.ws = ws
        self.name = None
        self.prev = None
        self.next = None
        self.is_chesser = False
        self.bgcolor = self.random_rgb()
        self.stall = None
        self.score = INIT_SCORE

    def forward(self, stall):
        self.stall = stall

    def resp_obj(self):
        dic = dict(player_id=id(self),
                   player_name=self.name,
                   player_score=self.score,
                   rgb=self.bgcolor)

        if self.stall:
            dic['stall'] = self.stall.index

        return dic

    @classmethod
    def random_rgb(cls):
        return random.randint(0, 0xaaaaaa)

    def send(self, event):
        try:
            logging.warning('event: %s, ws: %s', event.type, self.ws)
            self.ws.write_message(event.json(self.ws))
        except Exception:
            logging.exception('error sending message')


class Players(object):

    def __init__(self, stalls):
        self.active_chesser = None
        self.chessers_count = 0
        self.stalls = stalls
        self.players = {}
        self.dice = dice.Dice()

    def get(self, ws):
        p = self.players.get(id(ws))
        p = p if p else Player(ws)
        return p

    def say(self, player, message):
        s = message.get('body')
        if not s:
            player.send(event.Err(player, 'invalid message'))
            return

        self._send(event.Message(player, s))

    def flip(self, player):
        if not player.is_chesser:
            player.send(event.Err(player, 'you are not a chesser'))
            return

        rand = self.dice.random()
        index = player.stall.index + rand
        stall = self.stalls.round(index)
        player.forward(stall)

        self._send(event.Flip(player, rand, stall.new_quiz()))

    def fight(self, player):
        if player.is_chesser:
            player.send(event.Err(player, 'fought liao'))
            return

        if self.chessers_count >= MAX_CHESSERS_COUNT:
            player.send(event.Err(player, 'too many chessers'))
            return

        self.add_chesser(player)

        rivals = self.rivals(player)
        exclude_rivals_indexes = [r.stall.index for r in rivals]
        player.stall = self.stalls.random(exclude_rivals_indexes)
        self._send(event.Fight(player))

        if self.chessers_count == 2:
            self._send(event.Round(self.active_chesser))

    def reply(self, player, message):
        answer = quiz.Quiz.get_answer(message.get('animal'), message.get('topic'))

        correct = (answer == message.get('answer')) if answer else False
        player.score += CORRECT_SCORE if correct else INCORRECT_SCORE

        if player.score >= WIN_SCORE:
            self._send(event.Win(player))
            return

        next_chesser = self.turn_next_chesser()
        self._send(event.Reveal(player, correct, next_chesser))

    def turn_next_chesser(self):
        if self.chessers_count <= 1:
            return

        current = self.active_chesser
        next = current.next

        while 1:
            if next.name == current.name:
                return

            if next.score <= LOST_SCORE:
                next = next.next
                continue

            self.active_chesser = next
            break

        return self.active_chesser

    def rivals(self, player):
        rivals = []
        cur = self.active_chesser

        for _ in range(self.chessers_count):
            if cur.name != player.name:
                rivals.append(cur)
            cur = cur.next

        return rivals

    def chessers(self):
        chessers = []
        cur = self.active_chesser

        for _ in range(self.chessers_count):
            chessers.append(cur)
            cur = cur.next

        return chessers

    def add_chesser(self, player):
        player.is_chesser = True
        self.chessers_count += 1

        if not self.active_chesser:
            self.active_chesser = player
            # point to itself.
            player.prev = player
            player.next = player
            return

        prev = self.active_chesser.prev
        prev.next = player
        player.prev = prev
        player.next = self.active_chesser

        self.active_chesser.prev = player

    def logout(self, player):
        try:
            self.players.pop(id(player.ws))
        except KeyError:
            return

        if not player.is_chesser:
            self._send(event.LoggedOut(player))
            return

        new_active_chesser = self.logout_chesser(player)
        self._send(event.LoggedOut(player, new_round_chesser=new_active_chesser))

    def logout_chesser(self, player):
        self.chessers_count -= 1

        if self.chessers_count == 0:
            self.active_chesser = None
            return

        if player == self.active_chesser:
            self.active_chesser = player.next

        player.prev.next = player.next
        player.next.prev = player.prev

        if self.chessers_count > 1:
            return self.active_chesser

    def login(self, player):
        if not player.name:
            player.send(event.Err(player, 'invalid name'))
            return

        if player in self:
            player.send(event.Err(player, 'name is taken'))
            return

        self.players[id(player.ws)] = player

        # notice all players includes the logged in player.
        self._send(event.LoggedIn(player, self.chessers()))

    # send event to all players.
    def _send(self, event):
        for p in self:
            p.send(event)

    def __contains__(self, player):
        for p in self:
            if player.name == p.name:
                return True
        return False

    def __iter__(self):
        for _, p in self.players.items():
            yield p
