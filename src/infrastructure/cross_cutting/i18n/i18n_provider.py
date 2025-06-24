"""
横切关注点 - 国际化提供者

提供统一的国际化服务，包括多语言支持、本地化等。
遵循DDD架构中的横切关注点设计原则，为整个应用提供国际化基础设施。
"""

import os
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..logging import get_logger


class II18nProvider(ABC):
    """国际化提供者接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """获取翻译文本"""
        pass
    
    @abstractmethod
    def set_language(self, language: str) -> bool:
        """设置当前语言"""
        pass
    
    @abstractmethod
    def get_current_language(self) -> str:
        """获取当前语言"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        pass


class I18nProvider(II18nProvider):
    """国际化提供者实现 - 统一的多语言服务"""
    
    def __init__(self, default_language: str = "zh_CN", i18n_dir: str = None):
        """
        初始化国际化提供者
        
        Args:
            default_language: 默认语言
            i18n_dir: 国际化文件目录
        """
        self.logger = get_logger("i18n.provider")
        self.default_language = default_language
        self.current_language = default_language
        self.i18n_dir = Path(i18n_dir) if i18n_dir else Path("i18n")
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_default_translations()
    
    def _load_default_translations(self):
        """加载默认翻译"""
        # 内置的基础翻译
        self._translations["zh_CN"] = {
            "common.ok": "确定",
            "common.cancel": "取消",
            "common.save": "保存",
            "common.delete": "删除",
            "common.error": "错误",
            "common.success": "成功",
            "common.warning": "警告",
            "common.info": "信息"
        }
        
        self._translations["en_US"] = {
            "common.ok": "OK",
            "common.cancel": "Cancel",
            "common.save": "Save",
            "common.delete": "Delete",
            "common.error": "Error",
            "common.success": "Success",
            "common.warning": "Warning",
            "common.info": "Info"
        }
    
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            language: 语言代码（可选，默认使用当前语言）
            **kwargs: 格式化参数
            
        Returns:
            str: 翻译后的文本
        """
        try:
            lang = language or self.current_language
            
            # 获取翻译文本
            if lang in self._translations and key in self._translations[lang]:
                text = self._translations[lang][key]
            else:
                # 回退到默认语言
                if key in self._translations.get(self.default_language, {}):
                    text = self._translations[self.default_language][key]
                else:
                    # 如果都没有找到，返回键名
                    text = key
            
            # 格式化文本
            if kwargs:
                text = text.format(**kwargs)
            
            return text
            
        except Exception as e:
            self.logger.error(f"获取翻译文本失败 {key}: {str(e)}")
            return key
    
    def set_language(self, language: str) -> bool:
        """
        设置当前语言
        
        Args:
            language: 语言代码
            
        Returns:
            bool: 是否设置成功
        """
        try:
            if language in self._translations:
                self.current_language = language
                self.logger.info(f"设置语言: {language}")
                return True
            else:
                self.logger.warning(f"不支持的语言: {language}")
                return False
                
        except Exception as e:
            self.logger.error(f"设置语言失败: {str(e)}")
            return False
    
    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.current_language
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return list(self._translations.keys())
    
    def load_language_file(self, language: str, file_path: str) -> bool:
        """
        加载语言文件
        
        Args:
            language: 语言代码
            file_path: 语言文件路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            if not Path(file_path).exists():
                self.logger.warning(f"语言文件不存在: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            if language not in self._translations:
                self._translations[language] = {}
            
            self._translations[language].update(translations)
            self.logger.info(f"加载语言文件成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"加载语言文件失败: {str(e)}")
            return False


# 全局国际化提供者实例
_i18n_provider: Optional[I18nProvider] = None


def get_i18n_provider() -> I18nProvider:
    """获取全局国际化提供者"""
    global _i18n_provider
    if _i18n_provider is None:
        _i18n_provider = I18nProvider()
    return _i18n_provider


# 便捷函数
def get_text(key: str, language: str = None, **kwargs) -> str:
    """便捷函数：获取翻译文本"""
    return get_i18n_provider().get_text(key, language, **kwargs)


def set_language(language: str) -> bool:
    """便捷函数：设置语言"""
    return get_i18n_provider().set_language(language)


def get_current_language() -> str:
    """便捷函数：获取当前语言"""
    return get_i18n_provider().get_current_language()


def get_supported_languages() -> List[str]:
    """便捷函数：获取支持的语言列表"""
    return get_i18n_provider().get_supported_languages() 