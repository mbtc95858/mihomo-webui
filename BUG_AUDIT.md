# Mihomo WebUI Bug 审计报告

## 审计时间
2026-04-08

## 审计范围
- app.py（Flask 后端）
- templates/index.html（前端）

---

## Bug 清单

### 【CRITICAL】前端 - 事件绑定在 DOMContentLoaded 外部

**严重级别**: critical  
**所属模块**: 通用  
**复现步骤**:
1. 打开页面
2. 点击某些按钮可能没有反应

**实际表现**:
- 第 1954-1955 行：refreshStatusBtn 和 autoRefreshToggle 的事件绑定
- 第 2007-2035 行：日志功能相关的事件绑定
- 第 2087-2090 行：拓扑图刷新按钮事件绑定
- 第 2204-2241 行：流量监控和详细状态相关的事件绑定
- 这些都在 DOMContentLoaded 外部！

**预期表现**: 所有事件绑定应该在 DOMContentLoaded 内部

**根本原因**: 事件绑定在 DOM 就绪之前执行，元素可能不存在

**涉及文件**: templates/index.html

**修复方案**: 将所有事件绑定移到 DOMContentLoaded 内部

---

### 【CRITICAL】前端 - Modal 初始化在 DOMReady 之前

**严重级别**: critical  
**所属模块**: 通用  
**复现步骤**:
1. 打开页面
2. 打开浏览器控制台

**实际表现**: 可能出现 "Cannot read properties of null (reading 'addEventListener')" 错误

**预期表现**: Modal 应该在 DOM 就绪后初始化

**根本原因**: 第 1254-1255 行在 DOMContentLoaded 之前就调用了 `new bootstrap.Modal()`

**涉及文件**: templates/index.html

**修复方案**: 将 Modal 初始化移到 DOMContentLoaded 内部

---

### 【HIGH】前端 - 重复的事件绑定

**严重级别**: high  
**所属模块**: 状态监控  
**复现步骤**:
1. 打开状态监控页面
2. 多次点击刷新按钮

**实际表现**: 点击一次可能触发多次事件

**预期表现**: 每个事件只绑定一次

**根本原因**: 
- 第 1954-1955 行和第 2231-2240 行重复绑定了 refreshStatusBtn 和 autoRefreshToggle
- 第 2309-2318 行每次 renderProxyNodes() 时都会重新绑定 .proxy-node-select 的事件

**涉及文件**: templates/index.html

**修复方案**: 
1. 删除重复的绑定
2. renderProxyNodes() 中使用事件委托或清理旧事件

---

### 【HIGH】前端 - renderProxyNodes 事件绑定内存泄漏

**严重级别**: high  
**所属模块**: 代理组节点选择  
**复现步骤**:
1. 进入节点选择页面
2. 多次刷新列表
3. 选择节点

**实际表现**: 选择一次节点可能触发多次请求

**预期表现**: 每次选择只触发一次请求

**根本原因**: 第 2309-2318 行每次调用 renderProxyNodes() 都会给所有 .proxy-node-select 元素添加新的事件监听器，但没有清理旧的

**涉及文件**: templates/index.html

**修复方案**: 
- 使用事件委托（委托给父元素）
- 或在重新绑定前移除旧事件监听器

---

### 【MEDIUM】后端 - 配置写入没有原子性

**严重级别**: medium  
**所属模块**: 配置管理  
**复现步骤**:
1. 保存配置
2. 保存过程中断电或进程崩溃

**实际表现**: 配置文件可能损坏或部分写入

**预期表现**: 配置写入应该是原子操作

**根本原因**: save_config() 和 save_config_raw() 直接写入目标文件，没有使用临时文件+重命名方式

**涉及文件**: app.py

**修复方案**: 使用临时文件写入，完成后重命名

---

### 【MEDIUM】后端 - 子进程调用没有统一超时保护

**严重级别**: medium  
**所属模块**: 通用  
**复现步骤**:
1. 系统负载很高时
2. 调用 /api/status 或 /api/logs

**实际表现**: 请求可能长时间挂起

**预期表现**: 所有子进程调用都应该有超时保护

**根本原因**: 
- 第 288 行：ps 调用没有 timeout
- 第 301 行：ps -p 调用没有 timeout
- 第 311 行：netstat 调用没有 timeout
- 第 323 行：ss 调用没有 timeout

**涉及文件**: app.py

**修复方案**: 所有 subprocess.run() 都添加 timeout 参数

---

### 【MEDIUM】后端 - 异常捕获太宽泛

