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
        # 方法1：尝试使用 systemctl（不需要 sudo，因为当前用户可能已经有权限）
        result = subprocess.run(['systemctl', 'restart', 'mihomo'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, 'Mihomo 服务重启成功'
        
        # 方法2：如果不行，直接找到进程并重启
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
        
        if mihomo_pids:
            # 杀掉进程
            for pid in mihomo_pids:
                subprocess.run(['kill', '-9', pid], capture_output=True)
            
            # 等待一下
            time.sleep(1)
            
            # 重新启动 mihomo
            mihomo_path = '/usr/local/bin/mihomo'
            config_dir = '/home/admin/.config/mihomo'
            if os.path.exists(mihomo_path) and os.path.exists(config_dir):
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
            else:
                return False, '重启失败：找不到 mihomo 可执行文件或配置目录'
        
        return False, '重启失败：未找到 mihomo 进程'
        
    except subprocess.TimeoutExpired:
        return False, '重启失败：操作超时'
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


@app.route('/api/restart', methods=['POST'])
def restart():
    success, message = restart_mihomo()
    return jsonify({
        'success': success,
        'message': message
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
