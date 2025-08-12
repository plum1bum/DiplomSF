import pytest
from app.database.models import User, Coords, Image, Pereval, DatabaseQueries
from datetime import datetime


class TestModels:
    def test_user_model(self):
        """Тестирование модели пользователя"""
        user = User(
            id=1,
            email="test@example.com",
            phone="+79991234567",
            fam="Иванов",
            name="Иван",
            otc="Иванович"
        )

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.phone == "+79991234567"
        assert user.fam == "Иванов"
        assert user.name == "Иван"
        assert user.otc == "Иванович"

        # Проверка SQL для создания таблицы
        assert "CREATE TABLE IF NOT EXISTS users" in User.create_table_query()
        assert "id SERIAL PRIMARY KEY" in User.create_table_query()

    def test_coords_model(self):
        """Тестирование модели координат"""
        coords = Coords(
            id=1,
            latitude=45.123456,
            longitude=90.123456,
            height=2500
        )

        assert coords.id == 1
        assert coords.latitude == 45.123456
        assert coords.longitude == 90.123456
        assert coords.height == 2500

        assert "CREATE TABLE IF NOT EXISTS coords" in Coords.create_table_query()

    def test_image_model(self):
        """Тестирование модели изображения"""
        image = Image(
            id=1,
            pereval_id=1,
            img=b'test_image_data',
            title="Тестовое изображение"
        )

        assert image.id == 1
        assert image.pereval_id == 1
        assert image.img == b'test_image_data'
        assert image.title == "Тестовое изображение"

        assert "CREATE TABLE IF NOT EXISTS images" in Image.create_table_query()

    def test_pereval_model(self):
        """Тестирование модели перевала"""
        pereval = Pereval(
            id=1,
            date_added=datetime.now(),
            user_id=1,
            beauty_title="Тестовый перевал",
            title="Тест",
            other_titles="Тестовик",
            connect="Тестовое соединение",
            add_time="12:34:56",
            status="new",
            coord_id=1
        )

        assert pereval.id == 1
        assert pereval.user_id == 1
        assert pereval.beauty_title == "Тестовый перевал"
        assert pereval.status == "new"

        assert "CREATE TABLE IF NOT EXISTS pereval_added" in Pereval.create_table_query()
        assert "status VARCHAR(10) DEFAULT 'new'" in Pereval.create_table_query()


class TestDatabaseQueries:
    def test_get_user_by_id_query(self):
        """Тестирование запроса получения пользователя по ID"""
        query = DatabaseQueries.get_user_by_id()
        assert "SELECT id, email, phone, fam, name, otc FROM users WHERE id = %s" == query

    def test_create_user_query(self):
        """Тестирование запроса создания пользователя"""
        query = DatabaseQueries.create_user()
        assert "INSERT INTO users (email, phone, fam, name, otc)" in query
        assert "RETURNING id" in query

    def test_get_pereval_by_id_query(self):
        """Тестирование запроса получения перевала по ID"""
        query = DatabaseQueries.get_pereval_by_id()
        assert "JOIN coords c ON p.coord_id = c.id" in query
        assert "JOIN users u ON p.user_id = u.id" in query

    def test_update_pereval_query(self):
        """Тестирование запроса обновления перевала"""
        query = DatabaseQueries.update_pereval()
        assert "UPDATE pereval_added" in query
        assert "WHERE id = %s AND status = 'new'" in query

    def test_get_all_tables_creation_queries(self):
        """Тестирование получения всех запросов создания таблиц"""
        queries = DatabaseQueries.get_all_tables_creation_queries()
        assert len(queries) == 4
        assert all(isinstance(q, str) for q in queries)
        assert "CREATE TABLE IF NOT EXISTS users" in queries[0]
        assert "CREATE TABLE IF NOT EXISTS coords" in queries[1]