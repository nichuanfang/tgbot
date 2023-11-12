# 处理hosts文件
import yaml
from dns import resolver

# 读取docker/dockerfile_work/tgbot/docker-compose.yml
with open('docker/dockerfile_work/tgbot/docker-compose.yml', 'r+', encoding='utf-8') as f:
    content = f.read()
    yaml_content = yaml.load(
        content, Loader=yaml.FullLoader)

extra_hosts = []

# 通过dns模块解析特定的域名
record = resolver.query("kyfw.12306.cn", "A")
answers = record.rrset.items

for answer in answers:
    extra_hosts.append(f'kyfw.12306.cn:{answer.address}')
# 对extra_hosts去重
extra_hosts = list(set(extra_hosts))

yaml_content['services']['tgbot']['extra_hosts'] = extra_hosts
# 更新docker-compose.yml
with open('docker/dockerfile_work/tgbot/docker-compose.yml', 'w+', encoding='utf-8') as f:
    yaml.dump(yaml_content, f, allow_unicode=True, sort_keys=False)
    f.flush()
    f.close()
