from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import SignUpIn, LoginIn, BaseResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.db.supabase import get_supabase
from supabase import Client

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignUpIn):
    supabase = get_supabase()

    try:
        # Check if user already exists
        resp = (
            supabase.table("users")
            .select("*")
            .eq("email", payload.email)
            .maybe_single()
            .execute()
        )

        if resp is None or getattr(resp, "data", None) is None:
            # If no existing user, go ahead
            pass
        else:
            # User already exists
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB check failed: {str(e)}")

    # Hash the password
    hashed_pw = hash_password(payload.password)

    try:
        insert_resp = (
            supabase.table("users")
            .insert(
                {
                    "name": payload.name,
                    "email": payload.email,
                    "password": hashed_pw,
                    "role": "applicant",  # Ensure this matches the CHECK constraint
                }
            )
            .execute()
        )

        if insert_resp is None or not getattr(insert_resp, "data", None):
            raise HTTPException(
                status_code=500, detail="User insert returned no data."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB insert failed: {str(e)}")

    return {"message": "User created successfully"}

@router.post("/login", response_model=BaseResponse)
async def login(payload: LoginIn):
    supabase = supabase()
    user = supabase.table("User").select("*").eq("email", payload.email).maybe_single().execute().data
    if not user:
        return BaseResponse(success=False, message="User not found", errors=["User not found"])
    if not verify_password(payload.password, user["password"]):
        return BaseResponse(success=False, message="Incorrect password", errors=["Incorrect password"])
    token = create_access_token({"id": user["id"], "role": user["role"]})
    return BaseResponse(success=True, message="Logged in", object=TokenOut(access_token=token).dict())
