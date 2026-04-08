import requests
import json

controller_url = 'http://127.0.0.1:9090'
secret = '123456'
headers = {'Authorization': f'Bearer {secret}'}

print('=' * 60)
print('测试 Mihomo Proxies API')
print('=' * 60)

# 1. 获取所有代理和代理组
print('\n[1] 获取所有代理和代理组...')
try:
    response = requests.get(f'{controller_url}/proxies', headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f'✓ 成功获取，状态码: {response.status_code}')
        
        # 打印代理组信息
        print('\n--- 代理组列表 ---')
        proxies = data.get('proxies', {})
        for name, proxy in proxies.items():
            if proxy.get('type') == 'Selector':
                print(f'\n📋 代理组: {name}')
                print(f'   类型: {proxy.get("type")}')
                print(f'   当前选中: {proxy.get("now", "未设置")}')
                print(f'   可用节点数: {len(proxy.get("all", []))}')
                if len(proxy.get("all", [])) > 0:
                    print(f'   节点列表: {proxy.get("all", [])[:5]}...')
except Exception as e:
    print(f'✗ 失败: {e}')

# 2. 测试获取单个代理组
print('\n[2] 测试获取单个代理组...')
try:
    # 尝试获取一个代理组
    response = requests.get(f'{controller_url}/proxies/🚀 一键代理', headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f'✓ 成功获取 "🚀 一键代理" 代理组')
        print(f'  当前选中: {data.get("now", "未设置")}')
except Exception as e:
    print(f'✗ 失败: {e}')

# 3. 测试修改代理组选中节点（只是演示，不实际修改）
print('\n[3] 查看修改代理组的API格式...')
print('修改代理组的API: PUT /proxies/{group_name}')
print('请求体: {"name": "节点名称"}')

print('\n' + '=' * 60)
print('测试完成！')
print('=' * 60)
