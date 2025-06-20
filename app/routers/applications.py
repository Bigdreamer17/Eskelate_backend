from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
import cloudinary.uploader
from app.models.schemas import ApplyIn, BaseResponse, PaginatedResponse
from app.models.enums import Role, ApplicationStatus
from app.core.dependencies import role_required, get_current_user
from app.db.supabase import get_supabase
from typing import Optional

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/jobs/{job_id}", response_model=BaseResponse)
async def apply_for_job(
    job_id: str,
    cover: Optional[str] = None,
    resume: UploadFile = File(...),
    applicant = Depends(role_required(Role.applicant))
):
    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF")

    # upload to Cloudinary
    res = cloudinary.uploader.upload(resume.file, resource_type="raw")
    resume_url = res["secure_url"]

    supabase = get_supabase()

    # check duplicate
    dup = supabase.table("Application").select("*") \
        .eq("applicant_id", applicant["id"]).eq("job_id", job_id).maybe_single().execute().data
    if dup:
        return BaseResponse(success=False, message="Already applied", errors=["Duplicate application"])

    app_data = {
        "applicant_id": applicant["id"],
        "job_id": job_id,
        "resume_link": resume_url,
        "cover_letter": cover
    }
    record = supabase.table("Application").insert(app_data).execute().data[0]
    return BaseResponse(success=True, message="Application submitted", object=record)

@router.get("/me", response_model=PaginatedResponse)
async def my_apps(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    applicant = Depends(role_required(Role.applicant))
):
    supabase = get_supabase()
    start, end = (page-1)*size, (page-1)*size+size-1
    q = supabase.table("Application").select("*,Job(title,User(name))") \
        .eq("applicant_id", applicant["id"])
    data = q.range(start, end).order("applied_at", desc=True).execute()
    return PaginatedResponse(
        success=True,
        message="My applications",
        object=data.data,
        page_number=page,
        page_size=size,
        total_size=data.count or len(data.data)
    )

@router.patch("/{application_id}", response_model=BaseResponse)
async def update_status(
    application_id: str,
    new_status: ApplicationStatus,
    company = Depends(role_required(Role.company))
):
    supabase = get_supabase()
    app_row = supabase.table("Application").select("*,Job(created_by)").eq("id", application_id).single().execute().data
    if not app_row or app_row["Job"]["created_by"] != company["id"]:
        return BaseResponse(success=False, message="Unauthorized", object=None)
    updated = supabase.table("Application").update({"status": new_status}).eq("id", application_id).execute().data[0]
    return BaseResponse(success=True, message="Status updated", object=updated)
