from enum import Enum

class Role(str, Enum):
    applicant = "applicant"
    company = "company"

class ApplicationStatus(str, Enum):
    Applied = "Applied"
    Reviewed = "Reviewed"
    Interview = "Interview"
    Rejected = "Rejected"
    Hired = "Hired"
