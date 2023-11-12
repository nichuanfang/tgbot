# 处理hosts文件
import yaml

# 读取docker/dockerfile_work/tgbot/docker-compose.yml
with open('docker/dockerfile_work/tgbot/docker-compose.yml', 'r+', encoding='utf-8') as f:
    content = f.read()
    yaml_content = yaml.load(
        content, Loader=yaml.FullLoader)

extra_hosts = []
with open('hosts', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('#'):
            continue
        else:
            line = line.strip()
            if line:
                host_ip_entry = line.split(' ')
                if len(host_ip_entry) != 2:
                    raise Exception('hosts文件格式错误')
                else:
                    host_ip = host_ip_entry[0]
                    host_name = host_ip_entry[1]
                    # 如果yaml_content['services']['tgbot']['extra_hosts']不存在，则创建
                    extra_hosts.append(f'{host_name}:{host_ip} ')
yaml_content['services']['tgbot']['extra_hosts'] = extra_hosts
# 更新docker-compose.yml
with open('docker/dockerfile_work/tgbot/docker-compose.yml', 'w+', encoding='utf-8') as f:
    yaml.dump(yaml_content, f, allow_unicode=True, sort_keys=False)
    f.flush()
    f.close()
