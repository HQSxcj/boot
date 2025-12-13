"""
Link Parser Service
自动识别链接类型和来源网盘
"""
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LinkType(Enum):
    """链接类型枚举"""
    MAGNET = 'magnet'
    ED2K = 'ed2k'
    HTTP = 'http'
    SHARE_115 = '115_share'
    SHARE_123 = '123_share'
    UNKNOWN = 'unknown'


class CloudSource(Enum):
    """云盘来源枚举"""
    CLOUD_115 = '115'
    CLOUD_123 = '123'
    GENERAL = 'general'  # 通用链接，可离线到任意网盘


@dataclass
class ParsedLink:
    """解析后的链接信息"""
    type: LinkType
    source: CloudSource
    url: str
    share_code: Optional[str] = None
    access_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'source': self.source.value,
            'url': self.url,
            'share_code': self.share_code,
            'access_code': self.access_code
        }


class LinkParser:
    """链接解析服务 - 自动识别链接类型和来源"""
    
    # 115 分享链接正则
    PATTERNS_115_SHARE = [
        # https://115.com/s/sw3xxxx
        r'https?://115\.com/s/([a-zA-Z0-9]+)(?:\?password=([a-zA-Z0-9]+))?',
        # https://anxia.com/s/sw3xxxx  
        r'https?://anxia\.com/s/([a-zA-Z0-9]+)(?:\?password=([a-zA-Z0-9]+))?',
        # 115://share|xxx|xxx
        r'115://share\|([a-zA-Z0-9]+)\|?([a-zA-Z0-9]*)?',
    ]
    
    # 123 云盘分享链接正则
    PATTERNS_123_SHARE = [
        # https://www.123pan.com/s/xxxx
        r'https?://(?:www\.)?123pan\.com/s/([a-zA-Z0-9\-]+)(?:\?提取码[：:]?([a-zA-Z0-9]+))?',
        # https://www.123pan.cn/s/xxxx
        r'https?://(?:www\.)?123pan\.cn/s/([a-zA-Z0-9\-]+)(?:\?提取码[：:]?([a-zA-Z0-9]+))?',
        # 123pan://share/xxxx
        r'123pan://share/([a-zA-Z0-9\-]+)(?:\|([a-zA-Z0-9]+))?',
    ]
    
    # 磁力链接正则
    PATTERN_MAGNET = r'magnet:\?xt=urn:[a-zA-Z0-9]+:[a-zA-Z0-9]+'
    
    # Ed2k 链接正则  
    PATTERN_ED2K = r'ed2k://\|file\|[^|]+\|[0-9]+\|[a-fA-F0-9]+\|'
    
    # HTTP/HTTPS 下载链接正则
    PATTERN_HTTP = r'https?://[^\s]+'
    
    def parse(self, text: str) -> ParsedLink:
        """
        解析文本中的链接
        
        Args:
            text: 用户发送的文本
            
        Returns:
            ParsedLink 对象
        """
        text = text.strip()
        
        # 1. 检查 115 分享链接
        for pattern in self.PATTERNS_115_SHARE:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                share_code = match.group(1) if match.lastindex >= 1 else None
                access_code = match.group(2) if match.lastindex >= 2 else None
                # 尝试从文本中提取访问码
                if not access_code:
                    access_code = self._extract_access_code(text)
                return ParsedLink(
                    type=LinkType.SHARE_115,
                    source=CloudSource.CLOUD_115,
                    url=match.group(0),
                    share_code=share_code,
                    access_code=access_code
                )
        
        # 2. 检查 123 云盘分享链接
        for pattern in self.PATTERNS_123_SHARE:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                share_code = match.group(1) if match.lastindex >= 1 else None
                access_code = match.group(2) if match.lastindex >= 2 else None
                if not access_code:
                    access_code = self._extract_access_code(text)
                return ParsedLink(
                    type=LinkType.SHARE_123,
                    source=CloudSource.CLOUD_123,
                    url=match.group(0),
                    share_code=share_code,
                    access_code=access_code
                )
        
        # 3. 检查磁力链接
        match = re.search(self.PATTERN_MAGNET, text, re.IGNORECASE)
        if match:
            return ParsedLink(
                type=LinkType.MAGNET,
                source=CloudSource.GENERAL,
                url=match.group(0)
            )
        
        # 4. 检查 Ed2k 链接
        match = re.search(self.PATTERN_ED2K, text, re.IGNORECASE)
        if match:
            return ParsedLink(
                type=LinkType.ED2K,
                source=CloudSource.GENERAL,
                url=match.group(0)
            )
        
        # 5. 检查 HTTP/HTTPS 链接
        match = re.search(self.PATTERN_HTTP, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            # 排除已识别的分享链接
            if '115.com' not in url and '123pan' not in url:
                return ParsedLink(
                    type=LinkType.HTTP,
                    source=CloudSource.GENERAL,
                    url=url
                )
        
        # 未识别的链接
        return ParsedLink(
            type=LinkType.UNKNOWN,
            source=CloudSource.GENERAL,
            url=text
        )
    
    def _extract_access_code(self, text: str) -> Optional[str]:
        """从文本中提取访问码/提取码"""
        # 常见格式: 提取码: xxxx, 密码: xxxx, 访问码: xxxx
        patterns = [
            r'(?:提取码|密码|访问码|password)[：:\s]*([a-zA-Z0-9]{4,8})',
            r'(?:code)[：:\s]*([a-zA-Z0-9]{4,8})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def get_target_options(self, parsed: ParsedLink) -> list:
        """
        根据链接类型返回可选的目标网盘
        
        Args:
            parsed: 解析后的链接
            
        Returns:
            可选目标列表 ['115', '123']
        """
        if parsed.type == LinkType.SHARE_115:
            # 115 分享链接可转存到 115 或 123（如果 123 支持）
            return ['115']
        elif parsed.type == LinkType.SHARE_123:
            # 123 分享链接只能转存到 123
            return ['123']
        elif parsed.type in [LinkType.MAGNET, LinkType.ED2K, LinkType.HTTP]:
            # 通用链接可离线到任意网盘
            return ['115', '123']
        else:
            return []
    
    def get_action_text(self, parsed: ParsedLink) -> str:
        """获取操作描述文本"""
        if parsed.type == LinkType.SHARE_115:
            return "转存 115 分享链接"
        elif parsed.type == LinkType.SHARE_123:
            return "转存 123 云盘分享链接"
        elif parsed.type == LinkType.MAGNET:
            return "离线下载磁力链接"
        elif parsed.type == LinkType.ED2K:
            return "离线下载 Ed2k 链接"
        elif parsed.type == LinkType.HTTP:
            return "离线下载 HTTP 链接"
        else:
            return "未识别的链接"
