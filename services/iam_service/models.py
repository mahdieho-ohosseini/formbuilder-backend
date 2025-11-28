from sqlalchemy import Column, String, TIMESTAMP, Boolean,Integer,Text,DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from services.iam_service.app.core.database import get_entitybase


EntityBase = get_entitybase()
