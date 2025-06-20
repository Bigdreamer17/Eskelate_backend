from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.core.dependencies import role_required, get_current_user
from app.models.schemas import JobIn, BaseResponse, PaginatedResponse
from app.models.enums import Role
from app.db.supabase import get_supabase

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Company routes
@router.post("/", response_model=BaseResponse)
async def create_job(
    data: JobIn,
    company = Depends(role_required(Role.company))
):
    supabase = get_supabase()
    payload = data.dict()
    payload.update({"created_by": company["id"]})
    job = supabase.table("Job").insert(payload).execute().data[0]
    return BaseResponse(success=True, message="Job created", object=job)

@router.put("/{job_id}", response_model=BaseResponse)
async def update_job(
    job_id: str,
    data: JobIn,
    company = Depends(role_required(Role.company))
):
    supabase = get_supabase()
    # ownership enforcement
    job = supabase.table("Job").select("*").eq("id", job_id).single().execute().data
    if not job or job["created_by"] != company["id"]:
        return BaseResponse(success=False, message="Unauthorized access")
    updated = supabase.table("Job").update(data.dict()).eq("id", job_id).execute().data[0]
    return BaseResponse(success=True, message="Job updated", object=updated)

@router.delete("/{job_id}", response_model=BaseResponse)
async def delete_job(job_id: str, company = Depends(role_required(Role.company))):
    supabase = get_supabase()
    job = supabase.table("Job").select("*").eq("id", job_id).single().execute().data
    if not job or job["created_by"] != company["id"]:
        return BaseResponse(success=False, message="Unauthorized access")
    supabase.table("Job").delete().eq("id", job_id).execute()
    return BaseResponse(success=True, message="Job deleted")

# Applicant route – browse
@router.get("/", response_model=PaginatedResponse)
async def browse_jobs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    location: Optional[str] = None,
    company_name: Optional[str] = None,
    _applicant = Depends(role_required(Role.applicant))
):
    supabase = get_supabase()
    query = supabase.table("Job").select("*,User(name)")
    if title:
        query = query.ilike("title", f"%{title}%")
    if location:
        query = query.ilike("location", f"%{location}%")
    if company_name:
        # join condition uses embedded user alias
        query = query.ilike("User.name", f"%{company_name}%")
    start = (page - 1) * size
    end = start + size - 1
    data = query.range(start, end).order("created_at", desc=True).execute()
    jobs = data.data
    total = data.count or len(jobs)
    return PaginatedResponse(
        success=True,
        message="Jobs list",
        object=jobs,
        page_number=page,
        page_size=size,
        total_size=total
    )
