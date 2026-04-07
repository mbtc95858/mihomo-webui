import requests

controller_url = 'http://127.0.0.1:9090'
secret = '123456'
headers = {'Authorization': f'Bearer {secret}'}

print('Testing Mihomo API...')
print('=' * 50)

# Test 1: /version
try:
    print('\n[1] Testing /version')
    res = requests.get(f'{controller_url}/version', headers=headers, timeout=3)
    print(f'Status: {res.status_code}')
    if res.status_code == 200:
        print(f'Response: {res.json()}')
except Exception as e:
    print(f'Error: {e}')

# Test 2: /configs
try:
    print('\n[2] Testing /configs')
    res = requests.get(f'{controller_url}/configs', headers=headers, timeout=3)
    print(f'Status: {res.status_code}')
    if res.status_code == 200:
        data = res.json()
        print(f'Config keys: {list(data.keys())[:10]}...')
except Exception as e:
    print(f'Error: {e}')

# Test 3: /proxies
try:
    print('\n[3] Testing /proxies')
    res = requests.get(f'{controller_url}/proxies', headers=headers, timeout=3)
    print(f'Status: {res.status_code}')
    if res.status_code == 200:
        proxies = res.json()
        print(f'Proxies count: {len(proxies.get("proxies", {}))}')
except Exception as e:
    print(f'Error: {e}')
