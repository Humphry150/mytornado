# coding:utf-8


import base


class DefaultHandler(base.BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render("default/index.html")