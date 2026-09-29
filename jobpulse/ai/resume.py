"""Structured resume extraction workflow."""

import json

from pydantic import BaseModel, Field, ValidationError

from .client import AIClient
from .prompts import RESUME_EXTRACTION_SYSTEM_PROMPT


class ExperienceItem(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
    description: str = ""


class EducationItem(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    year: str = ""


class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    name: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)


class ResumeExtractionError(RuntimeError):
    """Raised when the provider returns an unusable resume profile."""


def extract_resume_profile(resume_text: str) -> ResumeProfile:
    """Extract and validate a structured profile from resume text."""
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("resume_text must be a non-empty string")

    ai_client = AIClient()
    try:
        from google.genai import types

        response = ai_client.provider_client.models.generate_content(
            model=ai_client.model,
            contents=resume_text,
            config=types.GenerateContentConfig(
                system_instruction=RESUME_EXTRACTION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ResumeProfile,
            ),
        )
        data = json.loads(response.text)
        return ResumeProfile.model_validate(data)
    except (ValidationError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ResumeExtractionError(
            "Resume extraction returned an invalid structured response"
        ) from error
    except Exception as error:
        raise ResumeExtractionError("Resume extraction API request failed") from error