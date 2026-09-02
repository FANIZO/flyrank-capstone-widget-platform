from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class FieldDefinition(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")
    label: str = Field(min_length=1, max_length=80)
    type: Literal["text", "email", "textarea"]
    required: bool = True


DEFAULT_FIELDS = [
    {"name": "name", "label": "Name", "type": "text", "required": True},
    {"name": "email", "label": "Email", "type": "email", "required": True},
    {"name": "message", "label": "Message", "type": "textarea", "required": True},
]


class WidgetCreate(BaseModel):
    widget_type: Literal["contact", "signup"] = "contact"
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    button_text: str = Field(default="Send", min_length=1, max_length=60)
    field_configuration: list[FieldDefinition] = Field(default_factory=lambda: [FieldDefinition(**item) for item in DEFAULT_FIELDS])
    display_options: dict = Field(default_factory=dict)


class WidgetUpdate(BaseModel):
    widget_type: Literal["contact", "signup"] | None = None
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    button_text: str | None = Field(default=None, min_length=1, max_length=60)
    field_configuration: list[FieldDefinition] | None = None
    display_options: dict | None = None
    active: bool | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    public_id: str
    owner_id: int
    widget_type: str
    title: str
    description: str | None
    button_text: str
    field_configuration: list
    display_options: dict
    active: bool
    created_at: datetime
    updated_at: datetime


class PublicWidgetConfig(BaseModel):
    public_id: str
    widget_type: str
    title: str
    description: str | None
    button_text: str
    fields: list
    display_options: dict
    submission_url: str


class LeadSubmission(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=1, max_length=2000)
    company_website: str = Field(default="", max_length=200)


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    widget_id: int
    name: str
    email: EmailStr
    message: str
    country: str | None
    city: str | None
    geo_provider: str | None
    created_at: datetime


class DashboardStats(BaseModel):
    total_submissions: int
    submissions_by_widget: list[dict]
    submissions_by_country: list[dict]
