from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Python Web Admin"
    VERSION: str = "1.0.0"
    
    # MySQL 配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "102938qyw"
    MYSQL_DB: str = "py_admin"
    
    # 构建数据库 URI
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )
    
    # JWT 配置
    SECRET_KEY: str = "90e140012c313093b37cd5e5aa074511ee6a8219c9be86d4fb0ea1c4bee09a78"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings() 