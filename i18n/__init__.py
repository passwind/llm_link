#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internationalization (i18n) module for the Intelligent PDF Query System.

This module provides multi-language support for the application,
including language detection, message loading, and translation functions.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class I18nManager:
    """
    Internationalization manager for handling multi-language support.
    
    Supports English (en) and Chinese (zh) languages with fallback mechanisms.
    """
    
    def __init__(self, default_language: str = 'en'):
        """
        Initialize the i18n manager.
        
        Args:
            default_language (str): Default language code ('en' or 'zh')
        """
        self.default_language = default_language
        self.current_language = default_language
        self.messages: Dict[str, Dict[str, Any]] = {}
        self.supported_languages = ['en', 'zh']
        
        # Load all language files
        self._load_all_languages()
    
    def _load_all_languages(self):
        """
        Load all supported language files.
        """
        base_dir = Path(__file__).parent / 'locales'
        
        for lang in self.supported_languages:
            lang_file = base_dir / lang / 'messages.json'
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.messages[lang] = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load language file {lang_file}: {e}")
                    self.messages[lang] = {}
            else:
                print(f"Warning: Language file not found: {lang_file}")
                self.messages[lang] = {}
    
    def set_language(self, language: str) -> bool:
        """
        Set the current language.
        
        Args:
            language (str): Language code to set
            
        Returns:
            bool: True if language was set successfully, False otherwise
        """
        if language in self.supported_languages:
            self.current_language = language
            return True
        return False
    
    def get_language(self) -> str:
        """
        Get the current language code.
        
        Returns:
            str: Current language code
        """
        return self.current_language
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported language codes.
        
        Returns:
            list: List of supported language codes
        """
        return self.supported_languages.copy()
    
    def get_language_name(self, language: str) -> str:
        """
        Get the display name for a language code.
        
        Args:
            language (str): Language code
            
        Returns:
            str: Display name for the language
        """
        language_names = {
            'en': 'English',
            'zh': '中文'
        }
        return language_names.get(language, language)
    
    def t(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Translate a message key to the current or specified language.
        
        Args:
            key (str): Message key in dot notation (e.g., 'app.title')
            language (str, optional): Language code to use (defaults to current)
            **kwargs: Variables to substitute in the message
            
        Returns:
            str: Translated message or the key if translation not found
        """
        if language is None:
            language = self.current_language
        
        # Get the message from the specified language
        message = self._get_nested_value(self.messages.get(language, {}), key)
        
        # Fallback to default language if not found
        if message is None and language != self.default_language:
            message = self._get_nested_value(
                self.messages.get(self.default_language, {}), key
            )
        
        # Fallback to key if still not found
        if message is None:
            message = key
        
        # Substitute variables if provided
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return message as-is if substitution fails
        
        return message
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """
        Get a nested value from a dictionary using dot notation.
        
        Args:
            data (dict): Dictionary to search in
            key (str): Dot-separated key path
            
        Returns:
            str or None: Value if found, None otherwise
        """
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def get_all_messages(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all messages for a language.
        
        Args:
            language (str, optional): Language code (defaults to current)
            
        Returns:
            dict: All messages for the language
        """
        if language is None:
            language = self.current_language
        
        return self.messages.get(language, {}).copy()


# Global i18n manager instance
_i18n_manager = I18nManager()


# Convenience functions
def set_language(language: str) -> bool:
    """
    Set the current language globally.
    
    Args:
        language (str): Language code to set
        
    Returns:
        bool: True if language was set successfully
    """
    return _i18n_manager.set_language(language)


def get_language() -> str:
    """
    Get the current language code.
    
    Returns:
        str: Current language code
    """
    return _i18n_manager.get_language()


def get_supported_languages() -> list:
    """
    Get list of supported language codes.
    
    Returns:
        list: List of supported language codes
    """
    return _i18n_manager.get_supported_languages()


def get_language_name(language: str) -> str:
    """
    Get the display name for a language code.
    
    Args:
        language (str): Language code
        
    Returns:
        str: Display name for the language
    """
    return _i18n_manager.get_language_name(language)


def t(key: str, language: Optional[str] = None, **kwargs) -> str:
    """
    Translate a message key.
    
    Args:
        key (str): Message key in dot notation
        language (str, optional): Language code to use
        **kwargs: Variables to substitute in the message
        
    Returns:
        str: Translated message
    """
    return _i18n_manager.t(key, language, **kwargs)


def get_all_messages(language: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all messages for a language.
    
    Args:
        language (str, optional): Language code
        
    Returns:
        dict: All messages for the language
    """
    return _i18n_manager.get_all_messages(language)