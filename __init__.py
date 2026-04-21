from handlers.main import main_router
from handlers.questions import questions_router
from handlers.applications import applications_router
from handlers.admin import admin_router

__all__ = ["main_router", "questions_router", "applications_router", "admin_router"]
