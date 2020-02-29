# -*- coding: utf-8 -*-
import os

settings = dict(
    cookie_secret="HCI-CNZodiac:2f1e21a6-bc15-484c-ad79-44913f960545",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=True,
)
