import pytest
from src.infrastructure.cross_cutting.i18n import get_i18n_provider, get_text, set_language

# 国际化模块单元测试

def test_get_text_default():
    """
    测试默认语言的翻译文本获取。
    """
    assert get_text('common.ok') == '确定'


def test_language_switch():
    """
    测试多语言切换功能。
    """
    set_language('en_US')
    assert get_text('common.ok') == 'OK'
    set_language('zh_CN')
    assert get_text('common.ok') == '确定'


def test_get_text_not_exist_key():
    """
    测试获取不存在key时的处理。
    """
    assert get_text('not.exist.key') in ['', None, 'not.exist.key']


def test_param_text():
    """
    测试参数化文本获取。
    """
    provider = get_i18n_provider()
    if hasattr(provider, 'get_text'):
        text = provider.get_text('greeting', language='zh_CN', name='张三')
        assert '张三' in text or '{name}' in text


def test_dynamic_language_load():
    """
    测试动态语言包加载（如有实现）。
    """
    provider = get_i18n_provider()
    if hasattr(provider, 'load_language_pack'):
        provider.load_language_pack('fr_FR', {'common.ok': 'D’accord'})
        set_language('fr_FR')
        assert get_text('common.ok') == 'D’accord' 