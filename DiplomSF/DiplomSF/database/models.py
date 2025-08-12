from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Модель пользователя"""
    id: int
    email: str
    phone: str
    fam: str
    name: str
    otc: Optional[str] = None

    @staticmethod
    def create_table_query() -> str:
        """SQL-запрос для создания таблицы пользователей"""
        return """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            fam VARCHAR(80) NOT NULL,
            name VARCHAR(80) NOT NULL,
            otc VARCHAR(80)
        )
        """


@dataclass
class Coords:
    """Модель координат"""
    id: int
    latitude: float
    longitude: float
    height: int

    @staticmethod
    def create_table_query() -> str:
        """SQL-запрос для создания таблицы координат"""
        return """
        CREATE TABLE IF NOT EXISTS coords (
            id SERIAL PRIMARY KEY,
            latitude DECIMAL(10, 7) NOT NULL,
            longitude DECIMAL(10, 7) NOT NULL,
            height INTEGER NOT NULL
        )
        """


@dataclass
class Image:
    """Модель изображения"""
    id: int
    pereval_id: int
    img: bytes
    title: str

    @staticmethod
    def create_table_query() -> str:
        """SQL-запрос для создания таблицы изображений"""
        return """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            pereval_id INTEGER REFERENCES pereval_added(id),
            img BYTEA NOT NULL,
            title VARCHAR(255) NOT NULL
        )
        """


@dataclass
class Pereval:
    """Модель перевала"""
    id: int
    date_added: datetime
    user_id: int
    beauty_title: Optional[str]
    title: str
    other_titles: Optional[str]
    connect: Optional[str]
    add_time: Optional[str]
    status: str
    coord_id: int

    @staticmethod
    def create_table_query() -> str:
        """SQL-запрос для создания таблицы перевалов"""
        return """
        CREATE TABLE IF NOT EXISTS pereval_added (
            id SERIAL PRIMARY KEY,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL REFERENCES users(id),
            beauty_title VARCHAR(255),
            title VARCHAR(255) NOT NULL,
            other_titles VARCHAR(255),
            connect VARCHAR(255),
            add_time TIME,
            status VARCHAR(10) DEFAULT 'new' CHECK (status IN ('new', 'pending', 'accepted', 'rejected')),
            coord_id INTEGER NOT NULL REFERENCES coords(id)
        )
        """


class DatabaseQueries:
    """Класс с базовыми SQL-запросами для работы с БД"""

    @staticmethod
    def get_user_by_id() -> str:
        return "SELECT id, email, phone, fam, name, otc FROM users WHERE id = %s"

    @staticmethod
    def get_user_by_email() -> str:
        return "SELECT id, email, phone, fam, name, otc FROM users WHERE email = %s"

    @staticmethod
    def create_user() -> str:
        return """
        INSERT INTO users (email, phone, fam, name, otc)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """

    @staticmethod
    def update_user() -> str:
        return """
        UPDATE users
        SET email = %s, phone = %s, fam = %s, name = %s, otc = %s
        WHERE id = %s
        RETURNING id, email, phone, fam, name, otc
        """

    @staticmethod
    def create_coords() -> str:
        return """
        INSERT INTO coords (latitude, longitude, height)
        VALUES (%s, %s, %s)
        RETURNING id
        """

    @staticmethod
    def create_pereval() -> str:
        return """
        INSERT INTO pereval_added 
        (user_id, beauty_title, title, other_titles, connect, add_time, coord_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'new')
        RETURNING id
        """

    @staticmethod
    def get_pereval_by_id() -> str:
        return """
        SELECT p.id, p.beauty_title, p.title, p.other_titles, p.connect, 
               p.add_time, p.status, 
               c.latitude, c.longitude, c.height,
               u.email, u.phone, u.fam, u.name, u.otc
        FROM pereval_added p
        JOIN coords c ON p.coord_id = c.id
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
        """

    @staticmethod
    def update_pereval() -> str:
        return """
        UPDATE pereval_added
        SET beauty_title = %s, title = %s, other_titles = %s,
            connect = %s, add_time = %s, coord_id = %s
        WHERE id = %s AND status = 'new'
        RETURNING id
        """

    @staticmethod
    def get_user_perevals() -> str:
        return """
        SELECT p.id, p.beauty_title, p.title, p.status
        FROM pereval_added p
        JOIN users u ON p.user_id = u.id
        WHERE u.email = %s
        """

    @staticmethod
    def create_image() -> str:
        return """
        INSERT INTO images (pereval_id, img, title)
        VALUES (%s, %s, %s)
        RETURNING id
        """

    @staticmethod
    def get_images_for_pereval() -> str:
        return "SELECT img, title FROM images WHERE pereval_id = %s"

    @staticmethod
    def get_all_tables_creation_queries() -> List[str]:
        """Возвращает все SQL-запросы для создания таблиц"""
        return [
            User.create_table_query(),
            Coords.create_table_query(),
            Pereval.create_table_query(),
            Image.create_table_query()
        ]