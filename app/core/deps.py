from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    """
    获取当前登录的管理员
    """
    payload = verify_token(token)
    username = payload.get("sub")
    if username != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    return username 