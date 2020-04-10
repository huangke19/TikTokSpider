#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" user-agent池 """

# 导入标准库
import os
import re
import sys
from argparse import ArgumentParser


def input_user_agent():
    print("\n抖音要求user_agent和当前请求匹配，请输入当前请求中的user_agent值\n")
    UA = input("Dev_tools中的user_agent: ").strip()
    return UA


def input_request_url():
    print("\n请输入加载作品对应的url，注意检查返回值中aweme_list是否为空\n")
    URL = input("Dev_tools中的url: ").strip()
    return URL


def get_id_from_cmd(cmd_args):
    '''
    从命令行获取user_id

    :param cmd_args:    命令行参数
    :return:            user_id
    '''
    args = parse_args(cmd_args)
    if not args:
        return

    if args.user_id:
        _id = args.user_id
        return _id
    return None


def get_id_from_input():
    '''
    从用户输入获取user_id

    :return:    user_id
    '''
    _id = input('\n请输入你要爬取的抖音用户id: ')
    return _id


def is_valid_id(_id):
    '''
    检查用户输入的抖音id是否合法

    :param _id:  user_id
    :return:     bool
    '''
    if not _id:
        return False
    if not re.match('^\\d+$', str(_id).strip()):
        sys.stdout.write("请输入正确格式的抖音id\n")
        return False
    return True


def makedir(name):
    '''
    建立用户名文件夹

    :param name:    username
    :return:        None
    '''
    if not os.path.isdir(name):
        os.mkdir(name)
    else:
        pass


def parse_args(args):
    '''
    解析命令行参数

    :param args:    命令行参数
    :return:        新的parse_args函数
    '''
    parser = ArgumentParser()
    parser.add_argument('--uid', dest='user_id', type=int, help='用户的抖音id')
    return parser.parse_args(args)
