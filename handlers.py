# -*- coding: utf-8 -*-
import tornado.escape
import tornado.web
import tornado.websocket

import cnz


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        winner = self.get_argument("lastWin", None, True)
        winner = tornado.escape.xhtml_escape(winner) if winner else None
        self.render('game.html', winner=winner)


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    cnz = cnz.CNZodiac()

    def get_compression_options(self):
        return {}

    def open(self):
        pass

    def on_close(self):
        self.cnz.logout(self)

    def on_message(self, message):
        self.cnz.on_message(self, message)


handlers = [
    (r'/', MainHandler),
    (r'/ws', WebSocketHandler),
]
