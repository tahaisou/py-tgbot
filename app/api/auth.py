from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models.admin import Admin, Token

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

@router.post("/login", response_model=Token, summary="管理员登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    管理员登录接口，获取访问令牌
    """
    # 添加日志，查看接收到的数据
    print(f"Received login request: username={form_data.username}, password={form_data.password}")
    
    # 验证用户名
    if form_data.username != Admin.USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not Admin.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": Admin.USERNAME}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    ) 