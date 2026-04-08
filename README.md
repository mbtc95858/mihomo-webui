# Mihomo WebUI

Mihomo 代理的 Web 管理界面，支持配置管理、代理组管理和规则管理。

## 功能特性

- 📝 **配置管理** - 可视化编辑 config.yaml
- 🔄 **代理组管理** - 轻松切换代理节点
- 📋 **规则管理** - 灵活配置分流规则
- 🚀 **一键重启** - 保存配置后自动重启服务
- 📊 **状态监控** - 实时查看代理运行状态
- 📈 **流量统计** - 查看流量使用情况
- 📜 **日志查看** - 查看 Mihomo 运行日志

## 快速开始

### 安装

```bash
git clone https://github.com/mbtc95858/mihomo-webui.git
cd mihomo-webui
pip install -r requirements.txt
```

### 运行

```bash
python app.py
```

然后访问 http://localhost:5000

### 配置 Mihomo

确保 Mihomo 配置了以下参数：

```yaml
external-controller: 0.0.0.0:9090
secret: '123456'
```

## 技术栈

- **后端**: Python Flask
- **前端**: 原生 HTML/CSS/JavaScript
- **通信**: RESTful API

## API 接口

详细的 API 文档请查看 [project-overview/API.md](project-overview/API.md)

## 项目结构

```
mihomo-webui/
├── app.py                      # Flask 后端主程序
├── templates/
│   └── index.html              # 前端页面
├── project-overview/           # 项目文档
│   ├── README.md
│   ├── API.md
│   ├── QUICKSTART.md
│   └── TECH_STACK.md
└── README.md
```

## 版本

当前版本: v1.0.0

## 许可证

MIT License
