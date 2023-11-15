import json
import requests
from settings.config import github_config


def trigger_github_workflow(repo: str, event_type: str, client_payload: dict = {}):
    """触发github workflow

    Args:
        repo (str): 仓库名
        event_type (str): 事件类型
        client_payload (dict): 负载
    """
    GH_TOKEN = github_config['GITHUB_TOKEN']
    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {GH_TOKEN}'
    }
    data = json.dumps({"event_type": f"{event_type}",
                       "client_payload": client_payload})
    requests.post(f'https://api.github.com/repos/nichuanfang/{repo}/dispatches',
                  data=data, headers=header)
