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