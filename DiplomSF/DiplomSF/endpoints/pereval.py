from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
import base64
from datetime import time

app = FastAPI()
db_manager = DatabaseManager()


class Coords(BaseModel):
    latitude: float = Field(..., gt=-90, lt=90)
    longitude: float = Field(..., gt=-180, lt=180)
    height: int


class Image(BaseModel):
    img: str  # base64 encoded image
    title: str


class User(BaseModel):
    email: EmailStr
    phone: str
    fam: str
    name: str
    otc: Optional[str] = None


class PerevalInput(BaseModel):
    beauty_title: Optional[str] = None
    title: str
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: Optional[str] = None
    coords: Coords
    user: User
    images: List[Image]

    @validator('add_time')
    def validate_time(cls, v):
        if v:
            try:
                time.fromisoformat(v)
            except ValueError:
                raise ValueError('Invalid time format, expected HH:MM:SS')
        return v


@app.post('/submitData')
async def submit_data(pereval: PerevalInput):
    try:
        # Validate input data
        if not pereval.images:
            raise HTTPException(status_code=400, detail="At least one image is required")

        # Add user
        user_id = db_manager.add_user(
            email=pereval.user.email,
            phone=pereval.user.phone,
            fam=pereval.user.fam,
            name=pereval.user.name,
            otc=pereval.user.otc
        )

        # Add coordinates
        coord_id = db_manager.add_coords(
            latitude=pereval.coords.latitude,
            longitude=pereval.coords.longitude,
            height=pereval.coords.height
        )

        # Add pereval
        pereval_id = db_manager.add_pereval(
            user_id=user_id,
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            add_time=pereval.add_time,
            coord_id=coord_id
        )

        # Add images
        for image in pereval.images:
            try:
                img_data = base64.b64decode(image.img)
            except:
                raise HTTPException(status_code=400, detail="Invalid image data (must be base64)")

            db_manager.add_image(
                pereval_id=pereval_id,
                img=img_data,
                title=image.title
            )

        return {
            "status": 200,
            "message": "Отправлено успешно",
            "id": pereval_id
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": 500,
            "message": f"Ошибка при выполнении операции: {str(e)}",
            "id": None
        }


class PerevalResponse(BaseModel):
    id: int
    status: str
    beauty_title: Optional[str] = None
    title: str
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: Optional[str] = None
    coords: Coords
    user: User
    images: List[Image]


@app.get('/submitData/{pereval_id}', response_model=PerevalResponse)
async def get_pereval(pereval_id: int):
    try:
        db_manager.connect()
        with db_manager.conn.cursor() as cursor:
            # Get pereval info
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
            pereval_data = cursor.fetchone()

            if not pereval_data:
                raise HTTPException(status_code=404, detail="Pereval not found")

            # Get images
            cursor.execute("""
                SELECT img, title FROM images
                WHERE pereval_id = %s
            """, (pereval_id,))
            images_data = cursor.fetchall()

            images = []
            for img_data in images_data:
                img_base64 = base64.b64encode(img_data[0]).decode('utf-8')
                images.append({
                    "img": img_base64,
                    "title": img_data[1]
                })

            response = {
                "id": pereval_data[0],
                "beauty_title": pereval_data[1],
                "title": pereval_data[2],
                "other_titles": pereval_data[3],
                "connect": pereval_data[4],
                "add_time": str(pereval_data[5]) if pereval_data[5] else None,
                "status": pereval_data[6],
                "coords": {
                    "latitude": float(pereval_data[7]),
                    "longitude": float(pereval_data[8]),
                    "height": pereval_data[9]
                },
                "user": {
                    "email": pereval_data[10],
                    "phone": pereval_data[11],
                    "fam": pereval_data[12],
                    "name": pereval_data[13],
                    "otc": pereval_data[14]
                },
                "images": images
            }

            return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_manager.disconnect()


@app.patch('/submitData/{pereval_id}')
async def update_pereval(pereval_id: int, pereval: PerevalInput):
    try:
        db_manager.connect()
        with db_manager.conn.cursor() as cursor:
            # Check if pereval exists and has status 'new'
            cursor.execute("""
                SELECT status, user_id FROM pereval_added
                WHERE id = %s
            """, (pereval_id,))
            pereval_status = cursor.fetchone()

            if not pereval_status:
                return {"state": 0, "message": "Pereval not found"}

            if pereval_status[0] != 'new':
                return {"state": 0, "message": "Pereval can't be edited because it's not in 'new' status"}

            # Get user_id from the original pereval
            user_id = pereval_status[1]

            # Update coordinates
            cursor.execute("""
                UPDATE coords
                SET latitude = %s, longitude = %s, height = %s
                WHERE id = (
                    SELECT coord_id FROM pereval_added WHERE id = %s
                )
                RETURNING id
            """, (
                pereval.coords.latitude,
                pereval.coords.longitude,
                pereval.coords.height,
                pereval_id
            ))
            coord_id = cursor.fetchone()[0]

            # Update pereval
            cursor.execute("""
                UPDATE pereval_added
                SET beauty_title = %s, title = %s, other_titles = %s,
                    connect = %s, add_time = %s, coord_id = %s
                WHERE id = %s
            """, (
                pereval.beauty_title,
                pereval.title,
                pereval.other_titles,
                pereval.connect,
                pereval.add_time,
                coord_id,
                pereval_id
            ))

            # Delete old images
            cursor.execute("""
                DELETE FROM images WHERE pereval_id = %s
            """, (pereval_id,))

            # Add new images
            for image in pereval.images:
                try:
                    img_data = base64.b64decode(image.img)
                except:
                    db_manager.conn.rollback()
                    return {"state": 0, "message": "Invalid image data (must be base64)"}

                cursor.execute("""
                    INSERT INTO images (pereval_id, img, title)
                    VALUES (%s, %s, %s)
                """, (pereval_id, img_data, image.title))

            db_manager.conn.commit()
            return {"state": 1, "message": "Pereval updated successfully"}

    except Exception as e:
        db_manager.conn.rollback()
        return {"state": 0, "message": f"Error updating pereval: {str(e)}"}
    finally:
        db_manager.disconnect()


@app.get('/submitData/', response_model=List[Dict[str, Any]])
async def get_user_perevals(user_email: str = Query(..., alias="user__email")):
    try:
        db_manager.connect()
        with db_manager.conn.cursor() as cursor:
            # Get user's perevals
            cursor.execute("""
                SELECT p.id, p.beauty_title, p.title, p.status
                FROM pereval_added p
                JOIN users u ON p.user_id = u.id
                WHERE u.email = %s
            """, (user_email,))
            perevals = cursor.fetchall()

            if not perevals:
                return []

            response = []
            for pereval in perevals:
                response.append({
                    "id": pereval[0],
                    "beauty_title": pereval[1],
                    "title": pereval[2],
                    "status": pereval[3]
                })

            return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_manager.disconnect()