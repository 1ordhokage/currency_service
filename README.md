
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

Внешний API: https://exchangeratesapi.io

## Сборка и запуск проекта:
    git clone https://github.com/1ordhokage/api_task.git
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

1) Обновление курсов валют в БД на актуальные курсы.

 

    
2) Выдача даты и времени последнего обновления курсов в БД.

   



3) Конвертация между валютами.
   

   

  
    Пример тела ответа:

    ```JSON
    {
        "original_code": "RUB",
        "target_code": "USD",
        "amount": 123000.76,
        "result": 1308.52,
        "date_time": "2023-10-25T18:02:15.354984"
    }
    ```
    
