# -*- coding: utf-8 -*-
import tornado.escape

ERROR = 0x0
LOGIN = 0x1
LOGOUT = 0x2
SAY = 0x3
FIGHT = 0x5
ROUND = 0x6
FLIP = 0x7
REPLY = 0x8
REVEAL = 0x9
WIN = 0xa


class Event(object):

    def __init__(self, type, player):
        self.type = type
        self.player = player

    def json(self, ws):
        return tornado.escape.json_encode(self.resp_obj(ws))
    
    def resp_obj(self, ws):
        dic = dict(type=self.type)
        dic.update(self.player.resp_obj())
        return dic


class Err(Event):

    def __init__(self, player, message):
        super(Err, self).__init__(ERROR, player)
        self.message = message

    def resp_obj(self, ws):
        obj = super(Err, self).resp_obj(ws)
        obj['body'] = self.message
        return obj


class Message(Event):

    def __init__(self, player, message):
        super(Message, self).__init__(SAY, player)
        self.name = self.player.name
        self.message = message

    def resp_obj(self, ws):
        obj = super(Message, self).resp_obj(ws)
        obj['html'] = ws.render_string('message.html', event=self).decode('utf-8')
        return obj


class Fight(Event):

    def __init__(self, player):
        super(Fight, self).__init__(FIGHT, player)


class LoggedIn(Event):

    def __init__(self, player, chessers):
        super(LoggedIn, self).__init__(LOGIN, player)
        self.chessers = chessers

    def resp_obj(self, ws):
        obj = super(LoggedIn, self).resp_obj(ws)
        obj['message'] = '**NOTICE** %s joined' % self.player.name
        obj['chessers'] = [c.resp_obj() for c in self.chessers]
        return obj


class Win(Event):

    def __init__(self, player):
        super(Win, self).__init__(WIN, player)


class LoggedOut(Event):

    def __init__(self, player, new_round_chesser=None):
        super(LoggedOut, self).__init__(LOGOUT, player)
        self.new_round_chesser = new_round_chesser

    def resp_obj(self, ws):
        obj = super(LoggedOut, self).resp_obj(ws)
        obj['message'] = '**NOTICE** %s exited' % self.player.name

        if self.new_round_chesser:
            obj['new_round_chesser'] = self.new_round_chesser.resp_obj()

        return obj


class Round(Message):

    def __init__(self, player):
        message = "**NOTICE** %s's round" % player.name
        super(Round, self).__init__(player, message)
        self.type = ROUND


class Reveal(Event):

    def __init__(self, player, correct, next_chesser):
        super(Reveal, self).__init__(REVEAL, player)
        self.correct = correct
        self.next_chesser = next_chesser

    def resp_obj(self, ws):
        obj = super(Reveal, self).resp_obj(ws)
        obj['correct'] = self.correct

        if self.next_chesser:
            obj['next_chesser'] = self.next_chesser.resp_obj()

        return obj


class Flip(Event):

    def __init__(self, player, point, quiz):
        super(Flip, self).__init__(FLIP, player)
        self.point = point
        self.type = FLIP
        self.quiz = quiz

    def resp_obj(self, ws):
        obj = super(Flip, self).resp_obj(ws)
        obj['point'] = self.point
        obj['quiz'] = self.quiz.resp_obj()
        return obj
