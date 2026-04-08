# 快速入门指南

## 前置条件

### 系统要求
- Linux 操作系统
- Python 3.6+
- Mihomo (Clash) 已安装并运行

### 依赖库
```bash
pip install flask pyyaml requests
```

## 快速启动

### 1. 进入项目目录
```bash
cd /home/admin/mihomo-webui
```

### 2. 启动 Flask 服务
```bash
python3 app.py
```

服务将在以下地址启动：
- 本地访问: http://127.0.0.1:5000
- 局域网访问: http://<服务器IP>:5000

### 3. 访问 WebUI
在浏览器中打开上述地址即可使用。

## 项目配置

### 配置文件路径
在 `app.py` 中修改以下常量（如果需要）：

```python
CONFIG_PATH = '/home/admin/.config/mihomo/config.yaml'
BACKUP_PATH = '/home/admin/.config/mihomo/config.yaml.backup'
```

### Mihomo API 连接
在 `app.py` 中修改以下参数（如果需要）：

```python
controller_url = 'http://127.0.0.1:9090'
secret = '123456'
```

## 开发流程

### Git 版本控制
项目使用 Git 进行版本控制：

```bash
# 查看状态
git status

# 查看修改
git diff

# 提交修改
git add <文件>
git commit -m "提交信息"

# 查看历史
git log
```

### 开发调试

#### 后端调试
1. Flask 服务以 debug 模式启动，代码修改后会自动重载
2. 查看终端输出了解请求和错误信息
3. 使用 print() 或 logging 输出调试信息

#### 前端调试
1. 打开浏览器开发者工具 (F12)
2. 查看 Console 标签页的日志
3. 查看 Network 标签页的 API 请求
4. 使用断点调试 JavaScript

### 常见开发任务

#### 添加新的 API 端点
在 `app.py` 中添加新的路由：

```python
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    try:
        # 你的逻辑
        return jsonify({
            'success': True,
            'data': ...
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
```

#### 添加新的前端功能
在 `templates/index.html` 中：
1. 添加 HTML 元素
2. 在 `<script>` 标签中添加 JavaScript 函数
3. 在 `DOMContentLoaded` 事件中绑定事件

#### 修改样式
在 `templates/index.html` 的 `<style>` 标签中添加或修改 CSS。

## 故障排查

### 问题：WebUI 无法访问

**检查清单**：
1. Flask 服务是否正在运行？
   ```bash
   ps aux | grep python
   ```
2. 端口 5000 是否被占用？
   ```bash
   netstat -tlnp | grep 5000
   ```
3. 防火墙是否允许访问？
4. 浏览器控制台是否有错误？

**解决方法**：
```bash
# 杀掉占用端口的进程
kill -9 <PID>

# 重新启动服务
cd /home/admin/mihomo-webui
python3 app.py
```

### 问题：配置无法保存

**检查清单**：
1. 配置文件路径是否正确？
2. 配置文件权限是否正确？
   ```bash
   ls -l /home/admin/.config/mihomo/config.yaml
   ```
3. 磁盘是否已满？
   ```bash
   df -h
   ```

**解决方法**：
```bash
# 修改文件权限
chmod 644 /home/admin/.config/mihomo/config.yaml
```

### 问题：Mihomo 状态无法获取

**检查清单**：
1. Mihomo 服务是否正在运行？
   ```bash
   ps aux | grep mihomo
   ```
2. Mihomo REST API 是否可访问？
   ```bash
   curl http://127.0.0.1:9090/version
   ```
3. API 口令是否正确？

**解决方法**：
```bash
# 重启 Mihomo 服务（如果使用 systemd）
sudo systemctl restart mihomo

# 或者手动重启
pkill -9 mihomo
/usr/local/bin/mihomo -d /home/admin/.config/mihomo &
```

### 问题：页面无法加载或跳转

**常见原因**：
1. JavaScript 语法错误
2. 事件绑定位置错误（应在 DOMContentLoaded 内）
3. 元素 ID 冲突
4. 函数名重复

**排查步骤**：
1. 打开浏览器开发者工具 (F12)
2. 查看 Console 标签页的错误信息
3. 检查 Network 标签页的 API 请求
4. 使用调试断点定位问题

## 生产部署

### 使用 Gunicorn（推荐）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Systemd 服务

创建 `/etc/systemd/system/mihomo-webui.service`：

```ini
[Unit]
Description=Mihomo WebUI
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/mihomo-webui
ExecStart=/usr/bin/python3 /home/admin/mihomo-webui/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable mihomo-webui
sudo systemctl start mihomo-webui
```

### 反向代理（Nginx）

配置 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 代码规范

### Python 代码规范
- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 函数和类使用 docstring
- 适当添加注释

### JavaScript 代码规范
- 使用 ES6+ 语法
- 使用 const/let 而非 var
- 事件绑定必须在 DOMContentLoaded 内
- 使用 async/await 处理异步

### Git 提交规范
- 提交信息使用中文
- 格式：`<类型>: <描述>`
- 类型：feat（新功能）、fix（修复）、refactor（重构）、docs（文档）

示例：
```
fix: 修复事件绑定位置错误
feat: 添加流量监控功能
docs: 更新项目文档
```

## 学习资源

### Flask
- 官方文档: https://flask.palletsprojects.com/
- 中文教程: https://dormousehole.readthedocs.io/

### Bootstrap
- 官方文档: https://getbootstrap.com/docs/5.3/
- 图标库: https://icons.getbootstrap.com/

### Mihomo
- GitHub: https://github.com/MetaCubeX/mihomo
- 文档: https://wiki.metacubex.one/

### YAML
- 官方文档: https://yaml.org/
- 快速入门: https://www.runoob.com/w3cnote/yaml-intro.html

## 获取帮助

如果遇到问题：
1. 查看本文档的故障排查部分
2. 检查浏览器控制台和后端日志
3. 查看 Git 历史了解之前的修改
4. 参考相关技术文档
