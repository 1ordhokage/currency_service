
# Тестовое задание: Разработка API для конвертации валют

__Цель:__ Проверить знание и навыки кандидата в области FastAPI, SQLAlchemy и docker-compose.

__Задача:__ Разработать API для конвертации валют с использованием FastAPI, SQLAlchemy. API должен предоставлять возможность получения актуальных курсов валют и конвертации между ними.

__Подзадачи:__
  1. Получение актуальных курсов валют:
        - Создайте модель для хранения информации о валюте (название, код, курс).
        - Реализуйте функцию, которая будет запрашивать актуальные курсы валют с внешнего API (например, https://exchangeratesapi.io/) и сохранять их в базе данных.
        - Реализуйте функцию, которая будет возвращать дату и время последнего обновления курсов в базе данных.

  2. Конвертация между валютами:
        - Реализуйте функцию, которая примет две валюты (исходную и целевую) и сумму для конвертации. Функция должна возвращать результат конвертации на основе актуальных курсов валют из базы данных.

  3. Создание и настройка API:
        - Используйте FastAPI для создания API с тремя эндпоинтами: 
                1) Обновление курсов валют в БД на актуальные курсы.
                2) Выдача даты и времени последнего обновления курсов в БД.
                3) Конвертация между валютами.
        - Сессия с базой данных и эндпоинты должны быть асинхронными.
        - Проект должен запускаться одной командой после клонирования репозитория, предпочтительно через "docker-compose -f docker-compose.yml up --build -d".
        - PostgreSQL также должен работать в контейнере.

Примечания:

    - После завершения разработки, предоставьте инструкции по установке и запуску проекта, а также примеры использования API. 

    - Учтите, что количество запросов к указанному в описании API ограничено. Необходимо оставить на проверку хотя бы 2 запроса, используя предустановленный API ключ. Внешний API с актуальными валютами не принципиален. Если найдете другой сервис, требования такие же — возможность хотя бы 2 раза обновить курсы валют.
...

## Разработано с помощью:
- Python 3.11
- FastAPI 
- PostgreSQL
- SQLAlchemy 
- Pydantic 
- httpx 

Внешний API: https://exchangeratesapi.io

## Сборка и запуск проекта:
    git clone https://github.com/1ordhokage/api_task.git
Из корневой папки проекта:

    docker compose -f docker-compose.yml up --build -d
    

Swagger: `http://0.0.0.0:8000/docs`


## Особенности реализации

1) Обеспечена сохранность данных при рестарте контейнера (использоются volume-ы для хранения файлов СУБД на хост-машине).

2) Так как требовалось хранить время последнего обновления курсов валют, а курсы валют обновляются все разом, то было принято решение создать отдельную таблицу с записями о времени обновления курсов:

    `src/models/update_date_time.py`
    ```Python
    
    class UpdateDateTime(Base):
        __tablename__ = "update_date_time"
        
        id: Mapped[int] = mapped_column(primary_key=True)
        last_update: Mapped[datetime] = mapped_column(
            DateTime,
            default=datetime.now(),
            nullable=False
        )
    ```

3) Требовалось разработать только три эндпоинта: для обновления курсов, для получения времени последнего обновления курсов и для конвертации валют. Возникает проблема: прежде чем обновлять курсы валют, валюты уже должны храниться в бд, а эндпоинта для добавления валют в БД нет. 
    
    - Теперь, до начала работы пользователя с приложением, должна выполниться следующая последовательность действий: 
        `получить валюты из внешнего API -> добавить валюты и время последнего обновления курсов валют в бд`. Получение валют с внешнего API выглядит так:
        
        `src/utils/external_api.py`
        ```Python
        async def get_from_api(option: OptionsToGetEnum) -> dict[str, str | float]:
            """Gets data from the external API. Uses access_key.
            Args:
                option (OptionsToGetEnum): Current variants shown in OptionsToGetEnum.
            Raises:
                HTTPException: HTTP_503_SERVICE_UNAVAILABLE.
            Returns:
                dict[str, str | float]: result, depends on the chosen option.
            """
            source_url = {
                OptionsToGetEnum.SYMBOLS: external_api_settings.SYMBOLS_URL,
                OptionsToGetEnum.RATES: external_api_settings.RATES_URL
            }
            params = {
                "access_key": external_api_settings.KEY
            }
            try:
                async with AsyncClient() as client:
                    result = await client.get(
                        source_url.get(option),
                        params=params
                    )
                    return result.json().get(option.value)
            except HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Currency API is temporary unavailable"
                )


        async def get_currencies() -> list[dict[str, str | float]]:
            """Gets lsit of currencies. Uses get_from_api() to transform data.
            Returns:
                list[dict[str, str | float]]: list of currencies.
            """
            symbols = await get_from_api(OptionsToGetEnum.SYMBOLS)
            rates = await get_from_api(OptionsToGetEnum.RATES)
            currencies = [
                {
                    "code": code,
                    "name": name,
                    "rate": rates.get(code)
                }
                for code, name in symbols.items()
                if rates.get(code)
            ]
            return currencies
        ```
        

    
    - Так как получение валют происходит асинхронно, то выполнить их добавление в БД с помощью синхронной миграции не получится. Решение - start up event FastAPI-приложения:

    `src/main.py`
    ```Python
    
    @app.on_event("startup")
    async def startup_event() -> None:
        """On start-up event. Cheks if db is empty.If empty,
        then inserts currencies from an external API.
        """
        if not await StartUp.check_db_emptyness():
            return
        currencies = await get_currencies()
        await StartUp.insert_currencies(currencies)

    ```


## Примеры запросов:

1) Обновление курсов валют в БД на актуальные курсы.

    ```HTTP
    PUT http://127.0.0.1:8000/api/rates
    ```
    <img width="1421" alt="put_rates" src="https://github.com/1ordhokage/currency_service/assets/61906886/4866b437-3da2-47b7-a283-71bd5e89be2e">

    
2) Выдача даты и времени последнего обновления курсов в БД.

    ```HTTP
    GET http://127.0.0.1:8000/api/last-updated
    ```
    <img width="1421" alt="Снимок экрана 2023-10-25 в 20 58 06" src="https://github.com/1ordhokage/currency_service/assets/61906886/1c1bda9b-a8b2-4860-869e-fccb8a98fae9">

    Пример тела ответа:

    ```JSON
    {
        "last_update": "2023-10-25T17:56:20.164016"
    }
    ```



3) Конвертация между валютами.
   

    ```HTTP
    POST http://127.0.0.1:8000/api/convert
    ```
    Пример тела запроса:
    ```JSON
    {
        "original_code": "RUB",
        "target_code": "USD",
        "amount": 123000.76
    }
    ```

  
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
    
   <img width="711" alt="Снимок экрана 2023-10-25 в 21 02 38" src="https://github.com/1ordhokage/currency_service/assets/61906886/c6a39727-966f-4dd7-9cd5-83743a316b73">
