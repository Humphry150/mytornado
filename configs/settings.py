# coding:utf-8

import os
host = "0.0.0.0"
port = 8888

WEB_COOKIE_SECRET = "123456789"

application_settings = dict(
    template_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=True,
    cookie_secret=WEB_COOKIE_SECRET,
    autoescape=None,
    login_url="/user/login/",
)

image_decrypt = {
    "encrypt_mark": "YUNFAN",
    # aes对称加密的密钥，长度最好为16位
    "aes_key": "abcdefghijklmno"
}

