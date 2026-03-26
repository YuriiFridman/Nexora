# Tiscord

Tiscord — Discord-подобное приложение, состоящее из:
- **Backend**: FastAPI (Python 3.11+), WebSocket `/ws`, REST API с префиксом `/api/v1`.
- **Desktop/Frontend**: Vite + React + TypeScript (папка `desktop`). (Также есть скрипты для Tauri-сборки.)

> Ниже — максимально подробная инструкция: как установить зависимости, запустить локально, собрать фронтенд, а также варианты деплоя на хостинг (VPS/Docker).

---

## Содержание

- [1. Требования](#1-требования)
- [2. Структура репозитория](#2-структура-репозитория)
- [3. Быстрый старт (локально за 10 минут)](#3-быстрый-старт-локально-за-10-минут)
- [4. Настройка переменных окружения (.env)](#4-настройка-переменных-окружения-env)
- [5. Локальный запуск Backend (FastAPI)](#5-локальный-запуск-backend-fastapi)
- [6. Локальный запуск Desktop/Frontend (Vite)](#6-локальный-запуск-desktopfrontend-vite)
- [7. Проверка, что всё работает](#7-проверка-что-всё-работает)
- [8. Сборка Frontend для продакшена](#8-сборка-frontend-для-продакшена)
- [9. Деплой на VPS (Linux) без Docker: systemd + reverse proxy](#9-деплой-на-vps-linux-без-docker-systemd--reverse-proxy)
- [10. Деплой на VPS (Linux) через Docker](#10-деплой-на-vps-linux-через-docker)
- [11. Настройка CORS и доменов](#11-настройка-cors-и-доменов)
- [12. Хранилище файлов (local vs s3)](#12-хранилище-файлов-local-vs-s3)
- [13. WebSocket и голос/звонки (STUN/TURN)](#13-websocket-и-голосзвонки-stunturn)
- [14. Миграции БД (alembic)](#14-миграции-бд-alembic)
- [15. Troubleshooting (частые ошибки)](#15-troubleshooting-частые-ошибки)

---

## 1. Требования

### Для локальной разработки
1. **Git** (для клонирования репозитория).
2. **Python 3.11+**
3. **Node.js 18+** (рекомендую 20 LTS)
4. **PostgreSQL 14+** (или любой совместимый, если поправить `DATABASE_URL`)
5. (Опционально) **Docker** — если хотите деплоить/запускать бэкенд контейнером.

---

## 2. Структура репозитория

- `backend/` — FastAPI приложение
  - `backend/app/main.py` — точка входа FastAPI (`app`)
  - `backend/app/config.py` — настройки через переменные окружения
  - `backend/app/database.py` — подключение SQLAlchemy (async)
  - `backend/alembic.ini`, `backend/alembic/` — миграции
  - `backend/requirements.txt` — зависимости Python
  - `backend/Dockerfile` — Docker-образ для бэкенда
- `desktop/` — Vite/React приложение
  - `desktop/package.json` — зависимости и скрипты
  - `desktop/vite.config.ts` — конфигурация Vite
  - `desktop/src/` — исходники

---

## 3. Быстрый старт (локально за 10 минут)

Ниже команды для macOS/Linux (на Windows почти то же самое, но в PowerShell некоторые команды отличаются).

### 3.1. Клонирование
```bash
git clone https://github.com/YuriiFridman/Tiscord.git
cd Tiscord
```

### 3.2. Backend: создать виртуальное окружение и установить зависимости
```bash
cd backend

python3.11 -m venv .venv
# активировать:
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

### 3.3. Backend: создать `.env`
Файл **`backend/.env`** (см. раздел ниже) — минимум `DATABASE_URL` и `JWT_SECRET`.

### 3.4. Запустить backend
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3.5. Frontend: установить зависимости и запустить dev
В новом терминале:
```bash
cd desktop
npm install
npm run dev
```

---

## 4. Настройка переменных окружения (.env)

Backend читает переменные окружения из файла **`backend/.env`** (см. `backend/app/config.py`).

Создайте файл `backend/.env`:

```env
# ======================
# Database
# ======================
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/tiscord

# ======================
# JWT (ОБЯЗАТЕЛЬНО поменять в проде)
# ======================
JWT_SECRET=changeme-in-production
JWT_ACCESS_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=30

# ======================
# File storage
# ======================
# local | s3
STORAGE_BACKEND=local
STORAGE_LOCAL_PATH=./uploads

# Если STORAGE_BACKEND=s3, заполните:
STORAGE_S3_BUCKET=
STORAGE_S3_ENDPOINT=
STORAGE_S3_ACCESS_KEY=
STORAGE_S3_SECRET_KEY=
STORAGE_S3_REGION=auto

# ======================
# Voice / WebRTC
# ======================
STUN_URLS=stun:stun.l.google.com:19302
TURN_URL=
TURN_USER=
TURN_PASS=

# ======================
# Upload limits
# ======================
MAX_ATTACHMENT_SIZE=8388608

# ======================
# CORS
# ======================
# В dev можно "*", в prod лучше конкретные домены через запятую
CORS_ORIGINS=*
```

### Важно про DATABASE_URL
По умолчанию строка рассчитана на **PostgreSQL + asyncpg**.

Пример, если у вас локальный Postgres:
- пользователь: `postgres`
- пароль: `postgres`
- БД: `tiscord`

Тогда:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tiscord
```

---

## 5. Локальный запуск Backend (FastAPI)

### 5.1. Поднять PostgreSQL (варианты)

#### Вариант A: PostgreSQL установлен локально
1) Создайте БД:
```bash
createdb tiscord
```

2) Проверьте, что `DATABASE_URL` указывает на корректные `user/pass/host/port/dbname`.

#### Вариант B: PostgreSQL в Docker (удобно)
Если у вас есть Docker, можно поднять Postgres контейнером:
```bash
docker run --name tiscord-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=tiscord \
  -p 5432:5432 \
  -d postgres:16
```

И в `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tiscord
```

---

### 5.2. Миграции БД (если в проекте есть версии миграций)
В репозитории есть `backend/alembic.ini` и папка `backend/alembic/`.

Обычно порядок такой:
```bash
cd backend
source .venv/bin/activate

# применить миграции:
alembic upgrade head
```

> Если миграции не настроены/нет версий — этот шаг может быть не нужен или потребует создания миграций.

---

### 5.3. Запуск сервера разработки
Из папки `backend/`:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API будет доступно на: `http://127.0.0.1:8000`
- Health-check: `http://127.0.0.1:8000/health`
- WebSocket: `ws://127.0.0.1:8000/ws?token=...`
- Swagger (если включен по умолчанию FastAPI): `http://127.0.0.1:8000/docs`

---

## 6. Локальный запуск Desktop/Frontend (Vite)

Из папки `desktop/`:
```bash
npm install
npm run dev
```

По умолчанию Vite dev server (см. `vite.config.ts`) стартует на порту:
- `http://localhost:1420`

### 6.1. Настройка API URL во фронтенде
В репозитории есть `envPrefix: ['VITE_']`, значит фронт может использовать переменные `VITE_*`.

Если у вас во фронтенде предусмотрена переменная типа `VITE_API_URL`, создайте файл:
- `desktop/.env` или `desktop/.env.local`

Пример:
```env
VITE_API_URL=http://127.0.0.1:8000
```

> Точное имя переменной зависит от того, как она используется в `desktop/src`. Если скажешь, где хранится base URL, я допишу README под фактическую реализацию.

---

## 7. Проверка, что всё работает

### 7.1. Проверить backend
Откройте:
- `http://127.0.0.1:8000/health`  
Ожидаемый ответ:
```json
{"status":"ok"}
```

### 7.2. Проверить фронтенд
Откройте:
- `http://localhost:1420`

Если фронт делает запросы к API — откройте DevTools → Network и убедитесь, что запросы идут на ваш backend.

---

## 8. Сборка Frontend для продакшена

Из `desktop/`:
```bash
npm install
npm run build
```

Обычно Vite собирает в `desktop/dist/`.

Локально посмотрет�� прод-сборку:
```bash
npm run preview
```

---

## 9. Деплой на VPS (Linux) без Docker: systemd + reverse proxy

Ниже — рабочая схема для продакшена:
- Backend: `uvicorn` как сервис systemd (или `gunicorn` + `uvicorn.workers`)
- Nginx: reverse proxy на `localhost:8000`
- Frontend: статикой через Nginx (если это web-вариант) или отдельный домен

### 9.1. Подготовка сервера
Пример для Ubuntu:
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git
```

Поставьте PostgreSQL (локально на сервер или отдельным сервисом managed DB).

### 9.2. Пользователь и директория
```bash
sudo adduser --disabled-password --gecos "" tiscord
sudo su - tiscord

git clone https://github.com/YuriiFridman/Tiscord.git
cd Tiscord/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Создайте `backend/.env` и заполните **продовые** значения (особенно `JWT_SECRET`, `CORS_ORIGINS`, `DATABASE_URL`).

### 9.3. systemd unit для backend
Создайте файл на сервере:
`/etc/systemd/system/tiscord-backend.service`

Пример:
```ini
[Unit]
Description=Tiscord Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=tiscord
WorkingDirectory=/home/tiscord/Tiscord/backend
Environment=PYTHONPATH=/home/tiscord/Tiscord/backend
ExecStart=/home/tiscord/Tiscord/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tiscord-backend
sudo systemctl status tiscord-backend
```

Логи:
```bash
sudo journalctl -u tiscord-backend -f
```

### 9.4. Nginx reverse proxy
Создайте конфиг (пример) `/etc/nginx/sites-available/tiscord`:

```nginx
server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # WebSocket support:
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Активировать:
```bash
sudo ln -s /etc/nginx/sites-available/tiscord /etc/nginx/sites-enabled/tiscord
sudo nginx -t
sudo systemctl reload nginx
```

Теперь backend доступен по `http://api.example.com/`.

> Для HTTPS поставьте certbot (Let’s Encrypt) — если хочешь, добавлю подробный блок под твой домен и Ubuntu-версию.

---

## 10. Деплой на VPS (Linux) через Docker

В репозитории есть `backend/Dockerfile`, который запускает:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 10.1. Собрать и запустить backend-контейнер
На сервере:
```bash
git clone https://github.com/YuriiFridman/Tiscord.git
cd Tiscord/backend

# Собираем образ
docker build -t tiscord-backend:latest .

# Запускаем
docker run --name tiscord-backend \
  --env-file .env \
  -p 8000:8000 \
  -d tiscord-backend:latest
```

Проверка:
```bash
curl http://127.0.0.1:8000/health
```

### 10.2. Рекомендуемая схема (prod)
- backend контейнер без публикации наружу
- nginx на хосте публикует 80/443 и проксирует на контейнер
- PostgreSQL лучше отдельным managed DB или отдельным контейнером + volume

> В репозитории **нет** `docker-compose.yml` (на момент чтения), но если хочешь — мо��у предложить готовый `docker-compose.yml` под backend+postgres+nginx.

---

## 11. Настройка CORS и доменов

Переменная:
- `CORS_ORIGINS`

В `backend/app/main.py` она читается как строка и делится по запятым.

### Пример для продакшена
Если фронтенд на `https://app.example.com`, API на `https://api.example.com`:
```env
CORS_ORIGINS=https://app.example.com
```

Если несколько доменов:
```env
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

> Не используйте `*` в продакшене без необходимости.

---

## 12. Хранилище файлов (local vs s3)

Настройки:
- `STORAGE_BACKEND=local` или `s3`
- Для `local`: файлы лежат в `STORAGE_LOCAL_PATH` (по умолчанию `./uploads`)
- В dev режиме (когда `local`) backend монтирует:
  - `/uploads` → директория `STORAGE_LOCAL_PATH`

### В проде с local storage
Убедитесь, что:
- директория существует
- у процесса есть права записи
- эта директория **сохранится** при деплое (volume, постоянное хранилище)

### В проде с S3
Заполните:
- `STORAGE_S3_BUCKET`
- `STORAGE_S3_ENDPOINT`
- `STORAGE_S3_ACCESS_KEY`
- `STORAGE_S3_SECRET_KEY`
- `STORAGE_S3_REGION`

---

## 13. WebSocket и голос/звонки (STUN/TURN)

В `.env`:
- `STUN_URLS` — список/строка STUN серверов
- `TURN_URL`, `TURN_USER`, `TURN_PASS` — если нужен TURN (обычно нужен для стабильной связи за NAT)

Если звонки/voice “не коннектятся” в реальных сетях — почти всегда нужен TURN.

---

## 14. Миграции БД (alembic)

Основные команды (из `backend/` в активированном venv):

Применить:
```bash
alembic upgrade head
```

Откатить на 1 миграцию:
```bash
alembic downgrade -1
```

Создать новую миграцию (пример):
```bash
alembic revision -m "add users table"
```

> Если используются автогенерации, обычно делают `--autogenerate`, но корректность зависит от того, как настроены модели и `env.py` Alembic.

---

## 15. Troubleshooting (частые ошибки)

### 15.1. `ModuleNotFoundError: No module named 'app'`
Запускайте `uvicorn` **из папки `backend/`**, либо выставляйте `PYTHONPATH`:
```bash
cd backend
uvicorn app.main:app --reload
```

### 15.2. Ошибки подключения к БД
- Проверьте `DATABASE_URL` (логин/пароль/порт/имя БД)
- Проверьте, что Postgres запущен
- Если Postgres в Docker — убедитесь, что порт проброшен и доступен

### 15.3. CORS ошибки во фронтенде
- Убедитесь, что `CORS_ORIGINS` включает домен/порт фронта
- В dev можно временно `CORS_ORIGINS=*`

### 15.4. Порт занят
- Backend: поменяйте `--port`
- Frontend (Vite): по умолчанию `1420` и `strictPort: true`, если порт занят — сервер упадёт. Освободите порт или поменяйте в `vite.config.ts`.

---

## Что я могу улучшить в README дальше (уточни, и я допишу “под ключ”)
1) **Какой именно “хостинг” ты имеешь в виду**: VPS (Ubuntu), Render/Fly.io, Railway, Heroku-like, или shared hosting?
2) Фронтенд планируется как **web-сайт** (Nginx + `dist/`) или как **Tauri desktop app** (сборка `.exe/.dmg/.AppImage`)?
3) Нужен ли **HTTPS** блок (Certbot/Let’s Encrypt) и под какой домен?
4) Ты хочешь деплой **в одном домене** (`example.com` + `/api`) или **раздельно** (`app.` и `api.`)?

Скажи ответы — и я адаптирую README под твой реальный сценарий (с точными командами, конфигами Nginx и systemd, и безопасными prod-настройками).
