# AIS Clinic Course Project

Минимальный каркас проекта для АИС "Клиника".

## Структура

- `backend/` — FastAPI backend.
- `frontend/` — SPA на React + Vite, связанная с backend API.
- `infra/` — инфраструктурные файлы (`docker-compose.yml`, SQL-инициализация БД).
- `Documentation/` — рабочая документация и проектные решения.
- `uml/` — UML/C4/ER диаграммы.

## Быстрый запуск

1. Перейдите в папку инфраструктуры:
   - `cd infra`
2. Поднимите сервисы:
   - `docker compose up --build`
3. Проверка backend:
   - API: `http://localhost:8000`
   - Health: `http://localhost:8000/health`
   - Swagger UI: `http://localhost:8000/docs`
4. Проверка frontend:
   - UI: `http://localhost:5173`

## Авторизация в Swagger UI

1. Откройте `http://localhost:8000/docs`.
2. Нажмите `Authorize`.
3. Введите:
   - `username`: `admin`
   - `password`: `admin12345`
4. Поля `client_id` и `client_secret` оставьте пустыми.

Логин-эндпоинт работает в формате `application/x-www-form-urlencoded`, поэтому окно `Authorize` в Swagger должно работать без ручного копирования токена.

Эти же учетные данные подходят для frontend (`http://localhost:5173`).

## Что инициализируется в БД

При первом запуске PostgreSQL автоматически выполняется:
- `infra/db/init/001_init.sql`

Скрипт создает:
- схему `clinic`;
- enum-типы статусов и ролей;
- основные таблицы из ER-модели;
- внешние ключи и базовые индексы;
- демо-пользователя `admin` (только при **первом** создании тома БД).

## Почему не логинится `admin` после перезапуска

В логах PostgreSQL может появиться строка:

`PostgreSQL Database directory appears to contain a database; Skipping initialization`

Это значит, что **том с данными уже существует**, и скрипты из `docker-entrypoint-initdb.d` **не выполняются повторно**. Если том был создан до появления seed-а `admin` в `001_init.sql`, пользователя в таблице просто нет — `POST /api/v1/auth/login` вернёт `401`.

### Вариант A — пересоздать БД с нуля (удалит все данные в volume)

```powershell
cd D:\GorohProd\Course\infra
docker compose down -v
docker compose up -d --build
```

### Вариант B — не удаляя данные, создать/обновить `admin` вручную

Из каталога `infra` (контейнеры должны быть запущены):

**Windows (PowerShell):**

```powershell
cd D:\GorohProd\Course\infra
.\scripts\seed_admin.ps1
```

**Linux / macOS:**

```sh
cd infra
sh scripts/seed_admin.sh
```

Учётные данные после скрипта:

- **username:** `admin`
- **password:** `admin12345`

