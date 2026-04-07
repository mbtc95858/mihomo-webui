from flask import Flask, render_template, jsonify, request
import yaml
import os
import subprocess
import shutil

app = Flask(__name__)

CONFIG_PATH = '/home/admin/.config/mihomo/config.yaml'
BACKUP_PATH = '/home/admin/.config/mihomo/config.yaml.backup'


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


def save_config(content):
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


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


@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        content = load_config()
        return jsonify({
            'success': True,
            'config': content
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
        content = data.get('config', '')
        save_config(content)
        return jsonify({
            'success': True,
            'message': '配置保存成功'
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
