from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Flutter web frontend to talk to backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # in production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ResumeRequest(BaseModel):
    name: str
    skills: list[str]

@app.post("/generate_resume")
def generate_resume(req: ResumeRequest):
    # Simulate AI logic for now
    resume_text = f"Resume for {req.name}\nSkills: {', '.join(req.skills)}"
    return {"resume": resume_text}
