# services/sensitive_data_service.py
# 敏感数据管理服务 - 统一管理所有加密存储的敏感信息

import json
from typing import Dict, Any, Optional
from services.secret_store import SecretStore


# 敏感数据 key 定义
class SensitiveKeys:
    """敏感数据存储键名常量"""
    # Admin 凭据
    ADMIN_PASSWORD_HASH = 'admin_password_hash'
    ADMIN_2FA_SECRET = 'admin_2fa_secret'
    
    # Telegram
    TELEGRAM_BOT_TOKEN = 'telegram_bot_token'
    
    # TMDB
    TMDB_API_KEY = 'tmdb_api_key'
    
    # Emby
    EMBY_API_KEY = 'emby_api_key'
    
    # AI 服务
    AI_API_KEY = 'ai_api_key'
    
    # 云盘凭据 (already in secret_store)
    CLOUD115_COOKIES = 'cloud115_cookies'
    CLOUD115_SESSION_METADATA = 'cloud115_session_metadata'
    CLOUD123_CREDENTIALS = 'cloud123_credentials'
    CLOUD123_COOKIES = 'cloud123_cookies'
    CLOUD123_TOKEN = 'cloud123_token'
    CLOUD123_SESSION_METADATA = 'cloud123_session_metadata'
    
    # OpenList
    OPENLIST_PASSWORD = 'openlist_password'
    
    # Proxy
    PROXY_PASSWORD = 'proxy_password'
    
    # WebDAV
    WEBDAV_PASSWORD = 'webdav_password'


