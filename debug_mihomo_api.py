#!/usr/bin/env python3
import requests
import json

controller_url = 'http://127.0.0.1:9090'
secret = '123456'
headers = {'Authorization': f'Bearer {secret}'} if secret else {}

print('=' * 60)
print('Mihomo API 完整测试')
print('=' * 60)

# 测试各个 API 端点
endpoints = [
    ('版本信息', '/version'),
    ('运行配置', '/configs'),
    ('代理列表', '/proxies'),
    ('规则列表', '/rules'),
    ('连接列表', '/connections'),
    ('流量统计', '/traffic'),
]

for name, endpoint in endpoints:
    print(f'\n[{name}] {endpoint}')
    print('-' * 60)
    try:
        url = f'{controller_url}{endpoint}'
        response = requests.get(url, headers=headers, timeout=5)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Success! Keys: {list(data.keys())[:10]}')
            # 打印一些关键信息
            if endpoint == '/version':
                print(f'  Version: {data}')
            elif endpoint == '/configs':
                print(f'  Mode: {data.get("mode")}')
                print(f'  Mixed Port: {data.get("mixed-port")}')
                print(f'  Allow LAN: {data.get("allow-lan")}')
                print(f'  TUN enabled: {data.get("tun", {}).get("enable", "N/A") if isinstance(data.get("tun"), dict) else data.get("tun")}')
            elif endpoint == '/proxies':
                proxies = data.get('proxies', {})
                print(f'  Total proxies: {len(proxies)}')
                print(f'  First 5: {list(proxies.keys())[:5]}')
            elif endpoint == '/connections':
                connections = data.get('connections', [])
                print(f'  Active connections: {len(connections)}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')

print('\n' + '=' * 60)
print('测试完成！')
print('=' * 60)
