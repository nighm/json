import json
import requests
import redis
import os
from pathlib import Path
import urllib3
import subprocess
import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 读取配置文件
def load_config():
    config_path = Path("src/config/project_config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_uuid():
    """获取UUID和验证码"""
    config = load_config()
    url = f"https://{config['server_url']}{config['uuid_api']}"
    response = requests.get(url, verify=False)  # 添加verify=False
    if response.status_code == 200:
        data = response.json()
        return data.get('uuid'), data.get('img')
    raise Exception("获取UUID失败")

def get_captcha_from_redis(uuid):
    """从Redis获取验证码"""
    config = load_config()
    r = redis.Redis(
        host=config['redis_host'],
        port=config['redis_port'],
        password=config['redis_password'],
        decode_responses=True
    )
    captcha_key = f"{config['redis_captcha_prefix']}{uuid}"
    return r.get(captcha_key)

def login_with_uuid(uuid, captcha):
    """使用UUID和验证码进行登录"""
    config = load_config()
    url = f"https://{config['server_url']}{config['login_api']}"
    data = {
        "username": config['login_username'],
        "password": config['login_password'],
        "code": captcha,
        "uuid": uuid
    }
    response = requests.post(url, json=data, verify=False)  # 添加verify=False
    return response.json()

# --- 配置 ---
# 获取项目根目录的绝对路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
JMETER_BIN_DIR = os.path.join(PROJECT_ROOT, "src", "tools", "jmeter", "bin")
JMETER_EXECUTABLE = os.path.join(JMETER_BIN_DIR, "jmeter.bat")
TEST_PLAN_FILE = os.path.join(JMETER_BIN_DIR, "register_test.jmx")
DB_MANAGER_SCRIPT = os.path.join(PROJECT_ROOT, "database_manager.py")

def run_command(command, working_dir=None):
    """通用命令执行函数"""
    print(f"\n▶️  执行命令: {' '.join(command)}")
    if working_dir:
        print(f"   (在目录: {working_dir})")
    try:
        result = subprocess.run(
            command,
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        print("✅ 命令成功执行。")
        # 只打印部分输出以保持日志整洁
        if len(result.stdout) > 500:
            print("   部分输出:\n" + "="*20 + f"\n{result.stdout[:500]}...\n" + "="*20)
        else:
            print("   输出:\n" + "="*20 + f"\n{result.stdout}\n" + "="*20)

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败. 返回码: {e.returncode}")
        print("   错误输出:\n" + "="*20 + f"\n{e.stderr}\n" + "="*20)
        return False
    except FileNotFoundError:
        print(f"❌ 命令执行失败: 文件未找到. 请检查路径是否正确: {command[0]}")
        return False

def query_database_state(step_name):
    """查询并打印数据库状态"""
    print(f"\n{'='*20} {step_name}: 查询数据库状态 {'='*20}")
    command = ["python", DB_MANAGER_SCRIPT, "--action", "analyze"]
    run_command(command, working_dir=PROJECT_ROOT)

def run_jmeter_test():
    """运行JMeter性能测试"""
    print(f"\n{'='*20} 正在启动JMeter性能测试 {'='*20}")
    
    # 为结果文件添加时间戳以避免覆盖
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(JMETER_BIN_DIR, "results", f"test_result_{timestamp}.jtl")
    
    command = [
        JMETER_EXECUTABLE,
        "-n",  # 非GUI模式
        "-t", TEST_PLAN_FILE,
        "-l", result_file
    ]
    
    if run_command(command, working_dir=JMETER_BIN_DIR):
        print(f"✅ JMeter测试完成. 结果已保存至: {result_file}")
    else:
        print("❌ JMeter测试失败.")

def main():
    """自动化测试流程主函数"""
    print(f"\n{'#'*60}")
    print(f"########### 开始端到端自动化API注册测试流程 ###########")
    print(f"{'#'*60}")

    # 1. 测试前查询数据库
    query_database_state("测试前")

    # 2. 运行JMeter测试
    run_jmeter_test()

    # 3. 测试后查询数据库
    query_database_state("测试后")

    print(f"\n{'#'*60}")
    print(f"########### 自动化测试流程结束 ###########")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    # 确保在执行前激活了虚拟环境
    if "VIRTUAL_ENV" not in os.environ:
        print("⚠️ 警告: 未检测到激活的Python虚拟环境。")
        print("请先运行: .\\venv\\Scripts\\Activate.ps1")
    main() 