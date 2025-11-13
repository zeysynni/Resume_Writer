from pydantic import BaseModel, Field
from typing import Optional

class Task(BaseModel):
    task: str = Field(description="A task that the resume owner has done.")

class Content(BaseModel):
    bullet_point: str = Field(description="A relevant content that is related to the education.", example= "Vertiefung in Automatisierungstechnik und KI")

class Language(BaseModel):
    language: str = Field(description="A language that the resume owner speaks")

class Skill(BaseModel):
    skill: str = Field(description="A skill that the resume owner has. You can put imilar skills together.", example="'Python' or 'Machine Learning and Deep Learning")

class Experience(BaseModel):
    company_name: str = Field(description="The name of the company.")
    company_location: str = Field(description="The location of the company.")
    company_time: str = Field(description="The time period when the resume owner was working in this company.")
    company_position: str = Field(description="The position of the resume owner in this company.")
    tasks: list[Task] = Field(description="A list of tasks that the resume owner has done in this company.")

class Education(BaseModel):
    topic: str = Field(description="The topic of the education (e.g. 'Bachelor of Science' or 'LLM Engineering')", example="'Bachelor of Science' or 'LLM Engineering'")
    institute: str = Field(description="The name of the institute where the education took place.")
    location: Optional[str] = Field(None, description="The location of the institute.")
    time: str = Field(description="time interval where the education took place.")
    contents: list[Content] = Field(description="A list of relevant contents to this education.")

class Resume(BaseModel):
    name: str = Field(description="The name of the resume owner.")
    current_position: str = Field(description="The current position of the resume owner.")
    address: str = Field(description="The address of the resume owner.")
    email: str = Field(description="The E-Mail address of the resume owner.")
    phone: str = Field(description="The phone number of the resume owner.")
    languages: list[Language] = Field(description="The languages that the resume owner speaks.")
    working_experiences: list[Experience] = Field(description="The working experiences of the resume owner")
    education: list[Education] = Field(description="The education experiences of the resume owner")
    softskills: str = Field(description="The soft skills of the resume owner")
    skills: list[Skill] = Field(description="The knowlege and skills of the resume owner")
    introduction: str = Field(description="A long self-introduction of the resume owner, including experiences, educations, technical and softskill")