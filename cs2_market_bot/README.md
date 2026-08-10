# CS2 Market Bot — Telegram бот для поиска выгодных лотов скинов CS2/CS:GO

## Краткое описание архитектуры

Бот построен по модульному принципу с четким разделением ответственности:

### Слои архитектуры:

1. **Bot Layer** (`bot/`) — взаимодействие с Telegram через aiogram 3.x
2. **Core Layer** (`core/`) — базовая инфраструктура (config, database, models)
3. **Market Layer** (`market/`) — работа с рыночными данными (providers, scanner, pricing)
4. **Workers Layer** (`workers/`) — фоновые задачи (scheduler, market worker)
5. **Payments Layer** (`payments/`) — оплата премиума через Telegram Stars

## Структура проекта

```
cs2_market_bot/
├── bot/
│   ├── main.py              # Точка входа бота
│   ├── handlers/            # Обработчики команд
│   ├── keyboards/           # Inline-клавиатуры
│   ├── middlewares/         # Middleware (auth, rate limit)
│   └── utils/               # Утилиты (форматирование)
├── core/
│   ├── config.py            # Настройки из env
│   ├── database.py          # Подключение к БД
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   └── logging.py           # Логирование
├── market/
│   ├── base_provider.py     # Абстрактный провайдер
│   ├── mock_provider.py     # Mock для разработки
│   ├── scanner.py           # Сервис сканирования
│   ├── pricing.py           # Расчет выгоды
│   └── liquidity.py         # Расчет ликвидности
├── workers/
│   ├── scheduler.py         # APScheduler
│   ├── scheduler_worker.py  # Воркер планировщика
│   └── market_worker.py     # Воркер сканирования
├── payments/
│   └── stars.py             # Telegram Stars
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

## Инструкция по запуску через Docker

### 1. Клонирование и настройка

```bash
cd cs2_market_bot

# Скопируйте .env.example в .env
cp .env.example .env

# Отредактируйте .env и укажите ваш токен бота
# TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 2. Запуск через Docker Compose

```bash
# Запуск всех сервисов (бот, воркер, PostgreSQL, Redis)
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
docker-compose logs -f worker

# Остановка
docker-compose down
```

### 3. Запуск без Docker (локальная разработка)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
# Отредактируйте .env

# Запуск бота
python -m bot.main

# Запуск воркера сканирования (в отдельном терминале)
python -m workers.scheduler_worker
```

## Требования к окружению

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker и docker-compose (опционально)

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | (обязательно) |
| `MARKET_PROVIDER` | Провайдер данных (mock/steam/csfloat) | `mock` |
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL подключения к Redis | `redis://localhost:6379/0` |
| `FEE_PERCENT` | Комиссия площадки | `0.15` |
| `DEFAULT_CURRENCY` | Валюта (RUB/USD) | `RUB` |

## Функционал MVP

### Команды бота:
- `/start` — Главное меню
- `/help` — Справка
- `/scan` — Запустить сканирование (через кнопки)
- `/filters` — Настроить фильтры
- `/signals` — Последние сигналы
- `/premium` — Информация о премиуме

### Ограничения тарифов:

**Free:**
- До 3 активных фильтров
- Обновление каждые 30 минут
- До 10 последних сигналов

**Premium:**
- До 20 активных фильтров
- Обновление каждые 5 минут
- До 100 сигналов
- История за 7 дней

## Добавление нового провайдера

Для добавления нового источника данных (Steam, CSFloat, Skinport и т.д.):

1. Создайте файл `market/new_provider.py`
2. Унаследуйтесь от `BaseMarketProvider`
3. Реализуйте методы:
   - `fetch_item_stats()`
   - `fetch_listings()`
   - `search_items()`
4. Обновите `MARKET_PROVIDER` в `.env`

## Важные замечания

⚠️ **Дисклеймер**: Бот предоставляет аналитику, а не финансовый совет. Торговля скинами связана с рисками.

- Не храните пароли от Steam
- Соблюдайте лимиты API
- Используйте rate limiting
- Не гарантируйте прибыль пользователям
