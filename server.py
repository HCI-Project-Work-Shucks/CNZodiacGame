#!/usr/bin/env python3
import sys

import tornado.ioloop
import tornado.options

import handlers
import settings

def main():
    tornado.options.define("port", default=80, type=int)
    tornado.options.parse_command_line()

    app = tornado.web.Application(handlers.handlers, **settings.settings)
    app.listen(tornado.options.options.port)

    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    sys.exit(main())
