import json
from util.base64 import base64_encode
import requests


def trigger_github_workflow(GH_TOKEN: str, event_type: str, repo: str, payload: dict):
    """触发github workflow

    Args:
        GH_TOKEN (str): github token
        event_type (str): 时间类型
        repo (str): 仓库名
        payload (dict): 负载
    """
    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {GH_TOKEN}'
    }
    type = payload['type']
    requests.post('https://api.github.com/repos/nichuanfang/{repo}/dispatches',
                  data=json.dumps({"event_type": event_type, "client_payload": {"topic_payload": base64_encode(payload)}}), headers=header)
