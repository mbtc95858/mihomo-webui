from flask import Flask, render_template, jsonify, request
import yaml
import os
import subprocess
import shutil
import time
import shlex
import requests

app = Flask(__name__)

CONFIG_PATH = '/home/admin/.config/mihomo/config.yaml'
BACKUP_PATH = '/home/admin/.config/mihomo/config.yaml.backup'

cache = {
    'status': {'data': None, 'time': 0},
    'logs': {'data': None, 'time': 0},
    'traffic': {'data': None, 'time': 0}
}
CACHE_TTL = 2


def load_config_raw():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def clear_cache():
    cache['status']['data'] = None
    cache['status']['time'] = 0
    cache['logs']['data'] = None
    cache['logs']['time'] = 0
    cache['traffic']['data'] = None
    cache['traffic']['time'] = 0


def save_config_raw(content):
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    clear_cache()


def save_config(config):
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    clear_cache()


def restart_mihomo():
    try:
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        mihomo_pids = []
        mihomo_cmd = None
        for line in ps_result.stdout.split('\n'):
            if 'mihomo' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    mihomo_pids.append(parts[1])
                    if not mihomo_cmd:
                        idx = line.find('/usr/local/bin/mihomo')
                        if idx != -1:
                            mihomo_cmd = line[idx:].strip()
        
        if not mihomo_pids:
            return False, '重启失败：未找到 mihomo 进程'
        
        for pid in mihomo_pids:
            subprocess.run(['kill', '-9', pid], capture_output=True)
        
        time.sleep(1)
        
        mihomo_path = '/usr/local/bin/mihomo'
        config_dir = '/home/admin/.config/mihomo'
        if not os.path.exists(mihomo_path) or not os.path.exists(config_dir):
            return False, '重启失败：找不到 mihomo 可执行文件或配置目录'
        
        if mihomo_cmd:
            args = shlex.split(mihomo_cmd)
            subprocess.Popen(args,
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
        else:
            subprocess.Popen([mihomo_path, '-d', config_dir], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
        
        return True, 'Mihomo 服务重启成功'
        
    except Exception as e:
        return False, f'重启失败: {str(e)}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/config/raw', methods=['GET'])
def get_config_raw():
    try:
        content = load_config_raw()
        return jsonify({
            'success': True,
            'config': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/config/raw', methods=['POST'])
def update_config_raw():
    try:
        data = request.get_json()
        content = data.get('config', '')
        save_config_raw(content)
        return jsonify({
            'success': True,
            'message': '配置保存成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        config = load_config()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/config', methods=['POST'])
def update_config():
    try:
        data = request.get_json()
        new_config = data.get('config', {})
        original_config = load_config()
        
        def deep_merge(original, update):
            result = original.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged_config = deep_merge(original_config, new_config)
        save_config(merged_config)
        return jsonify({
            'success': True,
            'message': '配置保存成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/proxies', methods=['GET'])
def get_proxies():
    try:
        config = load_config()
        proxies = config.get('proxies', [])
        proxy_groups = config.get('proxy-groups', [])
        return jsonify({
            'success': True,
            'proxies': proxies,
            'proxyGroups': proxy_groups
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/proxy-groups', methods=['POST'])
def update_proxy_groups():
    try:
        data = request.get_json()
        proxy_groups = data.get('proxyGroups', [])
        config = load_config()
        config['proxy-groups'] = proxy_groups
        save_config(config)
        return jsonify({
            'success': True,
            'message': '代理组更新成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/rules', methods=['GET'])
def get_rules():
    try:
        config = load_config()
        rules = config.get('rules', [])
        rule_providers = config.get('rule-providers', {})
        return jsonify({
            'success': True,
            'rules': rules,
            'ruleProviders': rule_providers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/rules', methods=['POST'])
def update_rules():
    try:
        data = request.get_json()
        rules = data.get('rules', [])
        config = load_config()
        config['rules'] = rules
        save_config(config)
        return jsonify({
            'success': True,
            'message': '规则更新成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/status', methods=['GET'])
def get_status():
    current_time = time.time()
    if cache['status']['data'] and (current_time - cache['status']['time']) < CACHE_TTL:
        return jsonify(cache['status']['data'])
    
    try:
        status = {
            'running': False,
            'pid': None,
            'cpu': None,
            'memory': None,
            'uptime': None,
            'command': None,
            'ports': [],
            'version': None,
            'mode': None,
            'mixed_port': None,
            'allow_lan': False,
            'tun_enabled': False
        }
        
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        for line in ps_result.stdout.split('\n'):
            if 'mihomo' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 10:
                    status['running'] = True
                    status['pid'] = parts[1]
                    status['cpu'] = parts[2]
                    status['memory'] = parts[3]
                    status['command'] = ' '.join(parts[10:])
                    
                    try:
                        stat_result = subprocess.run(['ps', '-p', parts[1], '-o', 'lstart='], 
                                                   capture_output=True, text=True, timeout=2)
                        if stat_result.returncode == 0:
                            status['uptime'] = stat_result.stdout.strip()
                    except Exception as e:
                        pass
        
        if status['pid']:
            try:
                netstat_result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True, timeout=5)
                for line in netstat_result.stdout.split('\n'):
                    if status['pid'] in line:
                        parts = line.split()
                        if len(parts) > 3:
                            local_addr = parts[3]
                            if ':' in local_addr:
                                port = local_addr.split(':')[-1]
                                if port not in status['ports']:
                                    status['ports'].append(port)
            except Exception as e:
                try:
                    ss_result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
                    for line in ss_result.stdout.split('\n'):
                        if status['pid'] in line:
                            parts = line.split()
                            if len(parts) > 4:
                                local_addr = parts[4]
                                if ':' in local_addr:
                                    port = local_addr.split(':')[-1]
                                    if port not in status['ports']:
                                        status['ports'].append(port)
                except Exception as e:
                    pass
        
        try:
            controller_url = 'http://127.0.0.1:9090'
            secret = '123456'
            headers = {'Authorization': f'Bearer {secret}'}
            
            try:
                version_response = requests.get(f'{controller_url}/version', headers=headers, timeout=2)
                if version_response.status_code == 200:
                    status['version'] = version_response.json().get('version')
            except Exception as e:
                pass
            
            try:
                config_response = requests.get(f'{controller_url}/configs', headers=headers, timeout=2)
                if config_response.status_code == 200:
                    config_data = config_response.json()
                    status['mode'] = config_data.get('mode')
                    status['mixed_port'] = config_data.get('mixed-port')
                    status['allow_lan'] = config_data.get('allow-lan', False)
                    tun_config = config_data.get('tun', {})
                    status['tun_enabled'] = tun_config.get('enable', False) if isinstance(tun_config, dict) else False
            except Exception as e:
                pass
        except Exception as e:
            pass
        
        result = {
            'success': True,
            'status': status
        }
        cache['status']['data'] = result
        cache['status']['time'] = time.time()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    current_time = time.time()
    if cache['logs']['data'] and (current_time - cache['logs']['time']) < CACHE_TTL:
        return jsonify(cache['logs']['data'])
    
    try:
        logs = []
        source = 'file'
        try:
            result = subprocess.run(['journalctl', '-u', 'mihomo', '-n', '100', '--no-pager'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logs = result.stdout.split('\n')
                source = 'systemd'
        except Exception as e:
            pass
        
        if len(logs) == 0 or len(logs) <= 1:
            log_dir = '/home/admin/.config/mihomo'
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    if filename.endswith('.log'):
                        log_path = os.path.join(log_dir, filename)
                        try:
                            with open(log_path, 'r', encoding='utf-8') as f:
                                lines = f.read().split('\n')
                                logs = lines[-100:]
                                source = 'file'
                                break
                        except Exception as e:
                            pass
        
        result = {
            'success': True,
            'logs': [line for line in logs if line.strip()],
            'source': source
        }
        cache['logs']['data'] = result
        cache['logs']['time'] = time.time()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/traffic', methods=['GET'])
def get_traffic():
    current_time = time.time()
    if cache['traffic']['data'] and (current_time - cache['traffic']['time']) < CACHE_TTL:
        return jsonify(cache['traffic']['data'])
    
    try:
        controller_url = 'http://127.0.0.1:9090'
        secret = '123456'
        headers = {'Authorization': f'Bearer {secret}'} if secret else {}
        
        result = {
            'traffic': {'up': 0, 'down': 0},
            'connections': []
        }
        
        try:
            traffic_response = requests.get(f'{controller_url}/traffic', headers=headers, timeout=2)
            if traffic_response.status_code == 200:
                result['traffic'] = traffic_response.json()
        except Exception as e:
            pass
        
        try:
            connections_response = requests.get(f'{controller_url}/connections', headers=headers, timeout=2)
            if connections_response.status_code == 200:
                data = connections_response.json()
                result['connections'] = data.get('connections', [])
        except Exception as e:
            pass
        
        response_data = {
            'success': True,
            'data': result
        }
        cache['traffic']['data'] = response_data
        cache['traffic']['time'] = time.time()
        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/proxies/runtime', methods=['GET'])
def get_runtime_proxies():
    try:
        controller_url = 'http://127.0.0.1:9090'
        secret = '123456'
        headers = {'Authorization': f'Bearer {secret}'}
        
        response = requests.get(f'{controller_url}/proxies', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            proxy_groups = []
            proxies = data.get('proxies', {})
            
            for name, proxy in proxies.items():
                if proxy.get('type') == 'Selector':
                    proxy_groups.append({
                        'name': name,
                        'type': proxy.get('type'),
                        'now': proxy.get('now'),
                        'all': proxy.get('all', [])
                    })
            
            return jsonify({
                'success': True,
                'proxyGroups': proxy_groups,
                'allProxies': proxies
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API返回错误: {response.status_code}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/proxies/runtime/<group_name>', methods=['PUT'])
def update_runtime_proxy_group(group_name):
    try:
        data = request.get_json()
        selected_proxy = data.get('name')
        
        if not selected_proxy:
            return jsonify({
                'success': False,
                'error': '请指定代理名称'
            })
        
        controller_url = 'http://127.0.0.1:9090'
        secret = '123456'
        headers = {'Authorization': f'Bearer {secret}'}
        
        response = requests.put(
            f'{controller_url}/proxies/{group_name}',
            headers=headers,
            json={'name': selected_proxy},
            timeout=5
        )
        
        if response.status_code == 204:
            return jsonify({
                'success': True,
                'message': f'代理组 "{group_name}" 已切换到 "{selected_proxy}"'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API返回错误: {response.status_code}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/restart', methods=['POST'])
def restart():
    success, message = restart_mihomo()
    return jsonify({
        'success': success,
        'message': message
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
