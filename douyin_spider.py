#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 一只抖音小爬虫 '''

#############################
#
#  Author: Huang Ke
#  Email: huangkwell@163.com
#  微信: 760208296
#  复活时间: 2020/4/6
#
#############################


# 导入标准库
import os
import re
import sys
from argparse import ArgumentParser
from time import sleep

# 导入第三方库
import requests

# 全局变量
VIDEO_URLS, PAGE = [], 1

URL = input("目标URL: ").strip()

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Mobile Safari/537.36'
}


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


def get_douyin_id():
    '''
    获取抖音用户id

    :return:    user_id
    '''
    _id1 = get_id_from_cmd(sys.argv[1:])
    if _id1:
        if is_valid_id(_id1):
            return _id1
        else:
            return get_douyin_id()

    _id2 = get_id_from_input()
    if _id2:
        if is_valid_id(_id2):
            return _id2
        else:
            return get_douyin_id()

    return None


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
    _id = input('请输入你要爬取的抖音用户id: ')
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


def get_username(user_id):
    '''
    获取用户名

    :param user_id:     用户抖音id
    :returns:           username
    '''
    url = "https://www.amemv.com/share/user/%s" % user_id
    headers = HEADERS
    try:
        response = requests.request("GET", url, headers=headers)
        name = re.findall('<p class="nickname">(.*?)</p>', response.text)[0]
        return name
    except (TypeError, IndexError):
        sys.stdout.write("提示： 请确认输入的是用户ID，而不是抖音号或单个视频的id\n")
        return None, None
    except requests.exceptions:
        sys.stdout.write("连接错误，未能获取正确数据\n")
        return None, None


def get_all_video_urls(user_id, max_cursor):
    '''
    递归获取用户所有视频的源地址url

    :param user_id:     用户抖音id
    :param max_cursor:  下一页地址游标

    :return:            urls
    '''

    url = re.sub('max_cursor=0', 'max_cursor=%s' % max_cursor, URL, )

    try:
        response = requests.request("GET", url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            l = data['aweme_list']
            if l == []:
                print("请检查输入的url地址，在Devtools里确认Response中aweme_list列表不为空")
                return VIDEO_URLS

            for li in data['aweme_list']:
                name = li.get('desc')
                url = li.get('video').get('play_addr').get('url_list')[0]
                VIDEO_URLS.append([name, url])
                print(VIDEO_URLS[-1])

            # 下拉获取更多视频
            if data['has_more'] is True and data.get('max_cursor') != 0:
                sleep(1)
                global PAGE
                print('正在收集第%s页视频地址' % (PAGE + 1))
                PAGE += 1
                return get_all_video_urls(
                    user_id, data.get('max_cursor'))
            else:
                return VIDEO_URLS
        else:
            print(response.status_code)
            return
    except Exception as e:
        print('failed,', e)
        return


def download_video(index, username, name, url, retry=3):
    '''
    下载视频,显示进度

    :param index:       视频序号
    :param username:    用户名
    :param name:        视频名
    :param url:         视频地址
    :param retry:       重试次数

    :return:            None
    '''

    print("\r下载第%s个视频: %s" % (index, name))
    try:
        response = requests.get(
            url,
            stream=True,
            headers=HEADERS,
            timeout=15,
            allow_redirects=False)
        video_url = response.headers['Location']
        video_response = requests.get(
            video_url, headers=HEADERS, timeout=15)

        # 保存视频，显示下载进度
        if video_response.status_code == 200:
            video_size = int(video_response.headers['Content-Length'])
            with open('%s/%s.mp4' % (username, name), 'wb') as f:
                data_length = 0
                for data in video_response.iter_content(chunk_size=1024):
                    data_length += len(data)
                    f.write(data)
                    done = int(50 * data_length / video_size)
                    sys.stdout.write("\r下载进度: [%s%s]" % (
                        '█' * done, ' ' * (50 - done)))
                    sys.stdout.flush()

        # 失败重试3次，超过放弃
        elif video_response.status_code != 200 and retry:
            retry -= 1
            download_video(index, username, name, url, retry)
        else:
            return
    except Exception as e:
        print('download failed,', name, e)
        return None


def download_all_videos(videl_urls, username):
    """
    下载所有的视频
    """
    for index, item in enumerate(videl_urls, 1):
        name = item[0]
        if name == '抖音-原创音乐短视频社区':
            name = name + str(index)
        url = item[1]
        download_video(index, username, name, url)
        sleep(1)
    pass


def main():
    '''
    主函数, 下载视频
    :return: None
    '''
    _id = get_douyin_id()

    username = get_username(_id)
    if not username:
        return
    else:
        makedir(username)

    video_urls = get_all_video_urls(_id, 0)
    if not video_urls:
        return

    download_all_videos(video_urls, username)


if __name__ == '__main__':
    main()
