from src.app.users import routes as users_routes
from src.app.records import routes as records_routes
from src.app.auth import routes as auth_routes
from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router(records_routes.router,
                           prefix="/records",
                           tags=["records"])


main_router.include_router(auth_routes.router,
                           prefix='/auth',
                           tags=['authorization'])