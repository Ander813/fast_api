from src.app.users import admin_routes as users_admin
from src.app.records import admin_routes as records_admin
from fastapi import APIRouter


admin_router = APIRouter()

admin_router.include_router(records_admin.admin_router,
                            prefix="/records",
                            tags=['admin-records'])

admin_router.include_router(users_admin.admin_router,
                            prefix="/users",
                            tags=['admin-users'])