# coding:utf-8

import os
import base64
import zlib
from Crypto.Cipher import AES
from configs.settings import image_decrypt
from handlers.base import BaseRequestHandler


class Prpcrypt(object):
    def __init__(self, key=image_decrypt.get('aes_key')):
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.
        # 目前AES-128足够用
        if len(key) < 16:
            key = key+(16-len(key))*"\0"
        self.key = key[:16]
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, IV=self.key)
        length = 16
        count = len(text)
        add=count % length
        if add:
            text = text + ('\0' * (length-add))
        self.ciphertext = cryptor.encrypt(text)

        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串用base64转化
        return base64.b64encode(self.ciphertext)

    # 解密后，去掉补足的'\0'用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, IV=self.key)
        plain_text = cryptor.decrypt(base64.b64decode(text))
        return plain_text.rstrip('\0')


class ImageDecryptHandler(BaseRequestHandler):

    def get(self, *args, **kwargs):
        full_name = "/data/test/static/images/b62ca5b757732595d55c5905d6debdf5.jpg"
        if os.path.exists(full_name):
            with open(full_name, 'r') as fo:
                content = fo.read()
                res_comp = content.replace(image_decrypt.get('encrypt_mark'), "", 1)
                res_decomp = zlib.decompress(res_comp)
                prp = Prpcrypt()
                res_final = prp.decrypt(res_decomp)
            self.write(res_final)
            self.set_header("Content-type", "image/jpg")
        else:
            self.write("")


