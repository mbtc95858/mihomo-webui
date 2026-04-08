# Mihomo WebUI 项目文档

欢迎来到 Mihomo WebUI 项目文档！本文件夹包含了帮助新开发者快速上手项目的所有必要文档。

## 📚 文档列表

### 1. [项目概览 (PROJECT_OVERVIEW.md)](./PROJECT_OVERVIEW.md)
- 项目简介和核心功能
- 项目结构说明
- 工作原理介绍
- 配置文件路径
- 开发和维护指南

### 2. [技术栈 (TECH_STACK.md)](./TECH_STACK.md)
- 后端技术详解（Python、Flask、PyYAML等）
- 前端技术详解（HTML5、CSS3、Bootstrap、JavaScript等）
- 外部服务说明（Mihomo REST API）
- 系统工具说明
- 依赖库安装指南
- 架构模式介绍
- 安全性考虑

### 3. [API 文档 (API.md)](./API.md)
- 所有 REST API 端点详细说明
- 请求/响应格式示例
- 配置管理 API
- 代理相关 API
- 规则相关 API
- 状态监控 API
- 日志 API
- 流量监控 API
- 运行时代理 API
- 服务管理 API
- 使用示例（JavaScript 和 Python）

### 4. [快速入门指南 (QUICKSTART.md)](./QUICKSTART.md)
- 前置条件和系统要求
- 快速启动步骤
- 项目配置说明
- 开发流程（Git、调试、常见任务）
- 故障排查指南
- 生产部署方案（Gunicorn、Systemd、Nginx）
- 代码规范
- 学习资源
- 获取帮助

## 🚀 快速开始

如果你是第一次接触这个项目，建议按以下顺序阅读：

1. **首先阅读** [项目概览](./PROJECT_OVERVIEW.md) - 了解项目是什么，做什么的
2. **然后阅读** [快速入门指南](./QUICKSTART.md) - 了解如何启动和运行项目
3. **需要时查阅** [技术栈](./TECH_STACK.md) - 深入了解技术细节
4. **开发时参考** [API 文档](./API.md) - 了解后端接口

## 📋 项目关键信息

- **项目位置**: `/home/admin/mihomo-webui`
- **WebUI 地址**: http://<服务器IP>:5000
- **Mihomo 配置**: `/home/admin/.config/mihomo/config.yaml`
- **Mihomo API**: http://127.0.0.1:9090
- **API 口令**: 123456

## 🔧 常用命令

```bash
# 进入项目目录
cd /home/admin/mihomo-webui

# 启动开发服务
python3 app.py

# 查看 Git 状态
git status

# 查看 Git 历史
git log --oneline
```

## 📞 获取帮助

如果在阅读文档或开发过程中遇到问题：
1. 查看对应文档的故障排查部分
2. 检查 Git 历史了解之前的修改
3. 参考相关技术文档

## 📝 文档维护

这些文档应该随着项目的发展而更新。当进行以下操作时，请记得更新文档：
- 添加新功能
- 修改现有 API
- 改变项目结构
- 更新依赖库版本
- 修改配置方式

---

**祝开发顺利！** 🎉
