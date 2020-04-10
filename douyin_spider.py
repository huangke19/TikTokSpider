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
import re
import sys
from time import sleep

# 导入第三方库
import requests

# 全局变量
from utils import (
    get_id_from_cmd,
    is_valid_id,
    get_id_from_input,
    input_user_agent,
    input_request_url,
    makedir
)

VIDEO_URLS, PAGE = [], 1

URL = input_request_url()
HEADERS = {
    'user-agent': input_user_agent()
}


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


def get_username(user_id):
    '''
    获取用户名

    :param user_id:     用户抖音id
    :returns:           username
    '''
    url = "https://www.amemv.com/share/user/%s" % user_id
    headers = HEADERS
    try:
        print("\n获取用户名，建立文件夹中...\n")
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
        global PAGE
        print('\n正在收集第%s页视频地址\n' % (PAGE))
        response = requests.request("GET", url, headers=HEADERS)
        print('第%s页视频地址获取成功\n' % (PAGE))

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

    print("\n下载第%s个视频: %s" % (index, name))
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