class SensitiveDataService:
    """Service for managing all sensitive data with encryption."""
    
    def __init__(self, secret_store: SecretStore):
        self.secret_store = secret_store
    
    # === Admin 凭据 ===
    
    def set_admin_password_hash(self, password_hash: str) -> bool:
        """Store encrypted admin password hash."""
        return self.secret_store.set_secret(SensitiveKeys.ADMIN_PASSWORD_HASH, password_hash)
    
    def get_admin_password_hash(self) -> Optional[str]:
        """Get decrypted admin password hash."""
        return self.secret_store.get_secret(SensitiveKeys.ADMIN_PASSWORD_HASH)
    
    def set_admin_2fa_secret(self, secret: str) -> bool:
        """Store encrypted 2FA secret."""
        return self.secret_store.set_secret(SensitiveKeys.ADMIN_2FA_SECRET, secret)
    
    def get_admin_2fa_secret(self) -> Optional[str]:
        """Get decrypted 2FA secret."""
        return self.secret_store.get_secret(SensitiveKeys.ADMIN_2FA_SECRET)
    
    def has_2fa_enabled(self) -> bool:
        """Check if 2FA is enabled."""
        return self.secret_store.secret_exists(SensitiveKeys.ADMIN_2FA_SECRET)
    
    # === API Keys ===
    
    def set_telegram_bot_token(self, token: str) -> bool:
        """Store encrypted Telegram bot token."""
        return self.secret_store.set_secret(SensitiveKeys.TELEGRAM_BOT_TOKEN, token)
    
    def get_telegram_bot_token(self) -> Optional[str]:
        """Get decrypted Telegram bot token."""
        return self.secret_store.get_secret(SensitiveKeys.TELEGRAM_BOT_TOKEN)
    
    def set_tmdb_api_key(self, key: str) -> bool:
        """Store encrypted TMDB API key."""
        return self.secret_store.set_secret(SensitiveKeys.TMDB_API_KEY, key)
    
    def get_tmdb_api_key(self) -> Optional[str]:
        """Get decrypted TMDB API key."""
        return self.secret_store.get_secret(SensitiveKeys.TMDB_API_KEY)
    
    def set_emby_api_key(self, key: str) -> bool:
        """Store encrypted Emby API key."""
        return self.secret_store.set_secret(SensitiveKeys.EMBY_API_KEY, key)
    
    def get_emby_api_key(self) -> Optional[str]:
        """Get decrypted Emby API key."""
        return self.secret_store.get_secret(SensitiveKeys.EMBY_API_KEY)
    
    def set_ai_api_key(self, key: str) -> bool:
        """Store encrypted AI API key."""
        return self.secret_store.set_secret(SensitiveKeys.AI_API_KEY, key)
    
    def get_ai_api_key(self) -> Optional[str]:
        """Get decrypted AI API key."""
        return self.secret_store.get_secret(SensitiveKeys.AI_API_KEY)
    
    # === 其他敏感字段 ===
    
    def set_openlist_password(self, password: str) -> bool:
        return self.secret_store.set_secret(SensitiveKeys.OPENLIST_PASSWORD, password)
    
    def get_openlist_password(self) -> Optional[str]:
        return self.secret_store.get_secret(SensitiveKeys.OPENLIST_PASSWORD)
    
    def set_proxy_password(self, password: str) -> bool:
        return self.secret_store.set_secret(SensitiveKeys.PROXY_PASSWORD, password)
    
    def get_proxy_password(self) -> Optional[str]:
        return self.secret_store.get_secret(SensitiveKeys.PROXY_PASSWORD)
    
    def set_webdav_password(self, password: str) -> bool:
        return self.secret_store.set_secret(SensitiveKeys.WEBDAV_PASSWORD, password)
    
    def get_webdav_password(self) -> Optional[str]:
        return self.secret_store.get_secret(SensitiveKeys.WEBDAV_PASSWORD)
    
    # === 批量操作 ===
    
    def extract_sensitive_from_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从配置中提取敏感字段并存储到 SecretStore。
        返回清理后的配置（敏感字段被移除或替换为占位符）。
        """
        cleaned_config = json.loads(json.dumps(config))  # Deep copy
        
        # Telegram bot token
        if cleaned_config.get('telegram', {}).get('botToken'):
            self.set_telegram_bot_token(cleaned_config['telegram']['botToken'])
            cleaned_config['telegram']['botToken'] = '[ENCRYPTED]'
        
        # TMDB API key
        if cleaned_config.get('tmdb', {}).get('apiKey'):
            self.set_tmdb_api_key(cleaned_config['tmdb']['apiKey'])
            cleaned_config['tmdb']['apiKey'] = '[ENCRYPTED]'
        
        # Emby API key
        if cleaned_config.get('emby', {}).get('apiKey'):
            self.set_emby_api_key(cleaned_config['emby']['apiKey'])
            cleaned_config['emby']['apiKey'] = '[ENCRYPTED]'
        
        # AI API key
        if cleaned_config.get('organize', {}).get('ai', {}).get('apiKey'):
            self.set_ai_api_key(cleaned_config['organize']['ai']['apiKey'])
            cleaned_config['organize']['ai']['apiKey'] = '[ENCRYPTED]'
        
        # OpenList password
        if cleaned_config.get('openList', {}).get('password'):
            self.set_openlist_password(cleaned_config['openList']['password'])
            cleaned_config['openList']['password'] = '[ENCRYPTED]'
        
        # Proxy password
        if cleaned_config.get('proxy', {}).get('password'):
            self.set_proxy_password(cleaned_config['proxy']['password'])
            cleaned_config['proxy']['password'] = '[ENCRYPTED]'
        
        # WebDAV password
        if cleaned_config.get('strm', {}).get('webdav', {}).get('password'):
            self.set_webdav_password(cleaned_config['strm']['webdav']['password'])
            cleaned_config['strm']['webdav']['password'] = '[ENCRYPTED]'
        
        return cleaned_config
    
    def inject_sensitive_to_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将加密存储的敏感数据注入回配置对象。
        """
        result = json.loads(json.dumps(config))  # Deep copy
        
        # Telegram bot token
        token = self.get_telegram_bot_token()
        if token and 'telegram' in result:
            result['telegram']['botToken'] = token
        
        # TMDB API key
        tmdb_key = self.get_tmdb_api_key()
        if tmdb_key and 'tmdb' in result:
            result['tmdb']['apiKey'] = tmdb_key
        
        # Emby API key
        emby_key = self.get_emby_api_key()
        if emby_key and 'emby' in result:
            result['emby']['apiKey'] = emby_key
        
        # AI API key
        ai_key = self.get_ai_api_key()
        if ai_key and result.get('organize', {}).get('ai'):
            result['organize']['ai']['apiKey'] = ai_key
        
        # OpenList password
        openlist_pwd = self.get_openlist_password()
        if openlist_pwd and 'openList' in result:
            result['openList']['password'] = openlist_pwd
        
        # Proxy password
        proxy_pwd = self.get_proxy_password()
        if proxy_pwd and 'proxy' in result:
            result['proxy']['password'] = proxy_pwd
        
        # WebDAV password
        webdav_pwd = self.get_webdav_password()
        if webdav_pwd and result.get('strm', {}).get('webdav'):
            result['strm']['webdav']['password'] = webdav_pwd
        
        return result
