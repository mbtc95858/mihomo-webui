from flask import Flask, render_template, jsonify, request
import yaml
import os
import subprocess
import shutil
import time
import shlex

app = Flask(__name__)

CONFIG_PATH = '/home/admin/.config/mihomo/config.yaml'
BACKUP_PATH = '/home/admin/.config/mihomo/config.yaml.backup'


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


def save_config_raw(content):
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def save_config(config):
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


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
    try:
        status = {
            'running': False,
            'pid': None,
            'cpu': None,
            'memory': None,
            'uptime': None,
            'command': None,
            'ports': []
        }
        
        # 获取进程信息
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in ps_result.stdout.split('\n'):
            if 'mihomo' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 10:
                    status['running'] = True
                    status['pid'] = parts[1]
                    status['cpu'] = parts[2]
                    status['memory'] = parts[3]
                    status['command'] = ' '.join(parts[10:])
                    
                    # 获取进程启动时间
                    try:
                        stat_result = subprocess.run(['ps', '-p', parts[1], '-o', 'lstart='], 
                                                   capture_output=True, text=True)
                        if stat_result.returncode == 0:
                            status['uptime'] = stat_result.stdout.strip()
                    except:
                        pass
        
        # 获取监听端口
        if status['pid']:
            try:
                netstat_result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
                for line in netstat_result.stdout.split('\n'):
                    if status['pid'] in line:
                        parts = line.split()
                        if len(parts) > 3:
                            local_addr = parts[3]
                            if ':' in local_addr:
                                port = local_addr.split(':')[-1]
                                if port not in status['ports']:
                                    status['ports'].append(port)
            except:
                try:
                    ss_result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
                    for line in ss_result.stdout.split('\n'):
                        if status['pid'] in line:
                            parts = line.split()
                            if len(parts) > 4:
                                local_addr = parts[4]
                                if ':' in local_addr:
                                    port = local_addr.split(':')[-1]
                                    if port not in status['ports']:
                                        status['ports'].append(port)
                except:
                    pass
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        # 获取 mihomo 日志
        # 尝试从 systemd journal 获取
        logs = []
        try:
            result = subprocess.run(['journalctl', '-u', 'mihomo', '-n', '100', '--no-pager'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logs = result.stdout.split('\n')
        except:
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
                                break
                        except:
                            pass
        
        return jsonify({
            'success': True,
            'logs': [line for line in logs if line.strip()],
            'source': 'systemd' if len(logs) > 0 and 'journalctl' in str(subprocess.run('which journalctl', shell=True, capture_output=True, text=True).stdout) else 'file'
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
