# 处理hosts文件
import yaml
from dns import resolver

special_hosts = ['kyfw.12306.cn', '', 'api.telegram.org',
                 'cvm.dogyun.com', 'account.dogyun.com', 'api.github.com', 'api.themoviedb.org']


# 读取docker/dockerfile_work/tgbot/docker-compose.yml
with open('docker/dockerfile_work/tgbot/docker-compose.yml', 'r+', encoding='utf-8') as f:
    content = f.read()
    yaml_content = yaml.load(
        content, Loader=yaml.FullLoader)

extra_hosts = []

for special_host in special_hosts:
    # 通过dns模块解析特定的域名
    if special_host in ['api.telegram.org', 'api.themoviedb.org']:
        type = ['A', 'AAAA']
    for t in type:
        record = resolver.query(f"{special_host}", f"{t}")
        answers = record.rrset.items
        for answer in answers:
            extra_hosts.append(f'{special_host}:{answer.address}')
# 对extra_hosts去重
extra_hosts = list(set(extra_hosts))

yaml_content['services']['tgbot']['extra_hosts'] = extra_hosts
# 更新docker-compose.yml
with open('docker/dockerfile_work/tgbot/docker-compose.yml', 'w+', encoding='utf-8') as f:
    yaml.dump(yaml_content, f, allow_unicode=True, sort_keys=False)
    f.flush()
    f.close()
