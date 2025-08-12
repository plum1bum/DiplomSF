import pytest
from app.database.manager import DatabaseManager
from app.database.models import DatabaseQueries
import os


class TestDatabaseManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестовой БД"""
        os.environ['FSTR_DB_NAME'] = 'fstr_test'
        self.db = DatabaseManager()
        self.db.connect()

        # Создаем тестовые таблицы
        with self.db.conn.cursor() as cursor:
            for query in DatabaseQueries.get_all_tables_creation_queries():
                cursor.execute(query)
            self.db.conn.commit()

        yield

        # Очистка после тестов
        with self.db.conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE images, pereval_added, coords, users RESTART IDENTITY CASCADE")
            self.db.conn.commit()
        self.db.disconnect()

    def test_add_user(self):
        """Тестирование добавления пользователя"""
        user_id = self.db.add_user(
            email="test@example.com",
            phone="+79991234567",
            fam="Иванов",
            name="Иван"
        )

        assert isinstance(user_id, int)
        assert user_id > 0

        # Проверяем, что пользователь действительно добавлен
        with self.db.conn.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            assert result[0] == "test@example.com"

    def test_add_coords(self):
        """Тестирование добавления координат"""
        coord_id = self.db.add_coords(
            latitude=45.123456,
            longitude=90.123456,
            height=2500
        )

        assert isinstance(coord_id, int)

        with self.db.conn.cursor() as cursor:
            cursor.execute("SELECT latitude FROM coords WHERE id = %s", (coord_id,))
            assert float(cursor.fetchone()[0]) == 45.123456

    def test_add_pereval(self):
        """Тестирование добавления перевала"""
        # Сначала добавляем пользователя и координаты
        user_id = self.db.add_user(
            email="test@example.com",
            phone="+79991234567",
            fam="Иванов",
            name="Иван"
        )

        coord_id = self.db.add_coords(
            latitude=45.123456,
            longitude=90.123456,
            height=2500
        )

        # Добавляем перевал
        pereval_id = self.db.add_pereval(
            user_id=user_id,
            beauty_title="Тестовый перевал",
            title="Тест",
            other_titles="Тестовик",
            connect="Тестовое соединение",
            add_time="12:34:56",
            coord_id=coord_id
        )

        assert isinstance(pereval_id, int)

        # Проверяем статус по умолчанию
        with self.db.conn.cursor() as cursor:
            cursor.execute("SELECT status FROM pereval_added WHERE id = %s", (pereval_id,))
            assert cursor.fetchone()[0] == 'new'

    def test_add_image(self):
        """Тестирование добавления изображения"""
        # Создаем тестовые данные
        user_id = self.db.add_user(email="test@example.com", phone="123", fam="Иванов", name="Иван")
        coord_id = self.db.add_coords(latitude=45, longitude=90, height=1000)
        pereval_id = self.db.add_pereval(
            user_id=user_id,
            title="Тест",
            coord_id=coord_id,
            beauty_title=None,
            other_titles=None,
            connect=None,
            add_time=None
        )

        # Добавляем изображение
        image_id = self.db.add_image(
            pereval_id=pereval_id,
            img=b'test_image_data',
            title="Тест"
        )

        assert isinstance(image_id, int)

        with self.db.conn.cursor() as cursor:
            cursor.execute("SELECT title FROM images WHERE id = %s", (image_id,))
            assert cursor.fetchone()[0] == "Тест"