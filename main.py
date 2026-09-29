from mainbackend import app
from auth import router as auth_router

app.include_router(auth_router)