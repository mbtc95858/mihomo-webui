# API 文档

## 概述

本文档描述 Mihomo WebUI 后端提供的所有 REST API 接口。

**基础 URL**: `http://<server-ip>:5000`

**数据格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功信息（可选）",
  ... 其他数据
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误描述"
}
```

---

## 页面路由

### GET /
渲染主页面

**响应**: HTML 页面

---

## 配置管理 API

### GET /api/config/raw
获取原始配置文件内容

**响应示例**:
```json
{
  "success": true,
  "config": "mixed-port: 7890\nallow-lan: true\n..."
}
```

### POST /api/config/raw
保存原始配置文件内容

**请求体**:
```json
{
  "config": "mixed-port: 7890\nallow-lan: true\n..."
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "配置保存成功"
}
```

### GET /api/config
获取解析后的配置对象

**响应示例**:
```json
{
  "success": true,
  "config": {
    "mixed-port": 7890,
    "allow-lan": true,
    "mode": "rule",
    "proxies": [...],
    "proxy-groups": [...],
    "rules": [...]
  }
}
```

### POST /api/config
更新配置（深度合并）

**请求体**:
```json
{
  "config": {
    "mixed-port": 7890,
    "allow-lan": false
  }
}
```

**说明**: 只会更新提供的字段，保留其他配置项

**响应示例**:
```json
{
  "success": true,
  "message": "配置保存成功"
}
```

---

## 代理相关 API

### GET /api/proxies
获取代理和代理组列表

**响应示例**:
```json
{
  "success": true,
  "proxies": [...],
  "proxyGroups": [...]
}
```

### POST /api/proxy-groups
更新代理组配置

**请求体**:
```json
{
  "proxyGroups": [
    {
      "name": "代理组1",
      "type": "select",
      "proxies": ["节点1", "节点2"]
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "代理组更新成功"
}
```

---

## 规则相关 API

### GET /api/rules
获取规则和规则提供程序

**响应示例**:
```json
{
  "success": true,
  "rules": [
    "DOMAIN-SUFFIX,google.com,PROXY",
    "MATCH,DIRECT"
  ],
  "ruleProviders": {...}
}
```

### POST /api/rules
更新规则配置

**请求体**:
```json
{
  "rules": [
    "DOMAIN-SUFFIX,google.com,PROXY",
    "MATCH,DIRECT"
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "规则更新成功"
}
```

---

## 状态监控 API

### GET /api/status
获取系统和 Mihomo 状态

**缓存**: 2秒 TTL

**响应示例**:
```json
{
  "success": true,
  "status": {
    "running": true,
    "pid": "12345",
    "cpu": "0.5",
    "memory": "1.2",
    "uptime": "Tue Apr  7 22:36:48 2026",
    "command": "/usr/local/bin/mihomo -d /home/admin/.config/mihomo",
    "ports": ["7890", "9090"],
    "version": "v1.19.21",
    "mode": "rule",
    "mixed_port": 7890,
    "allow_lan": true,
    "tun_enabled": true
  }
}
```

**字段说明**:
- `running`: Mihomo 是否正在运行
- `pid`: 进程 ID
- `cpu`: CPU 使用率百分比
- `memory`: 内存使用率百分比
- `uptime`: 进程启动时间
- `command`: 完整命令行
- `ports`: 监听的端口列表
- `version`: Mihomo 版本
- `mode`: 运行模式 (rule/global/direct)
- `mixed_port`: 混合代理端口
- `allow_lan`: 是否允许局域网连接
- `tun_enabled`: TUN 模式是否启用

---

## 日志 API

### GET /api/logs
获取 Mihomo 日志

**缓存**: 2秒 TTL

**响应示例**:
```json
{
  "success": true,
  "logs": [
    "日志行1",
    "日志行2"
  ],
  "source": "systemd"
}
```

**来源说明**:
- `systemd`: 从 systemd journal 获取
- `file`: 从日志文件获取

---

## 流量监控 API

### GET /api/traffic
获取流量统计和活跃连接

**缓存**: 2秒 TTL

**响应示例**:
```json
{
  "success": true,
  "data": {
    "traffic": {
      "up": 1024,
      "down": 2048
    },
    "connections": [
      {
        "id": "123",
        "metadata": {
          "network": "tcp",
          "type": "http",
          "host": "example.com",
          "sourceIP": "192.168.1.100",
          "sourcePort": "12345",
          "destinationIP": "93.184.216.34",
          "destinationPort": "443"
        },
        "upload": 1024,
        "download": 2048,
        "chains": ["PROXY", "节点1"]
      }
    ]
  }
}
```

**流量单位**: 字节/秒

---

## 运行时代理 API

### GET /api/proxies/runtime
获取运行时代理组信息（用于节点选择）

**响应示例**:
```json
{
  "success": true,
  "proxyGroups": [
    {
      "name": "PROXY",
      "type": "Selector",
      "now": "节点1",
      "all": ["节点1", "节点2", "节点3"]
    }
  ],
  "allProxies": {...}
}
```

### PUT /api/proxies/runtime/{group_name}
切换代理组的选中节点

**路径参数**:
- `group_name`: 代理组名称（URL 编码）

**请求体**:
```json
{
  "name": "节点1"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "代理组 \"PROXY\" 已切换到 \"节点1\""
}
```

---

## 服务管理 API

### POST /api/restart
重启 Mihomo 服务

**请求**: 无请求体

**响应示例**:
```json
{
  "success": true,
  "message": "Mihomo 服务重启成功"
}
```

**说明**: 
1. 找到并杀掉现有 Mihomo 进程
2. 等待 1 秒
3. 使用相同参数重新启动

---

## 错误处理

所有 API 在出错时都会返回:
- HTTP 状态码: 200（即使出错也是 200）
- `success`: false
- `error`: 错误描述

常见错误:
- 配置文件不存在
- YAML 解析失败
- Mihomo API 连接失败
- 系统命令执行失败
- 权限不足

---

## 使用示例

### JavaScript Fetch 示例

```javascript
// 获取配置
fetch('/api/config')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('配置:', data.config);
    }
  });

// 保存配置
fetch('/api/config', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    config: { 'mixed-port': 7890 }
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('保存成功');
    }
  });

// 切换代理节点
fetch('/api/proxies/runtime/PROXY', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: '节点1' })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('切换成功');
    }
  });
```

### Python requests 示例

```python
import requests

# 获取状态
response = requests.get('http://localhost:5000/api/status')
data = response.json()
if data['success']:
    print('Mihomo 运行状态:', data['status']['running'])

# 重启服务
response = requests.post('http://localhost:5000/api/restart')
data = response.json()
print(data['message'])
```
