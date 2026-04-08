from flask import Flask, render_template, jsonify, request, make_response
import yaml
import os
import subprocess
import shutil
import time
import shlex
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

CONFIG_PATH = '/home/admin/.config/mihomo/config.yaml'
BACKUP_PATH = '/home/admin/.config/mihomo/config.yaml.backup'

# Mihomo API 配置
MIHOMO_CONTROLLER_URL = 'http://127.0.0.1:9090'
MIHOMO_SECRET = '123456'
MIHOMO_HEADERS = {'Authorization': f'Bearer {MIHOMO_SECRET}'}

# 缓存机制（优化性能）
cache = {
    'status': {'data': None, 'time': 0},
    'logs': {'data': None, 'time': 0},
    'traffic': {'data': None, 'time': 0},
    'config': {'data': None, 'time': 0}  # 新增：配置缓存
}
CACHE_TTL = 10  # 缓存10秒，与前端刷新间隔匹配


def reload_mihomo_config():
    """通过 Mihomo API 热重载配置，避免进程重启"""
    try:
        # 1. 读取当前配置文件
        config = load_config()
        
        # 2. 通过 PUT 方法发送完整配置热重载
        response = requests.put(
            f'{MIHOMO_CONTROLLER_URL}/configs',
            headers={
                'Authorization': f'Bearer {MIHOMO_SECRET}',
                'Content-Type': 'application/json'
            },
            json=config,
            timeout=5
        )
        if response.status_code in [200, 204]:
            return True, 'Mihomo 配置热重载成功'
        else:
            return False, f'热重载失败: HTTP {response.status_code}'
    except Exception as e:
        return False, f'热重载异常: {str(e)}'


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
    """清除所有缓存"""
    cache['status']['data'] = None
    cache['status']['time'] = 0
    cache['logs']['data'] = None
    cache['logs']['time'] = 0
    cache['traffic']['data'] = None
    cache['traffic']['time'] = 0
    cache['config']['data'] = None
    cache['config']['time'] = 0


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
        # 直接使用进程方式重启，不使用 systemctl 避免超时
        # 找到 mihomo 进程
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        mihomo_pids = []
        mihomo_cmd = None
        for line in ps_result.stdout.split('\n'):
            if 'mihomo' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    mihomo_pids.append(parts[1])
                    # 保存完整命令用于重启
                    if not mihomo_cmd:
                        idx = line.find('/usr/local/bin/mihomo')
                        if idx != -1:
                            mihomo_cmd = line[idx:].strip()
        
        if not mihomo_pids:
            return False, '重启失败：未找到 mihomo 进程'
        
        # 杀掉进程
        for pid in mihomo_pids:
            subprocess.run(['kill', '-9', pid], capture_output=True)
        
        # 等待一下
        time.sleep(1)
        
        # 重新启动 mihomo
        mihomo_path = '/usr/local/bin/mihomo'
        config_dir = '/home/admin/.config/mihomo'
        if not os.path.exists(mihomo_path) or not os.path.exists(config_dir):
            return False, '重启失败：找不到 mihomo 可执行文件或配置目录'
        
        # 使用与原进程相同的参数启动
        if mihomo_cmd:
            # 使用完整命令
            args = shlex.split(mihomo_cmd)
            subprocess.Popen(args,
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
        else:
            # 使用默认参数
            subprocess.Popen([mihomo_path, '-d', config_dir], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
        
        return True, 'Mihomo 服务重启成功'
        
    except Exception as e:
        return False, f'重启失败: {str(e)}'


@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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
    # 检查缓存
    current_time = time.time()
    if cache['config']['data'] and (current_time - cache['config']['time']) < CACHE_TTL:
        return jsonify(cache['config']['data'])
    
    try:
        config = load_config()
        result = {
            'success': True,
            'config': config
        }
        # 保存到缓存
        cache['config']['data'] = result
        cache['config']['time'] = time.time()
        return jsonify(result)
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
        # 加载原始配置，确保不丢失任何配置项
        original_config = load_config()
        
        # 合并配置：只更新新配置中有值的部分，保留原始配置的其他所有项
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
        
        # 热重载配置，避免进程重启
        reload_success, reload_message = reload_mihomo_config()
        if reload_success:
            message = f'配置保存成功，{reload_message}'
        else:
            message = f'配置保存成功，但{reload_message}（请手动重启服务）'
        
        return jsonify({
            'success': True,
            'message': message
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
    # 检查缓存
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
        
        # 使用 pgrep 更高效地查找 mihomo 进程
        try:
            pgrep_result = subprocess.run(['pgrep', '-a', 'mihomo'], capture_output=True, text=True, timeout=2)
            if pgrep_result.returncode == 0 and pgrep_result.stdout.strip():
                lines = pgrep_result.stdout.strip().split('\n')
                for line in lines:
                    if 'grep' not in line:
                        parts = line.split(maxsplit=1)
                        if len(parts) >= 1:
                            status['pid'] = parts[0]
                            status['running'] = True
                            if len(parts) > 1:
                                status['command'] = parts[1]
                        break
        except Exception:
            pass
        
        # 如果 pgrep 失败，回退到 ps 命令
        if not status['running']:
            try:
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=3)
                for line in ps_result.stdout.split('\n'):
                    if 'mihomo' in line and 'grep' not in line:
                        parts = line.split()
                        if len(parts) > 10:
                            status['running'] = True
                            status['pid'] = parts[1]
                            status['cpu'] = parts[2]
                            status['memory'] = parts[3]
                            status['command'] = ' '.join(parts[10:])
                            break
            except Exception:
                pass
        
        # 获取进程详细信息
        if status['pid']:
            try:
                # 使用单个命令获取 CPU、内存和启动时间
                stat_result = subprocess.run(
                    ['ps', '-p', status['pid'], '-o', 'pcpu,pmem,lstart=', '--no-headers'],
                    capture_output=True, text=True, timeout=2
                )
                if stat_result.returncode == 0:
                    parts = stat_result.stdout.strip().split()
                    if len(parts) >= 3:
                        status['cpu'] = parts[0]
                        status['memory'] = parts[1]
                        status['uptime'] = ' '.join(parts[2:])
            except Exception:
                pass
            
            # 获取监听端口 - 只查询该 PID 的端口
            try:
                # 使用 lsof 直接查询特定 PID 的端口（更快）
                lsof_result = subprocess.run(
                    ['lsof', '-a', '-p', status['pid'], '-i', 'TCP', '-s', 'TCP:LISTEN', '-P', '-n'],
                    capture_output=True, text=True, timeout=2
                )
                if lsof_result.returncode == 0:
                    for line in lsof_result.stdout.split('\n')[1:]:  # 跳过标题行
                        if 'LISTEN' in line:
                            parts = line.split()
                            if len(parts) >= 9:
                                addr = parts[8]
                                if ':' in addr:
                                    port = addr.split(':')[-1]
                                    if port not in status['ports']:
                                        status['ports'].append(port)
            except Exception:
                # 回退到 netstat
                try:
                    netstat_result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True, timeout=3)
                    for line in netstat_result.stdout.split('\n'):
                        if status['pid'] in line:
                            parts = line.split()
                            if len(parts) > 3:
                                local_addr = parts[3]
                                if ':' in local_addr:
                                    port = local_addr.split(':')[-1]
                                    if port not in status['ports']:
                                        status['ports'].append(port)
                except Exception:
                    pass
        
        # 并发请求 Mihomo API
        def fetch_mihomo_info():
            controller_url = 'http://127.0.0.1:9090'
            secret = '123456'
            headers = {'Authorization': f'Bearer {secret}'}
            
            def fetch_version():
                try:
                    resp = requests.get(f'{controller_url}/version', headers=headers, timeout=1)
                    if resp.status_code == 200:
                        return ('version', resp.json().get('version'))
                except Exception:
                    pass
                return ('version', None)
            
            def fetch_config():
                try:
                    resp = requests.get(f'{controller_url}/configs', headers=headers, timeout=1)
                    if resp.status_code == 200:
                        data = resp.json()
                        return ('config', {
                            'mode': data.get('mode'),
                            'mixed_port': data.get('mixed-port'),
                            'allow_lan': data.get('allow-lan', False),
                            'tun_enabled': data.get('tun', {}).get('enable', False) if isinstance(data.get('tun'), dict) else False
                        })
                except Exception:
                    pass
                return ('config', None)
            
            # 使用线程池并发请求
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(fetch_version), executor.submit(fetch_config)]
                for future in as_completed(futures):
                    key, value = future.result()
                    if key == 'version' and value:
                        status['version'] = value
                    elif key == 'config' and value:
                        status['mode'] = value['mode']
                        status['mixed_port'] = value['mixed_port']
                        status['allow_lan'] = value['allow_lan']
                        status['tun_enabled'] = value['tun_enabled']
        
        # 只在 mihomo 运行时才请求 API
        if status['running']:
            fetch_mihomo_info()
        
        result = {
            'success': True,
            'status': status
        }
        # 保存到缓存
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
    # 检查缓存
    current_time = time.time()
    if cache['logs']['data'] and (current_time - cache['logs']['time']) < CACHE_TTL:
        return jsonify(cache['logs']['data'])
    
    try:
        # 获取 mihomo 日志
        # 尝试从 systemd journal 获取
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
        
        # 如果 systemd 没有，尝试从 mihomo 的日志目录获取
        if len(logs) == 0 or len(logs) <= 1:
            log_dir = '/home/admin/.config/mihomo'
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    if filename.endswith('.log'):
                        log_path = os.path.join(log_dir, filename)
                        try:
                            with open(log_path, 'r', encoding='utf-8') as f:
                                # 取最后 100 行
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
        # 保存到缓存
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
    # 检查缓存
    current_time = time.time()
    if cache['traffic']['data'] and (current_time - cache['traffic']['time']) < CACHE_TTL:
        return jsonify(cache['traffic']['data'])
    
    try:
        # 从 mihomo API 获取流量和连接信息
        controller_url = 'http://127.0.0.1:9090'
        secret = '123456'
        
        headers = {'Authorization': f'Bearer {secret}'} if secret else {}
        
        result = {
            'traffic': {'up': 0, 'down': 0},
            'connections': []
        }
        
        # 获取流量统计
        try:
            traffic_response = requests.get(f'{controller_url}/traffic', headers=headers, timeout=2)
            if traffic_response.status_code == 200:
                result['traffic'] = traffic_response.json()
        except Exception as e:
            pass
        
        # 获取连接列表
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
        # 保存到缓存
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
    # 优先使用热重载，避免进程重启
    success, message = reload_mihomo_config()
    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        # 热重载失败时回退到进程重启
        success, message = restart_mihomo()
        return jsonify({
            'success': success,
            'message': f'{message} (热重载失败，已回退到进程重启)'
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # 关闭debug模式避免自动重启导致ERR_ABORTED
