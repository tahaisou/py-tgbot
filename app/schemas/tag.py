from pydantic import BaseModel
from typing import List

class TagCreate(BaseModel):
    """
    创建标签的请求模型
    """
    tags: List[str] 