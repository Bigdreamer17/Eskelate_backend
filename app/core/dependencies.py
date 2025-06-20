from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token
from app.db.supabase import get_supabase
from app.models.enums import Role

security = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    token = creds.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    supabase = get_supabase()
    user = supabase.table("users").select("*").eq("id", payload["id"]).single().execute().data
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def role_required(role: Role):
    def _wrapper(user=Depends(get_current_user)):
        if user["role"] != role.value:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _wrapper
