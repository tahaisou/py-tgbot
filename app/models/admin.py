from pydantic import BaseModel

class Admin:
    """
    硬编码的管理员信息
    """
    USERNAME = "admin"
    PASSWORD = "admin123"
    
    @classmethod
    def verify_password(cls, password: str) -> bool:
        """
        验证密码
        """
        return cls.PASSWORD == password

class Token(BaseModel):
    """
    令牌模型
    """
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    """
    令牌数据模型
    """
    username: str 