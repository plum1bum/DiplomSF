from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.database.manager import DatabaseManager
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.exceptions import UserNotFound

router = APIRouter(prefix="/users", tags=["users"])


# Получение списка всех пользователей
@router.get("/", response_model=List[UserResponse])
async def get_users(
        limit: int = Query(10, gt=0, le=100),
        offset: int = Query(0, ge=0),
        db: DatabaseManager = Depends(DatabaseManager)
):
    """
    Получить список пользователей с пагинацией.
    """
    try:
        db.connect()
        with db.conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, phone, fam, name, otc FROM users LIMIT %s OFFSET %s",
                (limit, offset)
            )
            users = cursor.fetchall()
            return [
                {
                    "id": user[0],
                    "email": user[1],
                    "phone": user[2],
                    "fam": user[3],
                    "name": user[4],
                    "otc": user[5]
                }
                for user in users
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()


# Получение пользователя по ID
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        db: DatabaseManager = Depends(DatabaseManager)
):
    """
    Получить пользователя по его ID.
    """
    try:
        db.connect()
        with db.conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, phone, fam, name, otc FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            if not user:
                raise UserNotFound(user_id)
            return {
                "id": user[0],
                "email": user[1],
                "phone": user[2],
                "fam": user[3],
                "name": user[4],
                "otc": user[5]
            }
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()


# Поиск пользователей по email
@router.get("/search/", response_model=List[UserResponse])
async def search_users(
        email: Optional[str] = Query(None),
        db: DatabaseManager = Depends(DatabaseManager)
):
    """
    Поиск пользователей по email (частичное совпадение).
    """
    try:
        db.connect()
        with db.conn.cursor() as cursor:
            if email:
                cursor.execute(
                    "SELECT id, email, phone, fam, name, otc FROM users WHERE email LIKE %s",
                    (f"%{email}%",)
                )
            else:
                cursor.execute(
                    "SELECT id, email, phone, fam, name, otc FROM users"
                )
            users = cursor.fetchall()
            return [
                {
                    "id": user[0],
                    "email": user[1],
                    "phone": user[2],
                    "fam": user[3],
                    "name": user[4],
                    "otc": user[5]
                }
                for user in users
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()


# Обновление данных пользователя
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: DatabaseManager = Depends(DatabaseManager)
):
    """
    Обновить данные пользователя (частичное обновление).
    """
    try:
        db.connect()
        with db.conn.cursor() as cursor:
            # Проверяем существование пользователя
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                raise UserNotFound(user_id)

            # Формируем запрос для частичного обновления
            update_fields = []
            update_values = []
            for field, value in user_data.dict(exclude_unset=True).items():
                update_fields.append(f"{field} = %s")
                update_values.append(value)

            if not update_fields:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update"
                )

            update_query = f"""
                UPDATE users
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, email, phone, fam, name, otc
            """
            update_values.append(user_id)

            cursor.execute(update_query, update_values)
            updated_user = cursor.fetchone()
            db.conn.commit()

            return {
                "id": updated_user[0],
                "email": updated_user[1],
                "phone": updated_user[2],
                "fam": updated_user[3],
                "name": updated_user[4],
                "otc": updated_user[5]
            }
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()