# coding: utf8

import os
import sys
import datetime
import settings
import zlib
from AEScrypt import Prpcrypt





def write_success_log():
    pass


def write_error_log(msg):
    """
    错误日志
    :param msg:
    :return:
    """
    with open('./error.log', 'a+') as f:
        f.write("{}\t{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))


def get_all_image_count(directory):
    """
    获取目录下的所有图片总数
    :param directory: 目录
    """
    directory = directory if directory.endswith("/") else "{}/".format(directory)
    lists = os.listdir(directory)
    count = 0
    for val in lists:
        if os.path.isfile(directory+val) and (os.path.splitext(val)[1] in settings.image_ext):
            # 如果是图片
            count += 1
        elif os.path.isdir(directory+val):
            # 如果是目录
            count += get_all_image_count(directory+val)
    return count


def do_encrypt(directory):
    """
    执行加密
    :param directory:目录
    :param _current:当前正在执行的个数
    :param _all:总数
    :return:
    """
    global _current, _all
    # 目录处理
    directory = directory if directory.endswith("/") else "{}/".format(directory)

    if os.path.exists(directory):
        # 目录存在
        for item in os.listdir(directory):
            current_file = directory + item
            ext = os.path.splitext(item)[1]
            if os.path.isfile(current_file) and (os.path.splitext(item)[1] in settings.image_ext):
                # 图片
                if ext in settings.image_ext:
                    # 如果是指定类型的图片文件，则执行加密操作)
                    try:
                        with open(current_file, 'r+') as fp:
                            before_text = fp.read()
                            if before_text.startswith("YUNFAN"):
                                # print("has encrypt")
                                pass
                            else:
                                prp = Prpcrypt()
                                # 对内容加密
                                after_text = prp.encrypt(before_text)
                                # 对内容进行压缩
                                after_comp = zlib.compress(after_text)
                                # 将文件指针指到文件开始处
                                fp.seek(0)
                                # 清空文件
                                fp.truncate()
                                # 在内容开头处添加一个标记，下次执行压缩图片的脚本时就可以跳过这个文件
                                fp.write("YUNFAN" + after_comp)
                                _current += 1
                                # 显示加密进度
                                print "\r已完成{}%".format(_current*100/_all),
                                # print(i,end="")
                                sys.stdout.flush()
                    except:
                        write_error_log("{}图片加密时出错\n".format(current_file))
                else:
                    continue
            elif os.path.isdir(current_file):
                # 目录
                do_encrypt(current_file)
    else:
        # 目录不存在
        print("{}图片目录不存在".format(directory))
        write_error_log("{}图片目录不存在\n".format(directory))


if __name__ == "__main__":
    # aes对称加密的密钥，长度最好为16位
    aes_key = "abcdefghijklmno"

    params = sys.argv
    target_dir = params[1] if len(params) > 1 else settings.target_dir
    if os.path.exists(target_dir):
        _current = 0
        _all = get_all_image_count(target_dir)
        do_encrypt(target_dir)
    else:
        print("{}图片目录不存在".format(target_dir))
        write_error_log("{}图片目录不存在\n".format(target_dir))

