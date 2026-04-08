#!/usr/bin/env python3
import base64
import json
import requests

GITHUB_TOKEN = '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'
REPO_OWNER = 'mbtc95858'
REPO_NAME = 'mihomo-webui'
BRANCH = 'main'

print('=' * 60)
print('推送代码到 GitHub')
print('=' * 60)

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# 1. 推送代码
print('\n1. 推送代码...')
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{BRANCH}'
response = requests.get(url, headers=headers)
current_sha = response.json()['object']['sha']

# 创建 tree
print('   获取远程最新提交...')
commit_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{current_sha}'
response = requests.get(commit_url, headers=headers)
base_tree_sha = response.json()['tree']['sha']

# 读取本地提交
import subprocess
result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
local_commit_sha = result.stdout.strip()

# 获取本地提交的 tree
commit_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{local_commit_sha}'
response = requests.get(commit_url, headers=headers)
local_tree_sha = response.json()['tree']['sha']

# 创建新提交
print('   创建新提交...')
new_commit_data = {
    'message': 'perf: 性能优化 - 关闭Debug模式、优化缓存机制、统一刷新间隔\n\n- 关闭Flask Debug模式，避免ERR_ABORTED错误\n- 缓存TTL从2秒提升到10秒\n- 新增配置API缓存\n- 统一前端刷新间隔为10秒\n- 修复重复Flask进程问题',
    'tree': local_tree_sha,
    'parents': [current_sha]
}

response = requests.post(
    f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits',
    headers=headers,
    json=new_commit_data
)

if response.status_code == 201:
    new_commit_sha = response.json()['sha']
    print(f'   ✓ 提交创建成功: {new_commit_sha[:7]}')
    
    # 更新分支引用
    update_data = {
        'sha': new_commit_sha,
        'force': False
    }
    
    response = requests.patch(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print('   ✓ 分支更新成功!')
    else:
        print(f'   ✗ 分支更新失败: {response.status_code}')
        print(f'   {response.json()}')
else:
    print(f'   ✗ 提交创建失败: {response.status_code}')
    print(f'   {response.json()}')

# 2. 推送 Tag
print('\n2. 推送 Tag v1.0.1...')
tag_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()

tag_data = {
    'ref': 'refs/tags/v1.0.1',
    'sha': tag_sha,
    'message': 'v1.0.1: 性能优化版本，修复ERR_ABORTED问题'
}

response = requests.post(
    f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs',
    headers=headers,
    json=tag_data
)

if response.status_code == 201:
    print('   ✓ Tag v1.0.1 创建成功!')
elif response.status_code == 422:
    # Tag 已存在
    print('   ℹ Tag v1.0.1 已存在，将更新...')
    tag_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/tags/v1.0.1'
    response = requests.get(tag_url, headers=headers)
    old_sha = response.json()['object']['sha']
    
    # 删除旧 tag
    delete_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/tags/v1.0.1'
    response = requests.delete(delete_url, headers=headers)
    
    # 创建新 tag
    response = requests.post(
        f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs',
        headers=headers,
        json=tag_data
    )
    
    if response.status_code == 201:
        print('   ✓ Tag v1.0.1 更新成功!')
    else:
        print(f'   ✗ Tag 更新失败: {response.status_code}')
else:
    print(f'   ✗ Tag 创建失败: {response.status_code}')

print('\n' + '=' * 60)
print('推送完成!')
print(f'仓库地址: https://github.com/{REPO_OWNER}/{REPO_NAME}')
print('=' * 60)
