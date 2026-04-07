from flask import Flask, render_template, jsonify, request
import yaml
import os
import subprocess
import shutil

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
        result = subprocess.run(['systemctl', 'restart', 'mihomo'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, 'Mihomo 服务重启成功'
        else:
            return False, f'重启失败: {result.stderr}'
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
        config = data.get('config', {})
        save_config(config)
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
