import os
import json

# 项目标准目录结构
PROJECT_DIRS = [
    'src',
    'src/domain',
    'src/application',
    'src/infrastructure',
    'src/interfaces',
    'src/tools',
    'scripts'
]

# 依赖声明
REQUIREMENTS = '''\
requests>=2.31.0
redis>=5.0.0
pytest>=7.0.0
locust>=2.23.0
'''

# 配置信息
PROJECT_CONFIG = {
    "server_url": "192.168.24.45",
    "redis_host": "192.168.24.45",
    "redis_port": 6389,
    "redis_password": "Wjc4QRkz198a",
    "uuid_api": "/prod-api/captchaImage",
    "login_api": "/prod-api/login",
    "login_username": "super",
    "login_password": "Ujz4o8cWl9PC01879XItga==",
    "redis_captcha_prefix": "captcha_codes:",
    "test_apis": [
        "/protector/heartbeat",
        "/prod-api/dashboard/device/top5/online/school",
        "/prod-api/dashboard/device/top5/online/platform"
    ]
}

# 自动化开发计划文档
README = '''\
# 自动化接口测试与压力测试开发计划

## 1. 项目初始化
- [x] 明确需求与目标
- [x] 收集接口、Redis、认证等关键信息
- [ ] 初始化Python项目结构

## 2. 自动化登录流程开发
- [ ] 实现UUID获取接口自动请求
- [ ] 实现Redis自动查找验证码
- [ ] 实现自动登录并获取token
- [ ] token自动注入后续请求

## 3. 目标接口功能性自动化测试
- [ ] 实现心跳接口自动化测试
- [ ] 实现在线时长相关接口自动化测试
- [ ] 结果输出与校验

## 4. 压力测试开发
- [ ] 设计并实现可配置的并发压测脚本（如1000/5000/10000/50000/100000/500000）
- [ ] 支持多接口压测与性能统计
- [ ] 结果自动汇总与报告

## 5. 项目文档与交付
- [ ] 详细注释与使用说明
- [ ] 交付可运行脚本与完整文档

---

### 进度说明
- 当前阶段：项目初始化与需求梳理
- 正在进行：项目结构搭建、自动化脚本设计
- 下一步：实现自动化登录与接口测试主流程
- 已完成：需求确认、关键信息收集
- 待完成：功能性测试、压力测试、文档完善
'''

def create_dirs():
    for d in PROJECT_DIRS:
        os.makedirs(d, exist_ok=True)
        init_file = os.path.join(d, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('')

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    create_dirs()
    write_file('requirements.txt', REQUIREMENTS)
    write_file('project_config.json', json.dumps(PROJECT_CONFIG, indent=2, ensure_ascii=False))
    write_file('README.md', README)
    print('项目初始化完成，目录结构、依赖、配置、文档已生成。')

if __name__ == '__main__':
    main() 