import pytest
from fastapi import status
from app.schemas.pereval import PerevalResponse


class TestPerevalEndpoints:
    def test_submit_data_success(self, client, test_pereval_data):
        # Тест успешного добавления перевала
        response = client.post("/submitData/", json=test_pereval_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == 200
        assert response.json()["message"] == "Отправлено успешно"
        assert "id" in response.json()

    def test_submit_data_validation_error(self, client, test_pereval_data):
        # Тест ошибки валидации
        invalid_data = test_pereval_data.copy()
        invalid_data["coords"]["latitude"] = 100  # Некорректная широта

        response = client.post("/submitData/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_pereval_success(self, client, test_pereval_data):
        # Сначала создаем перевал
        create_response = client.post("/submitData/", json=test_pereval_data)
        pereval_id = create_response.json()["id"]

        # Тест получения перевала
        response = client.get(f"/submitData/{pereval_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == pereval_id
        assert data["status"] == "new"
        assert data["title"] == test_pereval_data["title"]
        assert len(data["images"]) == 1

    def test_get_pereval_not_found(self, client):
        # Тест запроса несуществующего перевала
        response = client.get("/submitData/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_pereval_success(self, client, test_pereval_data):
        # Создаем перевал
        create_response = client.post("/submitData/", json=test_pereval_data)
        pereval_id = create_response.json()["id"]

        # Обновляем данные
        updated_data = test_pereval_data.copy()
        updated_data["title"] = "Обновленный тест"

        # Тест обновления
        response = client.patch(f"/submitData/{pereval_id}", json=updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["state"] == 1

        # Проверяем, что данные изменились
        get_response = client.get(f"/submitData/{pereval_id}")
        assert get_response.json()["title"] == "Обновленный тест"

    def test_update_pereval_wrong_status(self, client, test_pereval_data, test_db):
        # Создаем перевал
        create_response = client.post("/submitData/", json=test_pereval_data)
        pereval_id = create_response.json()["id"]

        # Меняем статус на 'pending' напрямую в БД
        test_db.connect()
        with test_db.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE pereval_added SET status = 'pending' WHERE id = %s",
                (pereval_id,)
            )
            test_db.conn.commit()
        test_db.disconnect()

        # Пытаемся обновить
        updated_data = test_pereval_data.copy()
        updated_data["title"] = "Не должно обновиться"

        response = client.patch(f"/submitData/{pereval_id}", json=updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["state"] == 0
        assert "not in 'new' status" in response.json()["message"]

    def test_get_user_perevals_success(self, client, test_pereval_data):
        # Создаем несколько перевалов
        client.post("/submitData/", json=test_pereval_data)

        # Второй перевал с тем же email
        second_data = test_pereval_data.copy()
        second_data["title"] = "Второй перевал"
        client.post("/submitData/", json=second_data)

        # Тест получения перевалов пользователя
        email = test_pereval_data["user"]["email"]
        response = client.get(f"/submitData/?user__email={email}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert {item["title"] for item in data} == {"Тест", "Второй перевал"}

    def test_get_user_perevals_empty(self, client):
        # Тест для пользователя без перевалов
        response = client.get("/submitData/?user__email=empty@example.com")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []