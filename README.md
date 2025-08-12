# FSTR API - Система учета перевалов

REST API для учета туристических перевалов с возможностью модерации данных.

## 📌 Возможности

* ✅ Добавление новых перевалов с координатами и фотографиями

* 🔍 Поиск и просмотр информации о перевалах

* ✏️ Редактирование непромодерированных данных

* 👥 Управление пользователями

* 🛡️ Модерация перевалов (new/pending/accepted/rejected)

* 🚀 Быстрый старт

Требования
* Python 3.9+
* PostgreSQL 13+
* Poetry (для управления зависимостями)

## Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/plum__bum/DiplomSF.git
   cd fstr_api
   ```
   
2. Установите зависимости:
  ```
  poetry install
  ```
3. Создайте файл .env:
  ```
  FSTR_DB_HOST=localhost
  FSTR_DB_PORT=5432
  FSTR_DB_LOGIN=postgres
  FSTR_DB_PASS=yourpassword
  FSTR_DB_NAME=fstr
  ```
4. Инициализируйте БД:
  ```
  python -m app.database.init_db
  ```
5. Запустите сервер:
  ```
  uvicorn app.main:app --reload
  ```

## 📚 Документация API
После запуска сервера документация будет доступна:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

## 🗄️ Структура проекта
```
  fstr_api/
  ├── app/                          # Основное приложение
  │   ├── database/                 # Работа с БД
  │   ├── endpoints/                # API endpoints
  │   ├── schemas/                  # Pydantic схемы
  │   └── utils/                    # Вспомогательные утилиты
  ├── tests/                        # Тесты
  ├── migrations/                   # Миграции БД
  ├── .env.example                  # Пример .env файла
  ├── pyproject.toml                # Конфигурация Poetry
  └── README.md                     # Документация

```
