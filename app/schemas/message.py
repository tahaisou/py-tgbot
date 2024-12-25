from pydantic import BaseModel, HttpUrl
from enum import Enum
from typing import Optional

class ParseMode(str, Enum):
    """
    消息解析模式
    """
    MARKDOWN = "MarkdownV2"  # Telegram 的 Markdown V2 格式
    HTML = "HTML"           # HTML 格式
    TEXT = "Text"          # 纯文本

class MediaType(str, Enum):
    """
    媒体类型
    """
    PHOTO = "photo"
    DOCUMENT = "document"

class MessageCreate(BaseModel):
    """
    发送消息的请求模型
    """
    text: str
    parse_mode: ParseMode = ParseMode.TEXT  # 默认为纯文本 
    photo_url: Optional[HttpUrl] = None  # 图片URL
    caption: Optional[str] = None        # 图片说明 