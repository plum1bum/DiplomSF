from fastapi import FastAPI
from app.database.manager import DatabaseManager
from app.endpoints import pereval, users

app = FastAPI(title="FSTR API", version="1.0.0")

# Инициализация менеджера БД
db_manager = DatabaseManager()

# Подключение роутеров
app.include_router(pereval.router, prefix="/submitData", tags=["pereval"])
app.include_router(users.router, prefix="/users", tags=["users"])