Проверка входа: Swagger [http://localhost:8000/docs](http://localhost:8000/docs) → `POST /api/v1/auth/login`.

## Миграции БД для существующего volume

Если том PostgreSQL был создан **до** появления файлов в `infra/db/init`, при повторном запуске они не применятся автоматически. Тогда выполните вручную (DBeaver или `psql`):

```sql
ALTER TABLE clinic.patients ADD COLUMN IF NOT EXISTS email varchar(255);
CREATE TABLE IF NOT EXISTS clinic.schedule_exceptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id uuid NOT NULL REFERENCES clinic.doctors(id) ON DELETE CASCADE,
    date_from date NOT NULL,
    date_to date NOT NULL,
    reason varchar(255) NOT NULL,
    CHECK (date_to >= date_from)
);
CREATE TABLE IF NOT EXISTS clinic.referrals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id uuid NOT NULL REFERENCES clinic.visits(id) ON DELETE CASCADE,
    target_specialty_id int NOT NULL REFERENCES clinic.specialties(id) ON DELETE RESTRICT,
    target_doctor_id uuid REFERENCES clinic.doctors(id) ON DELETE SET NULL,
    reason text NOT NULL,
    status varchar(20) NOT NULL DEFAULT 'created',
    comment text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (status IN ('created', 'accepted', 'rejected', 'completed'))
);
```

Либо пересоздайте том: `docker compose down -v` и снова `up -d --build`.

## Актуальность документации

Документация ведется синхронно с разработкой:
- при изменении API обновляются `Documentation/openapi.yaml` и `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`;
- каждое значимое изменение фиксируется в `Documentation/WORKLOG.md`.

## Frontend ↔ Backend интеграция

- Frontend использует `VITE_API_BASE_URL` (по умолчанию: `http://localhost:8000/api/v1`).
- Backend включает CORS для `http://localhost:5173` и `http://127.0.0.1:5173`.
- Для dev-запуска frontend с другого устройства в LAN (например, MacBook по `http://192.168.x.x:5173`) включен `CORS_ALLOW_ORIGIN_REGEX` в `infra/docker-compose.yml`.
- Для диагностики ошибок backend возвращает заголовок/поле `X-Request-ID` / `request_id`; frontend пишет детальный лог в консоль (`[httpRequest] request failed`) с методом, URL, статусом и деталями ответа.
- Backend пишет структурированные JSON-логи в `/app/logs/app.log` (в контейнере `clinic-backend`); при сбое ищите запись по `request_id`, там есть метод, путь, query, статус, duration и traceback.
- Frontend реализован по слоистой структуре `app/pages/widgets/features/entities/shared`.
- В UI добавлены плавные переходы, toast-уведомления и сохранение настроек таблиц в `localStorage`.
- Добавлен кадровый контур врачей: создание врача, список врачей, просмотр и управление их записями (перенос/отмена).
- Добавлен контур назначения диагнозов: `admin`/`doctor` через страницу `Diagnoses` с ролевыми ограничениями.
- Для демо-проверки добавлено нормализованное наполнение БД (`ФИО`, специализации, визиты, диагнозы, оклады/премии).
- Для ручной проверки:
  1. Откройте `http://localhost:5173`;
  2. Войдите `admin/admin12345`;
  3. Перейдите на `/appointments`: выберите врача, затем загрузите доступные слоты через `GET /api/v1/schedule-slots`;
  4. Создайте запись без ручного ввода UUID слота;
  5. Для роли `admin/registrar` доступны `patients`, `appointments`, `doctors` маршруты;
  6. Для ролей `admin/doctor` доступен маршрут `/visits` (назначение диагнозов);
  7. Для ролей `admin/registrar/doctor` доступен маршрут `reports` и `reports/diagnoses`;
  8. Измените сортировку/колонки на `patients` и обновите страницу — настройки должны сохраниться;
  9. На `/doctors` проверьте колонки ФИО/специализации, добавьте врача и выполните операции с записями;
  10. На `/visits` назначьте диагноз:
     - под `admin` — любому визиту;
     - под `doctor` — только своим завершенным приемам;
  11. Проверьте toast-уведомления на успешных/ошибочных действиях.

## Демо-наполнение БД

После запуска инфраструктуры:

```powershell
cd D:\GorohProd\Course\infra
.\scripts\seed_data.ps1
```

Скрипт заполнит БД реалистичными данными:
- ФИО пациентов и врачей;
- справочник специализаций (`Терапевт`, `Педиатр`, `Хирург`, `ЛОР` и др.);
- записи на прием, визиты и пример назначенного диагноза;
- оклад и премию врачей для кадровых сценариев администратора.

## Интеграционные тесты backend

Тесты запускаются внутри контейнера backend и используют реальный API + PostgreSQL:

```powershell
cd D:\GorohProd\Course\infra
docker compose up -d --build
docker compose exec -T backend pytest -q
```

По умолчанию используется:
- `API_BASE_URL=http://localhost:8000` (внутри контейнера);
- `TEST_DB_DSN=postgresql://clinic_user:clinic_pass@db:5432/clinic`.

При необходимости параметры можно переопределить переменными окружения.

Текущее состояние тестового контура:
- реализованы 6 интеграционных файлов (`e2e` + негативные + валидационные + граничные периоды + RBAC-матрица отчетов + фильтры/пагинация);
- проверяются `happy-path`, ошибки доступа/конфликтов (`403`, `409`), валидация (`422`), периодные границы дат, роли `admin/registrar/doctor` в `reports`, а также `skip/limit/status/q` фильтры списков;
- при последнем прогоне внутри контейнера: `10 passed`.
