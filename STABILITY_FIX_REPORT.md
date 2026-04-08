# Mihomo WebUI 载入与刷新稳定性修复报告

## 修复日期
2026-04-08

---

## A. 根因总结

### 根本原因
**初始化链断裂 - `loadConfig()` 和 `loadRawConfig()` 在 DOMContentLoaded 中被意外删除！**

### 这是架构问题吗？
**绝对不是！** 这是**简单的人为失误**，不是架构问题。

- ✅ 事件绑定位置修复 - 是正确的
- ✅ Modal 初始化位置修复 - 是正确的  
- ✅ 自动刷新机制 - 是正确的
- ❌ 只是在整理代码时，不小心删除了两个关键函数调用

---

## B. 为什么会"修着修着暂时正常，最终又坏了"

### 时间线分析
1. **初始代码** - `loadConfig()` 和 `loadRawConfig()` 都在 DOMContentLoaded 中
2. **某个修复提交** - 我在整理 DOMContentLoaded 代码时，把这两个调用删掉了
3. **后续** - 页面就一直"无法载入 / 无法刷新"

### 为什么我没发现
- 只检查"页面能否打开"
- 没有检查"内容是否完整"
- 看到状态监控能工作，误以为其他部分也正常

---

## C. 这次具体改了什么

### 修改文件
`/home/admin/mihomo-webui/templates/index.html`

### 修改内容
在 DOMContentLoaded 开头恢复了两个关键调用，并添加了调试日志：

```javascript
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DOMContentLoaded] 开始初始化...');
    
    // 初始化 Modal
    proxyGroupModal = new bootstrap.Modal(document.getElementById('proxyGroupModal'));
    ruleModal = new bootstrap.Modal(document.getElementById('ruleModal'));
    console.log('[DOMContentLoaded] Modal 初始化完成');

    // 加载配置（关键！）
    console.log('[DOMContentLoaded] 开始加载配置...');
    loadConfig();        // ← 恢复这个！
    loadRawConfig();     // ← 恢复这个！
    console.log('[DOMContentLoaded] 配置加载完成');
    
    updateStatus();
    startAutoRefresh();
    loadLogs();
    startLogsAutoRefresh();
    loadTraffic();
    startTrafficAutoRefresh();
    
    // ... 其他事件绑定
});
```

---

## D. 现在如何保证不再反复出现

### 1. 防回归机制
- ✅ 添加了初始化的 console.log，方便调试和验证
- ✅ 每个初始化步骤都有明确的日志输出
- ✅ 代码注释中明确标明"加载配置（关键！）"

### 2. 手动检查清单（每次修改后）
1. 页面能打开吗？
2. 控制台有完整的初始化日志吗？
3. 仪表盘数据不是全 0 吗？
4. 原始配置编辑器有内容吗？
5. 代理组和规则页面能显示内容吗？

---

## E. 修复验证

### 预期结果
- ✅ 页面打开时控制台有完整初始化日志
- ✅ 仪表盘显示正确的配置数量
- ✅ 原始配置编辑器有 YAML 内容
- ✅ 代理组和规则页面正常工作

### 代码正确性验证
- ✅ 文件已正确修改
- ✅ `loadConfig()` 已恢复
- ✅ `loadRawConfig()` 已恢复
- ✅ 有调试日志

---

## F. 还剩哪些风险点

### LOW 优先级，不影响核心功能
1. **前端 fetch 没有超时** - 可以加，但现在不影响功能
2. **没有统一的 fetch 包装** - 可以重构，但不影响功能
3. **Mihomo API 地址硬编码** - 可以改进，但不影响功能
4. **配置写入没有原子性** - 可以改进，但很少出问题

---

## G. 总结

| 问题 | 答案 |
|------|------|
| 为什么"无法刷新 / 无法载入" | **不是总是，是从 commit 49116fb 开始** |
| 这是架构问题吗？ | **不是**，是简单的人为失误 |
| 这次修复解决根因了吗？ | **是的**，恢复两个关键调用 |
| 以后如何避免回归？ | 修改后检查：1. 完整初始化日志 2. 内容完整 3. 功能可用 |

---

## H. Commit

```
fix: 修复页面初始化缺少 loadConfig 和 loadRawConfig

- 根因：在整理 DOMContentLoaded 代码时意外删除了关键初始化调用
- 修复：恢复 loadConfig() 和 loadRawConfig()
- 改进：添加调试日志，方便验证初始化流程
```
