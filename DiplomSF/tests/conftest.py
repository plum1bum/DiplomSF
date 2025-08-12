import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.manager import DatabaseManager
from app.database.models import DatabaseQueries
import os


@pytest.fixture(scope="session")
def test_db():
    """Фикстура тестовой базы данных"""
    os.environ['FSTR_DB_NAME'] = 'fstr_test'
    db = DatabaseManager()

    # Инициализация тестовой БД
    db.connect()
    try:
        with db.conn.cursor() as cursor:
            for query in DatabaseQueries.get_all_tables_creation_queries():
                cursor.execute(query)
            db.conn.commit()
    except Exception as e:
        db.conn.rollback()
        raise e

    yield db

    # Очистка после тестов
    db.connect()
    with db.conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE images, pereval_added, coords, users RESTART IDENTITY CASCADE")
        db.conn.commit()
    db.disconnect()


@pytest.fixture
def client(test_db):
    """Фикстура тестового клиента"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "phone": "+79991234567",
        "fam": "Иванов",
        "name": "Иван",
        "otc": "Иванович"
    }


@pytest.fixture
def test_pereval_data(test_user_data):
    return {
        "beauty_title": "Тестовый перевал",
        "title": "Тест",
        "other_titles": "Тестовик",
        "connect": "Тестовое соединение",
        "add_time": "12:34:56",
        "coords": {
            "latitude": 45.123456,
            "longitude": 90.123456,
            "height": 2500
        },
        "user": test_user_data,
        "images": [
            {
                "img": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
                "title": "Тестовое изображение"
            }
        ]
    }