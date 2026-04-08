# Mihomo WebUI 项目概览

## 项目简介

Mihomo WebUI 是一个用于管理 Mihomo (Clash) 代理配置的可视化 Web 界面。该项目提供了一个用户友好的图形界面，允许用户轻松管理代理配置、规则、代理组，并实时监控系统状态和流量。

## 核心功能

### 1. 配置管理
- 基本设置（端口、网络、运行模式等）
- 外部控制设置（REST API、口令等）
- TUN 设置（虚拟网卡配置）
- DNS 设置
- 嗅探设置

### 2. 策略规则管理
- 代理组配置（可视化添加、编辑、删除）
- 节点选择（运行时代理组节点切换）
- 规则管理（可视化规则编辑）
- 规则流程图展示

### 3. 系统监控
- 实时状态监控（CPU、内存、端口等）
- 流量监控（上传/下载速度、活跃连接）
- 日志查看（实时日志显示）

### 4. 其他功能
- 原始配置编辑器
- 配置导入导出
- 服务重启
- 自动刷新

## 项目结构

```
mihomo-webui/
├── app.py                      # Flask 后端主文件
├── templates/
│   └── index.html             # 完整的前端页面
├── config/                    # 配置文件目录
│   └── config.yaml            # 项目配置文件
└── README.md                  # 项目说明
```

## 工作原理

### 后端（Flask）
- 提供 REST API 接口
- 读取和写入 Mihomo 配置文件
- 通过 Mihomo REST API 获取运行时数据
- 执行系统命令获取进程信息
- 简单的缓存机制提高性能

### 前端（Bootstrap + JavaScript）
- 响应式单页应用
- 异步 API 调用
- 实时数据更新
- 友好的用户交互

## 配置文件路径

- Mihomo 配置文件: `/home/admin/.config/mihomo/config.yaml`
- 配置备份文件: `/home/admin/.config/mihomo/config.yaml.backup`

## Mihomo REST API 连接

- 默认地址: `http://127.0.0.1:9090`
- 认证口令: `123456`

## WebUI 访问地址

- 本地访问: `http://127.0.0.1:5000`
- 局域网访问: `http://<服务器IP>:5000`

## 开发和维护

### 主要技术负责人
- 了解 Flask 框架
- 熟悉 JavaScript 和 Bootstrap
- 了解 Mihomo/Clash 配置格式
- 熟悉 Linux 系统命令

### 关键文件
- `app.py` - 后端逻辑
- `templates/index.html` - 前端界面和逻辑

### 常见问题排查
1. 检查 Mihomo 服务是否运行
2. 检查配置文件路径是否正确
3. 检查 Mihomo REST API 是否可访问
4. 检查端口 5000 是否被占用
