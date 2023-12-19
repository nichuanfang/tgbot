# 阿里云盘相关的工具模块
import base64
import json
import os
import time
from aligo import Aligo
from difflib import SequenceMatcher

try:
    ALIGO_TOKEN = os.environ.get('ALIGO_TOKEN', '')
    aligo_config_str = base64.b64decode(
        ALIGO_TOKEN).decode(encoding='utf-8')
    aligo_config: dict = json.loads(aligo_config_str)
    refresh_token = aligo_config['refresh_token']
    aligo = Aligo(refresh_token=refresh_token, re_login=False)
except Exception as e:
    raise Exception(f'请检查环境变量ALIGO_TOKEN是否正确: {e}')


def calculate_file_size(parent_file_id: str, share_token: str):
    """计算电影文件大小

    Args:
        parent_file_id (str): 父文件id
        share_token (str): 分享token

    Returns:
        float: 视频文件大小
    """
    max_size = 0
    share_file = aligo.get_share_file(parent_file_id, share_token)
    if share_file.type == 'file':  # 如果是文件
        # 在这里根据文件类型判断是否是视频文件，可以使用相应的方法来获取文件大小
        if share_file.file_extension in ('mkv', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'f4v', 'm4v', 'rmvb', 'rm', '3gp', 'dat', 'ts', 'mts', 'vob'):
            max_size = share_file.size
    else:  # 如果是文件夹
        share_file_list = aligo.get_share_file_list(
            share_token, parent_file_id)
        for share_file in share_file_list:
            size = calculate_file_size(
                share_file.file_id, share_token)  # 传递正确的参数
            if size > max_size:
                max_size = size
    time.sleep(0.2)
    return max_size


def calculate_tv_file_size(parent_file_id: str, share_token: str):
    """计算电影文件大小

    Args:
        parent_file_id (str): 父文件id
        share_token (str): 分享token

    Returns:
        float: 视频文件大小
    """
    share_file = aligo.get_share_file(parent_file_id, share_token)
    if share_file.type == 'file':  # 如果是文件
        # 在这里根据文件类型判断是否是视频文件，可以使用相应的方法来获取文件大小
        if share_file.file_extension in ('mkv', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'f4v', 'm4v', 'rmvb', 'rm', '3gp', 'dat', 'ts', 'mts', 'vob'):
            return share_file.size
    else:  # 如果是文件夹
        share_file_list = aligo.get_share_file_list(
            share_token, parent_file_id)
        for share_file in share_file_list:
            size = calculate_tv_file_size(
                share_file.file_id, share_token)  # 传递正确的参数
            if size > 0:
                return size
    time.sleep(0.2)
    return 0


def preprocess_string(s):
    # 移除空格和括号 不考虑大小写
    s = s.replace(" ", "").replace("(", "").replace(")", "").lower()
    return s


def similarity_score(s1, s2, file_size, weight_edit_distance, weight_file_size):
    """计算相似度得分

    Args:
        s1 (_type_): 第一个字符串
        s2 (_type_): 第二个字符串
        file_size (_type_): 文件大小
        weight_edit_distance (_type_): 字符串相似度权重
        weight_file_size (_type_): 文件大小权重

    Returns:
        _type_: 相似度得分
    """
    similarity = SequenceMatcher(None,
                                 preprocess_string(s1), preprocess_string(s2)).ratio()
    score = weight_edit_distance * similarity + weight_file_size * file_size
    return score


def handle_share_res(name: str, share_res: list[dict[str, str]], type):
    """处理分享链接列表

    Args:
        name: 电影或剧集名称
        share_ids (list[str]): 分享链接列表
        type (str): 类型

    Returns:
        list[dict[str,str]]: 处理后的分享链接列表
    """
    res = []
    for share_item in share_res:
        # 分享详情
        try:
            share_id = share_item['share_id']
            share_name = share_item['name']
            share_info = aligo.get_share_info(share_id)
            # 分享token
            share_token = aligo.get_share_token(share_id)
        except:
            continue

        # 转为GB  保留两位小数
        try:
            if type == 'movie':
                max_size = calculate_file_size(
                    'root', share_token)
            elif type == 'tv':
                max_size = calculate_tv_file_size(
                    'root', share_token)
            max_size = round(max_size / 1024 / 1024 / 1024, 2)
        except:
            max_size = 0

        # 死链检测
        try:
            if share_info.file_count < 1 or max_size == 0:
                # 总文件数小于1 或者 视频文件大小为0
                continue
        except Exception as e:
            print(f'死链检测失败: {e}')
            continue

        # 除了文件大小还要考虑相似度匹配程度
        score = similarity_score(
            name, share_name, max_size, 1, 0)
        res.append({
            'name': share_name,
            'url': f'https://www.aliyundrive.com/s/{share_id}',
            'size': f'{max_size}GB',
            'score': score
        })
        time.sleep(0.2)
    # 根据score排序 从大到小
    res.sort(key=lambda x: x['score'], reverse=True)
    return res


if __name__ == '__main__':
    test_ids = ['BiTcxmfjeys', 'F3gwK1WQJs8']
    res = handle_share_res('阿凡达2', test_ids)
    pass
