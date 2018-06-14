# coding:utf-8

import os
import settings
import zlib
from AEScrypt import Prpcrypt


def image_decrypt(full_name=''):
    if os.path.exists(full_name):
        with open(full_name, 'r') as fp:
            content = fp.read()
            res_comp = content.replace(settings.encrypt_mark, "", 1)
            res_decomp = zlib.decompress(res_comp)
            prp = Prpcrypt()
            res_final = prp.decrypt(res_decomp)
            return res_final
    else:
        return ''


if __name__=="__main__":
    image_decrypt()