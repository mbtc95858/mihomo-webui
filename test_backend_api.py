#!/usr/bin/env python3
import requests
import json

print('测试我们的后端 API...\n')

# 测试 /api/status
print('[1] 测试 /api/status')
try:
    response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('Response:', json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*60)
