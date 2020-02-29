# -*- coding: utf-8 -*-
import tornado.escape

import event
import player
import stall


class CNZodiac(object):

    def __init__(self):
        self.players = player.Players(stall.Stalls())

        self.funcs = {
            event.LOGIN: self.login,
            event.SAY: self.say,
            event.FIGHT: self.fight,
            event.FLIP: self.flip,
            event.REPLY: self.reply,
        }

    def on_message(self, ws, raw):
        p = self.players.get(ws)
        message = tornado.escape.json_decode(raw)
        fn = self.funcs.get(message.get('type'))
        if not fn:
            p.send(event.Err(p, 'invalid message'))
            return

        fn(p, message)

    def flip(self, player, message):
        self.players.flip(player)

    def fight(self, player, message):
        self.players.fight(player)

    def logout(self, ws):
        p = self.players.get(ws)
        if not p:
            return

        self.players.logout(p)

    def login(self, player, message):
        player.name = message.get('body')
        self.players.login(player)

    def say(self, player, message):
        self.players.say(player, message)

    def reply(self, player, message):
        self.players.reply(player, message)
