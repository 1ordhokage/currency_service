
# API для конвертации валют

## Разработано с помощью:
- Python 3.11
- FastAPI 
- PostgreSQL
- Redis
- Celery
- Flower
- SQLAlchemy 
- Pydantic 
- httpx 


## Сборка и запуск проекта:
    git clone https://github.com/1ordhokage/currency_service.git
Из корневой папки проекта:

    docker compose up -d
    

Swagger: `http://0.0.0.0:8000/docs`

Flower: `http://0.0.0.0:8888`




## Особенности реализации

1) __Работа с асинхронностью__
    
    Все эндпоинты асинхронные, подключение к бд также через асинхронный драйвер asyncpg.

2) __Фоновые задачи__

    При регистрации пользователя, ему на почту отправояется welcome email в фоновом режиме `Celery + Redis`:

    `src/tasks/tasks.py`
    ```Python
    
   @celery.task
    def send_welcome_email(user_email: str):
        ...
    ```

    
    `src/api/auth.py`
    ```Python
    
    @router.post(
        "/register",
        status_code=status.HTTP_201_CREATED,
        response_model=UserResponseSchema
    )
    async def register(schema: UserRequestSchema, service: AuthService = Depends()):
        user = await service.create_user(schema)
        send_welcome_email.delay(schema.email)
        return user

    ```


    
<img width="634" alt="Снимок экрана 2023-11-30 в 21 09 25" src="https://github.com/1ordhokage/currency_service/assets/61906886/88285f87-2d37-41f9-a7fa-29af90eef76e">

    

3) __Оптимизация производительности__

    Используется кэширование для эндпоинта с получением всех курсов валют.

    `src/main.py`
    ```Python
    
    @app.on_event("startup")
    async def startup_event() -> None:
        redis = aioredis.from_url(
            redis_settings.connection_string,
            encoding="utf8",
            decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        # ...
    ```

    
    `src/api/currencies.py`
    ```Python
    
    @router.get("", response_model=list[CurrencySchema])
    @cache(expire=600) 
    async def get_currencies(service: CurrenciesService = Depends()):
        currencies = await service.get_currencies()
        return currencies

    ```

4) __Интеграция с внешним API__

    Валюты и их актуальные курсы запрашиваются с  https://exchangeratesapi.io/ (`src/utils/external_api.py`)

5) __Аутентификация__:
    
    JWT + Bearer

6) __Авторизация__:

    _user_ может:
    - получить актуальные валюты и их курсы
    - Конвертировать из одной валюты в другую
    - получить/обновить/удалить информацию о себе

    _admin_ пользователь может все то же что и _user_, но еще и:
    - Обновить курсы валют из внешнего API
    - Просмотреть время последнего обновления курса валют

    Авторизация обеспечивается через JWT. 

7) Обеспечена сохранность данных при рестарте контейнера (использоются volume-ы для хранения файлов СУБД на хост-машине).

8) До начала работы пользователя с приложением, должна выполниться следующая последовательность действий: 
        `получить валюты из внешнего API -> добавить валюты и время последнего обновления курсов валют в бд`. 
        
    - Так как получение валют происходит асинхронно, то выполнить их добавление в БД с помощью синхронной миграции не получится. Решение - start up event FastAPI-приложения:

    `src/main.py`
    ```Python
    
    @app.on_event("startup")
    async def startup_event() -> None:
        # ...
        if not await StartUp.check_db_emptyness():
            return
        currencies = await get_currencies()
        await StartUp.insert_currencies(currencies)

    ```



## API:

1) __Регистрация__:

    ```
    curl -X 'POST' \
      'http://127.0.0.1:8000/auth/register' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "email": "example@example.com",
      "text_password": "12345678",
      "role": "admin"
    }'
    ```
    Ответ:

    201
    ```JSON
    {
      "id": 5,
      "email": "example@example.com",
      "role": "admin"
    }
    ```

    
2) __Аутентификация__:
   
    ```
    curl -X 'POST' \
      'http://127.0.0.1:8000/auth/token' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -d 'grant_type=&username=example%40example.com&password=12345678&scope=&client_id=&client_secret='
    ```
    Ответ:

    200
    ```JSON
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgxNDMsImV4cCI6MTcwMTM3MTc0Mywic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.ui9xT-c2U_DM-cIZDjWZyvKdyheiUc-DHtueNEMxk44",
      "token_type": "bearer"
    }
    ```
   



3) __Получение списка всех валют (курс к евро)__:
   
    ```
    curl -X 'GET' \
      'http://127.0.0.1:8000/currencies' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI'
    ```
    Ответ:

    200
    ```JSON
    [
      {
        "code": "AFN",
        "name": "Afghan Afghani",
        "rate": 75.68504333496094
      },
      {
        "code": "ALL",
        "name": "Albanian Lek",
        "rate": 101.77205657958984
      },
      ...
    ]
    ```

   
4) __Обновить курсы валют__:
   
    ```
   curl -X 'PUT' \
      'http://127.0.0.1:8000/currencies/rates' \
      -H 'accept: */*' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI'
    ```
    Ответ:

    204


  
5) __Посмотреть время последнего обновления валют__:
   
    ```
   curl -X 'GET' \
      'http://127.0.0.1:8000/currencies/last-updated' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI'

    ```
    Ответ:

    200
    ```JSON
    {
      "last_update": "2023-11-30T18:21:07.099708"
    }
    ```

6) __Конвертировать валюты__:
   
    ```
    curl -X 'POST' \
      'http://127.0.0.1:8000/currencies/convert' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI' \
      -H 'Content-Type: application/json' \
      -d '{
      "original_code": "USD",
      "target_code": "RUB",
      "amount": 128750
    }'
    ```
    Ответ:

    200
    ```JSON
    {
      "original_code": "USD",
      "target_code": "RUB",
      "amount": 128750,
      "result": 11584282.88,
      "date_time": "2023-11-30T18:25:21.917362"
    }
    ```

7) __Получить свои данные__:
   
    ```
    curl -X 'GET' \
      'http://127.0.0.1:8000/users/me' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI'
    ```
    Ответ:

    200
    ```JSON
    {
      "id": 5,
      "email": "example@example.com",
      "role": "admin"
    }
    ```

8) __Обновить свои данные__:
   
    ```
    curl -X 'PUT' \
      'http://127.0.0.1:8000/users/me' \
      -H 'accept: */*' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI' \
      -H 'Content-Type: application/json' \
      -d '{
      "email": "new@mail.com",
      "text_password": "11111111"
    }'
    ```
    Ответ:

    204


9) __Удалить свои данные__:
   
    ```
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/users/me' \
      -H 'accept: */*' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzNjgyMzAsImV4cCI6MTcwMTM3MTgzMCwic3ViIjoiNSIsInJvbGUiOiJhZG1pbiJ9.4zeQZDhiSB0_SYRhPe8cOG95LnHDbbqYGicvm7uOkMI'
    ```
    Ответ:

    204


   
    
