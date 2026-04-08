# 技术栈文档

## 后端技术

### Python 3.x
项目使用 Python 3.x 作为主要开发语言。

### Flask 框架
- **用途**: Web 后端框架
- **版本**: 最新稳定版
- **功能**:
  - 路由管理
  - 请求/响应处理
  - 模板渲染
  - JSON API 支持

### PyYAML
- **用途**: YAML 配置文件解析
- **功能**:
  - 读取 Mihomo 配置文件
  - 写入配置文件
  - 支持 Unicode 字符

### Requests
- **用途**: HTTP 请求库
- **功能**:
  - 与 Mihomo REST API 通信
  - 获取运行时代理信息
  - 切换代理节点

### Subprocess
- **用途**: 执行系统命令
- **功能**:
  - 获取进程信息 (ps)
  - 获取网络端口 (netstat/ss)
  - 重启 Mihomo 服务
  - 获取日志 (journalctl)

### OS & Shutil
- **用途**: 文件系统操作
- **功能**:
  - 文件读取/写入
  - 配置文件备份
  - 目录操作

## 前端技术

### HTML5
- **用途**: 页面结构
- **功能**:
  - 语义化标签
  - 表单元素
  - 响应式布局

### CSS3
- **用途**: 页面样式
- **功能**:
  - 自定义样式
  - 动画效果
  - Flexbox 布局
  - CSS 变量

### Bootstrap 5.3.2
- **用途**: UI 组件库
- **CDN**: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css`
- **功能**:
  - 响应式网格系统
  - 预构建组件（卡片、按钮、表单等）
  - 模态框
  - 工具类

### Bootstrap Icons 1.11.1
- **用途**: 图标库
- **CDN**: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css`
- **功能**:
  - 丰富的图标集合
  - 易于使用

### JavaScript (ES6+)
- **用途**: 前端逻辑
- **功能**:
  - 异步操作 (async/await)
  - DOM 操作
  - 事件处理
  - Fetch API

### Fetch API
- **用途**: 网络请求
- **功能**:
  - 与后端 API 通信
  - 异步数据获取
  - JSON 数据处理

## 外部服务

### Mihomo (Clash)
- **用途**: 代理核心服务
- **可执行文件**: `/usr/local/bin/mihomo`
- **配置目录**: `/home/admin/.config/mihomo`
- **功能**:
  - 代理流量处理
  - 规则匹配
  - 节点选择
  - REST API 提供

### Mihomo REST API
- **地址**: `http://127.0.0.1:9090`
- **认证**: Bearer Token (secret: 123456)
- **主要端点**:
  - `/version` - 获取版本信息
  - `/configs` - 获取运行配置
  - `/proxies` - 获取代理列表
  - `/proxies/{name}` - 切换代理
  - `/traffic` - 获取流量统计
  - `/connections` - 获取连接列表

## 系统工具

### ps
- **用途**: 进程查看
- **功能**: 获取 Mihomo 进程信息（PID、CPU、内存等）

### netstat / ss
- **用途**: 网络端口查看
- **功能**: 获取 Mihomo 监听的端口

### kill
- **用途**: 进程管理
- **功能**: 重启 Mihomo 服务时杀掉旧进程

### journalctl
- **用途**: 系统日志
- **功能**: 获取 Mihomo 服务日志

## 开发工具

### Git
- **用途**: 版本控制
- **功能**:
  - 代码版本管理
  - 分支管理
  - 提交历史

### 浏览器开发者工具
- **用途**: 前端调试
- **功能**:
  - Console 日志
  - Network 监控
  - DOM 检查
  - JavaScript 调试

## 依赖库安装

### Python 依赖
```bash
pip install flask pyyaml requests
```

### 前端依赖
- 通过 CDN 引入，无需本地安装

## 架构模式

### 前后端分离
- 后端提供 REST API
- 前端通过 Fetch API 调用
- JSON 数据交换格式

### 单页应用 (SPA)
- 所有页面在一个 HTML 文件中
- 通过 JavaScript 切换内容
- 无需页面刷新

### 缓存机制
- 后端简单缓存（2秒 TTL）
- 减少重复请求
- 提高响应速度

## 安全性考虑

- 内部网络使用（不建议公网暴露）
- Mihomo API 使用 Bearer Token 认证
- 配置文件备份机制
- 无用户认证系统（基于网络信任）
