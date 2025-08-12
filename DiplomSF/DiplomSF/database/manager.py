import os
import psycopg2
from psycopg2 import sql


class DatabaseManager:
    def __init__(self):
        self.db_host = os.getenv('FSTR_DB_HOST')
        self.db_port = os.getenv('FSTR_DB_PORT')
        self.db_login = os.getenv('FSTR_DB_LOGIN')
        self.db_pass = os.getenv('FSTR_DB_PASS')
        self.db_name = os.getenv('FSTR_DB_NAME', 'fstr')
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_login,
            password=self.db_pass,
            database=self.db_name
        )

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def add_user(self, email, phone, fam, name, otc=None):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO users (email, phone, fam, name, otc)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """)
                cursor.execute(query, (email, phone, fam, name, otc))
                user_id = cursor.fetchone()[0]
                self.conn.commit()
                return user_id
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def add_coords(self, latitude, longitude, height):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO coords (latitude, longitude, height)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """)
                cursor.execute(query, (latitude, longitude, height))
                coord_id = cursor.fetchone()[0]
                self.conn.commit()
                return coord_id
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def add_pereval(self, user_id, beauty_title, title, other_titles, connect, add_time, coord_id):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO pereval_added 
                    (user_id, beauty_title, title, other_titles, connect, add_time, coord_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'new')
                    RETURNING id
                """)
                cursor.execute(query, (user_id, beauty_title, title, other_titles, connect, add_time, coord_id))
                pereval_id = cursor.fetchone()[0]
                self.conn.commit()
                return pereval_id
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def add_image(self, pereval_id, img, title):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO images (pereval_id, img, title)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """)
                cursor.execute(query, (pereval_id, img, title))
                image_id = cursor.fetchone()[0]
                self.conn.commit()
                return image_id
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def get_pereval(self, pereval_id: int):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                # Получение данных о перевале
                cursor.execute("""
                    SELECT p.id, p.beauty_title, p.title, p.other_titles, p.connect, 
                           p.add_time, p.status, 
                           c.latitude, c.longitude, c.height,
                           u.email, u.phone, u.fam, u.name, u.otc
                    FROM pereval_added p
                    JOIN coords c ON p.coord_id = c.id
                    JOIN users u ON p.user_id = u.id
                    WHERE p.id = %s
                """, (pereval_id,))
                return cursor.fetchone()
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def get_pereval_images(self, pereval_id: int):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT img, title FROM images
                    WHERE pereval_id = %s
                """, (pereval_id,))
                return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def get_user_perevals(self, email: str):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.beauty_title, p.title, p.status
                    FROM pereval_added p
                    JOIN users u ON p.user_id = u.id
                    WHERE u.email = %s
                """, (email,))
                return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            self.disconnect()