**严重级别**: medium  
**所属模块**: 通用  
**复现步骤**: 代码出现异常时

**实际表现**: 可能吞掉重要的错误信息，难以调试

**预期表现**: 应该捕获具体的异常类型并记录

**根本原因**: 
- 第 305 行：`except:` (空 except)
- 第 321 行：`except:` (空 except)
- 第 333 行：`except:` (空 except)
- 第 347 行：`except:` (空 except)
- 第 360 行：`except:` (空 except)
- 第 362 行：`except:` (空 except)
- 第 396 行：`except:` (空 except)
- 第 412 行：`except:` (空 except)
- 第 455 行：`except:` (空 except)
- 第 464 行：`except:` (空 except)

**涉及文件**: app.py

**修复方案**: 改为 `except Exception as e:` 并适当记录日志

---

### 【MEDIUM】前端 - 没有统一的 fetch 错误处理

**严重级别**: medium  
**所属模块**: 通用  
**复现步骤**: API 调用失败时

**实际表现**: 每个 fetch 都有自己的错误处理，不一致

**预期表现**: 应该有统一的错误处理机制

**根本原因**: 没有封装统一的 fetch 函数

**涉及文件**: templates/index.html

**修复方案**: 封装统一的 apiFetch() 函数

---

### 【MEDIUM】前端 - fetch 调用没有超时

**严重级别**: medium  
**所属模块**: 通用  
**复现步骤**: 网络慢或后端挂起时

**实际表现**: 请求可能无限等待

**预期表现**: 应该有请求超时机制

**根本原因**: 所有 fetch 调用都没有设置 AbortController 或 timeout

**涉及文件**: templates/index.html

**修复方案**: 使用 AbortController 实现超时

---

### 【LOW】后端 - Mihomo API 配置硬编码

**严重级别**: low  
**所属模块**: 通用  
**复现步骤**: 修改 Mihomo 配置时

**实际表现**: 需要修改代码才能更改 API 地址和密钥

**预期表现**: 应该从配置文件读取或使用环境变量

**根本原因**: 
- 第 338-339 行：硬编码 controller_url 和 secret
- 第 440-441 行：重复硬编码
- 第 485-486 行：重复硬编码
- 第 533-534 行：重复硬编码

**涉及文件**: app.py

**修复方案**: 提取为常量或配置项

---

### 【LOW】后端 - 缓存没有失效机制

**严重级别**: low  
**所属模块**: 通用  
**复现步骤**:
1. 修改配置
2. 立即查看状态

**实际表现**: 可能看到旧数据（最多2秒）

**预期表现**: 配置修改后应该立即清除相关缓存

**根本原因**: 配置保存时没有清除 status/logs/traffic 的缓存

**涉及文件**: app.py

**修复方案**: 在 save_config() 和 save_config_raw() 中清除缓存

---

### 【LOW】后端 - 日志 API 中的奇怪代码

**严重级别**: low  
**所属模块**: 日志  
**复现步骤**: 查看日志代码

**实际表现**: 第 418 行有不必要的 subprocess.run('which journalctl') 调用，每次都执行

**预期表现**: 不需要每次都检查

**根本原因**: 代码冗余

**涉及文件**: app.py

**修复方案**: 简化这部分逻辑

---

## 分类统计

| 类型 | 数量 |
|------|------|
| 功能失效 | 3 |
| 刷新异常 | 0 |
| 状态不同步 | 0 |
| 前后端协议不一致 | 0 |
| 异常处理缺失 | 1 |
| 代码结构问题 | 3 |
| 潜在高风险问题 | 5 |

## 优先级排序

### 立即修复（CRITICAL + HIGH）
1. 事件绑定在 DOMContentLoaded 外部
2. Modal 初始化在 DOMReady 之前
3. 重复的事件绑定
4. renderProxyNodes 事件绑定内存泄漏

### 尽快修复（MEDIUM）
5. 配置写入没有原子性
6. 子进程调用没有统一超时保护
7. 异常捕获太宽泛
8. 没有统一的 fetch 错误处理
9. fetch 调用没有超时

### 计划修复（LOW）
10. Mihomo API 配置硬编码
11. 缓存没有失效机制
12. 日志 API 中的奇怪代码

---

## 备注

本次审计发现的问题主要集中在：
1. 前端事件绑定位置错误（最严重）
2. 缺乏统一的错误处理和超时机制
3. 后端异常处理不够规范
4. 一些代码结构可以优化

建议优先修复 CRITICAL 和 HIGH 级别的问题，这些问题会直接影响用户体验。
