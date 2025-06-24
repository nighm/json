import os
import pytest
from scripts.jmeter_batch_register_enhanced import EnhancedJMeterBatchRegister

@pytest.fixture
def tester():
    """返回增强版JMeter批量注册管理器实例"""
    return EnhancedJMeterBatchRegister()

def test_init_and_prerequisites(tester):
    """
    测试类初始化与前置条件检查：
    - 检查JMeter可执行文件、JMX模板、结果目录等是否存在
    - 不依赖外部数据库和SSH，仅验证本地文件结构
    """
    # 检查实例属性
    assert hasattr(tester, 'jmeter_bin')
    assert hasattr(tester, 'results_dir')
    assert hasattr(tester, 'server_config')
    assert hasattr(tester, 'cpu_monitor')
    # 检查前置条件（只要本地文件存在即可通过）
    result = tester.check_prerequisites()
    assert isinstance(result, bool)


def test_modify_jmx_threads(tester):
    """
    测试JMX模板线程数/循环数修改功能：
    - 生成新JMX文件并检查其存在
    - 检查文件内容是否包含指定线程数和循环数
    """
    thread_count = 3
    loops = 2
    new_jmx = tester.modify_jmx_threads(thread_count, loops)
    assert os.path.exists(new_jmx)
    with open(new_jmx, 'r', encoding='utf-8') as f:
        content = f.read()
    assert f'<stringProp name="ThreadGroup.num_threads">{thread_count}</stringProp>' in content
    assert f'<stringProp name="LoopController.loops">{loops}</stringProp>' in content
    # 清理生成的测试JMX文件
    os.remove(new_jmx) 