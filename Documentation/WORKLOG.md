# Журнал работ (что сделано и зачем)

Формат записи:
- **Дата**
- **Шаг**
- **Что сделано**
- **Зачем**
- **Артефакты**
- **Результат**

---

## 2026-04-15 — Шаг 1: Базовое техническое задание

- **Что сделано:** создан файл технического задания по АИС "Клиника".
- **Зачем:** зафиксировать рамки проекта, требования, функции, критерии приемки и стек.
- **Артефакты:** `TECHNICAL_SPECIFICATION.md`.
- **Результат:** сформирована единая база требований для дальнейшего проектирования и разработки.

## 2026-04-15 — Шаг 2: C4-диаграммы архитектуры

- **Что сделано:** созданы C4-диаграммы контекста, контейнеров и компонентов backend.
- **Зачем:** визуализировать архитектуру для пояснительной записки и защиты курсового.
- **Артефакты:** `uml/c4-context.puml`, `uml/c4-container.puml`, `uml/c4-component-backend.puml`.
- **Результат:** подготовлен архитектурный комплект диаграмм C4.

## 2026-04-15 — Шаг 3: Переработка диаграмм под слоистую архитектуру

- **Что сделано:** устранены проблемы рендера (`!include` по URL), диаграммы переведены на локально-совместимый PlantUML; компонентная диаграмма переработана под слои `Presentation -> Application -> Domain -> Infrastructure`.
- **Зачем:** обеспечить корректное открытие диаграмм и убрать лишние компоненты, сфокусироваться на архитектурных слоях и GoF-паттернах.
- **Артефакты:** `uml/c4-context.puml`, `uml/c4-container.puml`, `uml/c4-component-backend.puml`.
- **Результат:** диаграммы открываются стабильнее, архитектура стала компактнее и логичнее для защиты.

## 2026-04-15 — Шаг 4: Создание контура проектной документации

- **Что сделано:** создана папка `Documentation` и базовые документы по структуре и журналированию работ.
- **Зачем:** фиксировать каждый шаг разработки с обоснованием "что и зачем", чтобы не терять ход проекта.
- **Артефакты:** `Documentation/README.md`, `Documentation/PROJECT_STRUCTURE.md`, `Documentation/WORKLOG.md`.
- **Результат:** сформирован процессный каркас документации для всего проекта.

## 2026-04-15 — Шаг 5: ER-модель, API-взаимодействия и OpenAPI-контракты

- **Что сделано:** спроектирована ER-диаграмма с типами данных и связями; подготовлено описание взаимодействия фронтенда/внешних систем с backend по слоям C4 Level 3; составлены эндпоинты и JSON-контракты с валидацией; добавлен черновой OpenAPI-файл.
- **Зачем:** зафиксировать целевую модель данных и API-контракты до начала реализации backend, снизить риск ошибок в медицинских данных и назначениях.
- **Артефакты:** `uml/er-clinic.puml`, `Documentation/ER_MODEL.md`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/openapi.yaml`.
- **Результат:** определены сущности, связи, ключевые ограничения и интерфейс API для дальнейшей реализации и Swagger-документации.

---

## Следующий шаг (рекомендуется)

**Шаг 6: Каркас backend и frontend по целевой структуре.**

План:
1. Создать директории `backend/`, `frontend/`, `infra/`.
2. Подготовить минимальные файлы запуска (`main.py`, `docker-compose.yml`, базовый `README.md`).
3. Зафиксировать результат в этом журнале отдельной записью.

## 2026-04-15 — Шаг 6: Каркас запуска и первичная инициализация БД

- **Что сделано:** созданы директории `backend/`, `frontend/`, `infra/`; добавлен минимальный FastAPI backend (`main.py`), Dockerfile и зависимости; добавлен `infra/docker-compose.yml`; подготовлен SQL-скрипт первичной инициализации PostgreSQL с таблицами и ограничениями по ER-модели; создан базовый `README.md`.
- **Зачем:** получить рабочую стартовую точку, которую можно запустить одной командой и сразу иметь развернутую БД для дальнейшей разработки API.
- **Артефакты:** `backend/main.py`, `backend/requirements.txt`, `backend/Dockerfile`, `infra/docker-compose.yml`, `infra/db/init/001_init.sql`, `README.md`, `frontend/README.md`.
- **Результат:** проект готов к первому инфраструктурному запуску через Docker Compose, БД инициализируется автоматически при первом старте контейнера PostgreSQL.

## 2026-04-15 — Шаг 7: Формирование слоистого файлового каркаса

- **Что сделано:** создана целевая структура backend по слоям (`api`, `services`, `domain`, `infrastructure`) с базовыми файлами и роутерами v1; добавлены базовые файлы frontend (`package.json`, `Dockerfile`, `src/main.tsx`) и инфраструктурные шаблоны (`.env.example`, `backup_db.sh`, `seed_data.py`).
- **Зачем:** привести репозиторий к архитектурному каркасу из документации и подготовить основу для поэтапной реализации модулей.
- **Артефакты:** `backend/app/*`, `backend/tests/conftest.py`, `frontend/package.json`, `frontend/Dockerfile`, `frontend/src/main.tsx`, `infra/.env.example`, `infra/scripts/backup_db.sh`, `infra/scripts/seed_data.py`.
- **Результат:** структура проекта соответствует выбранной слоистой архитектуре и готова к реализации бизнес-логики и API-контрактов.

## 2026-04-15 — Шаг 8: Первый вертикальный срез Auth (JWT)

- **Что сделано:** реализован базовый вертикальный срез аутентификации: Pydantic-схемы входа/токена, SQLAlchemy-модель пользователя, репозиторий пользователя, сервис логина, роут `POST /api/v1/auth/login`, утилиты безопасности (bcrypt + JWT), обновлены настройки и зависимости.
- **Зачем:** заложить рабочий шаблон `router -> service -> repository -> db` для последующей реализации остальных доменных модулей по аналогии.
- **Артефакты:** `backend/app/schemas/auth.py`, `backend/app/infrastructure/db/models/user.py`, `backend/app/infrastructure/repositories/user_repository.py`, `backend/app/services/auth_service.py`, `backend/app/api/v1/auth.py`, `backend/app/core/security.py`, `backend/app/core/settings.py`, `backend/requirements.txt`, `infra/.env.example`.
- **Результат:** endpoint логина подключен, при валидных учетных данных возвращается JWT access token, обработаны базовые сценарии ошибок (401/403).

## 2026-04-15 — Шаг 9: Расширение Auth (current user + RBAC dependency)

- **Что сделано:** добавлен endpoint `GET /api/v1/auth/me`, реализовано декодирование JWT и получение текущего пользователя, добавлен dependency `require_roles(...)` для ролевой защиты эндпоинтов; обновлен OpenAPI и API-документация; в SQL-инициализацию добавлен демо-пользователь `admin`.
- **Зачем:** завершить минимально пригодный auth-контур для разработки защищенных бизнес-эндпоинтов и ускорить локальное тестирование без ручного наполнения users.
- **Артефакты:** `backend/app/api/deps.py`, `backend/app/api/v1/auth.py`, `backend/app/core/security.py`, `backend/app/services/auth_service.py`, `backend/app/infrastructure/repositories/user_repository.py`, `backend/app/schemas/auth.py`, `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `infra/db/init/001_init.sql`.
- **Результат:** backend умеет аутентифицировать пользователя и возвращать текущий профиль по Bearer JWT, база содержит стартовую учетную запись для проверки входа.

## 2026-04-15 — Шаг 10: Устранение проблемы логина admin при существующем volume БД

- **Что сделано:** добавлен идемпотентный SQL `infra/db/seed_admin.sql` и скрипты `infra/scripts/seed_admin.ps1` / `seed_admin.sh`; в `README.md` описаны причина `Skipping initialization` и два способа исправления (`down -v` или seed без удаления данных).
- **Зачем:** при повторном `docker compose up` без пересоздания тома init-скрипты не выполняются, из-за чего пользователь `admin` мог отсутствовать и логин возвращал 401.
- **Артефакты:** `infra/db/seed_admin.sql`, `infra/scripts/seed_admin.ps1`, `infra/scripts/seed_admin.sh`, `README.md`.
- **Результат:** можно в любой момент создать или сбросить пароль демо-админа без пересоздания всей БД.

## 2026-04-15 — Шаг 11: Совместимость bcrypt с passlib в Docker

- **Что сделано:** убрана зависимость `passlib` для проверки пароля; используется пакет `bcrypt` напрямую в `verify_password` / `get_password_hash`, обновлён `requirements.txt` и упоминание в ТЗ.
- **Зачем:** в контейнере подтягивался `bcrypt` 4.1+, с которым `passlib` падает (`AttributeError: module 'bcrypt' has no attribute '__about__'`), из-за чего логин завершался 500.
- **Артефакты:** `backend/app/core/security.py`, `backend/requirements.txt`, `TECHNICAL_SPECIFICATION.md`.
- **Результат:** проверка хэшей из PostgreSQL `crypt(..., gen_salt('bf'))` и генерация новых хэшей в Python работают на актуальных версиях `bcrypt`.

## 2026-04-15 — Шаг 12: Модуль Patients (CRUD + RBAC)

- **Что сделано:** добавлены SQLAlchemy-модель `Patient`, репозиторий, сервис, Pydantic-схемы; реализованы эндпоинты `POST/GET/PATCH/DELETE` для `/api/v1/patients` с разграничением ролей; добавлен init-скрипт `002_patients_email.sql`; обновлены OpenAPI и README.
- **Зачем:** закрыть функции Ф-01–Ф-05 по подсистеме пациентов и задать шаблон для остальных доменных модулей.
- **Артефакты:** `backend/app/infrastructure/db/models/patient.py`, `backend/app/infrastructure/repositories/patient_repository.py`, `backend/app/services/patient_service.py`, `backend/app/schemas/patients.py`, `backend/app/api/v1/patients.py`, `backend/app/api/deps.py`, `backend/requirements.txt`, `infra/db/init/002_patients_email.sql`, `Documentation/openapi.yaml`, `README.md`.
- **Результат:** регистрация и поиск пациентов, просмотр, обновление и мягкая деактивация доступны через API с JWT и RBAC.

## 2026-04-15 — Шаг 13: Модуль Schedules (расписания, слоты, исключения)

- **Что сделано:** реализованы SQLAlchemy-модели `Schedule`, `ScheduleSlot`, `ScheduleException`; добавлен репозиторий и сервис расписаний; реализованы API-эндпоинты `POST/GET /api/v1/schedules`, `POST /api/v1/schedule-slots/generate`, `POST /api/v1/schedule-exceptions` с RBAC; обновлена спецификация OpenAPI.
- **Зачем:** закрыть функции подсистемы управления расписанием (Ф-06, Ф-07, Ф-08) и подготовить основу для корректной записи пациентов на прием.
- **Артефакты:** `backend/app/infrastructure/db/models/schedule.py`, `backend/app/infrastructure/repositories/schedule_repository.py`, `backend/app/services/schedule_service.py`, `backend/app/schemas/schedules.py`, `backend/app/api/v1/schedules.py`, `backend/app/api/v1/schedule_slots.py`, `backend/app/api/v1/schedule_exceptions.py`, `backend/app/api/router.py`, `backend/app/api/deps.py`, `Documentation/openapi.yaml`, `infra/db/init/003_schedule_exceptions.sql`, `README.md`.
- **Результат:** backend поддерживает создание/просмотр расписаний, генерацию временных слотов и фиксацию нерабочих периодов врача.

## 2026-04-15 — Шаг 14: Модуль Appointments (запись, отмена, перенос)

- **Что сделано:** реализованы SQLAlchemy-модель `Appointment`, репозиторий, сервис и API-эндпоинты `POST/GET /api/v1/appointments`, `PATCH /api/v1/appointments/{appointment_id}/cancel`, `PATCH /api/v1/appointments/{appointment_id}/reschedule`; добавлены схемы Pydantic и обновлён OpenAPI.
- **Зачем:** закрыть функции Ф-09 и Ф-10 (запись и изменение записи) с проверкой занятости слота и согласованным обновлением статусов (`slot` и `appointment`).
- **Артефакты:** `backend/app/infrastructure/db/models/appointment.py`, `backend/app/infrastructure/repositories/appointment_repository.py`, `backend/app/services/appointment_service.py`, `backend/app/schemas/appointments.py`, `backend/app/api/v1/appointments.py`, `backend/app/api/deps.py`, `Documentation/openapi.yaml`, `backend/app/infrastructure/db/models/__init__.py`.
- **Результат:** в API доступны запись пациента в слот, фильтруемый список записей, отмена и перенос на другой свободный слот с ролевой защитой.

## 2026-04-15 — Шаг 15: Исправление авторизации Swagger (422 -> корректный OAuth2 form)

- **Что сделано:** endpoint `POST /api/v1/auth/login` переведен на `OAuth2PasswordRequestForm`; в сервисе auth выделен метод `login_by_credentials`; добавлена зависимость `python-multipart` для обработки form-data.
- **Зачем:** окно `Authorize` в Swagger отправляет `application/x-www-form-urlencoded`, а endpoint ожидал JSON, что вызывало `422 Unprocessable Entity`.
- **Артефакты:** `backend/app/api/v1/auth.py`, `backend/app/services/auth_service.py`, `backend/requirements.txt`.
- **Результат:** авторизация через Swagger UI работает штатно по `username/password`, backend выдает JWT без ручных обходов.

## 2026-04-15 — Шаг 16: Реализация модуля Visits (базовый клинический контур)

- **Что сделано:** добавлены модель `Visit`, репозиторий, схемы, сервис и API-эндпоинты `POST /api/v1/visits`, `GET /api/v1/visits`, `GET /api/v1/visits/{visit_id}`, `PATCH /api/v1/visits/{visit_id}/complete`; подключена dependency `get_visit_service`.
- **Зачем:** закрыть основной сценарий приема пациента: создание визита по записи и его завершение с синхронизацией статуса записи.
- **Артефакты:** `backend/app/infrastructure/db/models/visit.py`, `backend/app/infrastructure/db/models/__init__.py`, `backend/app/infrastructure/repositories/visit_repository.py`, `backend/app/schemas/visits.py`, `backend/app/services/visit_service.py`, `backend/app/api/v1/visits.py`, `backend/app/api/deps.py`.
- **Результат:** в backend появился рабочий контур визитов с проверками консистентности (`appointment exists`, уникальность визита на запись, допустимые статусы завершения).

## 2026-04-15 — Шаг 17: Детализация и синхронизация документации с фактической реализацией

- **Что сделано:** обновлены правила ведения документации, уточнен README по Swagger-авторизации, каталог API приведен к фактическому состоянию (`implemented/partial/planned`) и дополнен актуальными контрактами для `auth` и `visits`.
- **Зачем:** исключить рассинхрон между кодом и документацией, упростить ручное тестирование и повысить прозрачность статуса разработки.
- **Артефакты:** `Documentation/README.md`, `README.md`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/WORKLOG.md`.
- **Результат:** документация стала более подробной, ориентированной на проверку и поддержку дальнейшей разработки.

## 2026-04-15 — Шаг 18: Реализация diagnoses для визитов

- **Что сделано:** добавлены ORM-модель `Diagnosis`, расширен репозиторий визитов (проверка наличия МКБ-10, проверка первичного диагноза, сохранение набора диагнозов), добавлены DTO-схемы для диагнозов, реализован сервисный метод и endpoint `POST /api/v1/visits/{visit_id}/diagnoses`.
- **Зачем:** закрыть следующий обязательный клинический сценарий после создания визита — постановка диагноза с ограничением на единственный первичный диагноз.
- **Артефакты:** `backend/app/infrastructure/db/models/diagnosis.py`, `backend/app/infrastructure/db/models/__init__.py`, `backend/app/infrastructure/repositories/visit_repository.py`, `backend/app/schemas/visits.py`, `backend/app/services/visit_service.py`, `backend/app/api/v1/visits.py`.
- **Результат:** API поддерживает массовое добавление диагнозов к визиту с валидацией МКБ-10 и бизнес-ограничениями (`in_progress`, уникальный primary).

## 2026-04-15 — Шаг 19: Синхронизация документации после внедрения diagnoses

- **Что сделано:** обновлены OpenAPI и контрактная документация по разделу `Visits`, статус endpoint `POST /api/v1/visits/{visit_id}/diagnoses` изменен на `implemented`, добавлены примеры запроса/ответа и бизнес-правила.
- **Зачем:** поддерживать документацию в актуальном состоянии одновременно с кодом.
- **Артефакты:** `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/WORKLOG.md`.
- **Результат:** Swagger и текстовые контракты отражают фактическую реализацию diagnoses.

## 2026-04-15 — Шаг 20: Реализация prescriptions для визитов

- **Что сделано:** добавлена ORM-модель `Prescription`, расширен репозиторий визитов (проверка наличия медикамента, массовое сохранение назначений), добавлены DTO для назначений, реализован сервисный сценарий и endpoint `POST /api/v1/visits/{visit_id}/prescriptions`.
- **Зачем:** закрыть следующий обязательный клинический сценарий после постановки диагноза — назначение терапии с базовой валидацией дозировки и длительности.
- **Артефакты:** `backend/app/infrastructure/db/models/prescription.py`, `backend/app/infrastructure/db/models/__init__.py`, `backend/app/infrastructure/repositories/visit_repository.py`, `backend/app/schemas/visits.py`, `backend/app/services/visit_service.py`, `backend/app/api/v1/visits.py`.
- **Результат:** API поддерживает пакетное добавление назначений к визиту с проверками (`visit_status`, `medication exists`, формат дозировки, диапазон дней лечения).

## 2026-04-15 — Шаг 21: Синхронизация документации после внедрения prescriptions

- **Что сделано:** обновлены OpenAPI и контрактная документация по разделу `Visits`, статус endpoint `POST /api/v1/visits/{visit_id}/prescriptions` изменен на `implemented`, добавлены примеры и бизнес-ограничения.
- **Зачем:** сохранять правило синхронного обновления документации в каждый функциональный шаг.
- **Артефакты:** `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/WORKLOG.md`.
- **Результат:** документация соответствует текущему состоянию backend по визитам/диагнозам/назначениям.

## 2026-04-15 — Шаг 22: Реализация базового контура лаборатории (orders/items/results)

- **Что сделано:** реализованы ORM-модели лабораторного контура (`LabOrder`, `LabOrderItem`, `LabResult`, `LabTestType`), создан репозиторий лаборатории, добавлены DTO-схемы и сервис `LabService`, реализованы API-эндпоинты `POST /api/v1/labs/orders`, `POST /api/v1/labs/orders/{order_id}/items`, `POST /api/v1/labs/results`, `GET /api/v1/labs/results`.
- **Зачем:** заменить заглушку `labs` рабочим минимумом по ТЗ для оформления направлений, внесения результатов и просмотра истории.
- **Артефакты:** `backend/app/infrastructure/db/models/lab.py`, `backend/app/infrastructure/db/models/__init__.py`, `backend/app/infrastructure/repositories/lab_repository.py`, `backend/app/schemas/labs.py`, `backend/app/services/lab_service.py`, `backend/app/api/v1/labs.py`, `backend/app/api/deps.py`.
- **Результат:** лабораторный модуль переведен из `partial` в рабочее состояние с базовыми проверками целостности (`visit exists`, `test type exists`, `single result per order item`).

## 2026-04-15 — Шаг 23: Синхронизация документации после внедрения лабораторного контура

- **Что сделано:** обновлены OpenAPI-пути и схемы по `labs`, обновлен каталог эндпоинтов и JSON-контракты с примерами запросов/ответов.
- **Зачем:** сохранить полную синхронизацию документации и фактической реализации backend.
- **Артефакты:** `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/WORKLOG.md`.
- **Результат:** документация отражает текущий реальный API лаборатории.

## 2026-04-15 — Шаг 24: Реализация referrals для визитов

- **Что сделано:** добавлены SQL-скрипт `004_referrals.sql`, ORM-модель `Referral`, расширен репозиторий визитов (валидации `specialty/doctor` и массовое сохранение), добавлены DTO и сервисный сценарий `add_referrals`, реализован endpoint `POST /api/v1/visits/{visit_id}/referrals`.
- **Зачем:** закрыть клинический модуль `Visits` по ТЗ направлением к специалисту как отдельным доменным объектом.
- **Артефакты:** `infra/db/init/004_referrals.sql`, `backend/app/infrastructure/db/models/referral.py`, `backend/app/infrastructure/db/models/__init__.py`, `backend/app/infrastructure/repositories/visit_repository.py`, `backend/app/schemas/visits.py`, `backend/app/services/visit_service.py`, `backend/app/api/v1/visits.py`.
- **Результат:** API поддерживает создание направлений в рамках визита с базовыми ограничениями целостности (`visit in_progress`, `specialty exists`, `doctor exists`).

## 2026-04-15 — Шаг 25: Синхронизация документации после внедрения referrals

- **Что сделано:** обновлены OpenAPI-пути/схемы для `referrals`, обновлен каталог API и JSON-контракты, отражено текущее состояние модулей и дополнен блок миграций для существующих volume.
- **Зачем:** сохранять единый источник истины между кодом, Swagger и текстовой документацией.
- **Артефакты:** `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/PROJECT_STRUCTURE.md`, `Documentation/WORKLOG.md`, `README.md`.
- **Результат:** `referrals` переведен в `implemented` как в коде, так и в документации.

## 2026-04-15 — Шаг 26: Реализация модуля reports (реальные агрегирующие отчеты)

- **Что сделано:** создан репозиторий отчетов с SQL-агрегациями, добавлены DTO-схемы и сервис `ReportService`, реализованы API-эндпоинты `GET /api/v1/reports/doctor-workload`, `GET /api/v1/reports/diagnoses`, `GET /api/v1/reports/appointments`, `GET /api/v1/reports/finance`; подключен DI-провайдер `get_report_service`.
- **Зачем:** заменить заглушку отчетности на рабочий аналитический контур по ТЗ и дать backend готовые метрики для дашбордов.
- **Артефакты:** `backend/app/infrastructure/repositories/report_repository.py`, `backend/app/schemas/reports.py`, `backend/app/services/report_service.py`, `backend/app/api/v1/reports.py`, `backend/app/api/deps.py`.
- **Результат:** модуль `reports` отдает реальные сводки по периоду для загрузки врачей, диагнозов, статусов записей и финансов.

## 2026-04-15 — Шаг 27: Синхронизация документации после внедрения reports

- **Что сделано:** обновлены OpenAPI-пути и схемы для отчетов, обновлены статус-каталог и JSON-контракты в документации, модуль `reports` переведен в реализованные в структуре проекта.
- **Зачем:** поддерживать документацию в строгом соответствии с фактической реализацией backend.
- **Артефакты:** `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/PROJECT_STRUCTURE.md`, `Documentation/WORKLOG.md`.
- **Результат:** отчеты отображаются как `implemented` и описаны в Swagger/контрактах с параметрами и примерами ответов.

## 2026-04-15 — Шаг 28: Добавление интеграционного e2e-теста ключевого сценария

- **Что сделано:** добавлен тестовый каркас на `pytest` с подготовкой тестовых данных напрямую в БД (`doctor/patient/schedule/slot/icd10/medication/lab_test_type`), реализован e2e-интеграционный тест полного backend-сценария: `auth -> appointment -> visit -> diagnoses -> prescriptions -> referrals -> labs -> reports`.
- **Зачем:** зафиксировать рабочую связность модулей и иметь проверку основных бизнес-потоков после изменений.
- **Артефакты:** `backend/tests/conftest.py`, `backend/tests/test_integration_api_flow.py`, `backend/requirements.txt`.
- **Результат:** автоматический интеграционный тест выполняется внутри контейнера backend и подтверждает корректность сквозного сценария.

## 2026-04-15 — Шаг 29: Устранение ошибки SQLAlchemy metadata в интеграционном сценарии

- **Что сделано:** добавлены минимальные ORM-модели справочных таблиц (`Doctor`, `Specialty`, `Medication`, `ICD10Code`) и подключены в metadata; исправлена генерация тестового ICD-10 кода по шаблону в фикстурах.
- **Зачем:** устранить падение `NoReferencedTableError` при `flush()` для сущностей с внешними ключами и стабилизировать интеграционные тесты.
- **Артефакты:** `backend/app/infrastructure/db/models/reference.py`, `backend/app/infrastructure/db/models/__init__.py`, `backend/tests/conftest.py`.
- **Результат:** e2e-тест проходит (`1 passed`), а связность FK-таблиц в ORM-контуре подтверждена.

## 2026-04-15 — Шаг 30: Синхронизация документации по тестированию

- **Что сделано:** в корневой `README.md` добавлен раздел запуска интеграционных тестов backend через Docker Compose.
- **Зачем:** сделать воспроизводимую инструкцию проверки качества backend для разработки и демонстрации.
- **Артефакты:** `README.md`, `Documentation/WORKLOG.md`.
- **Результат:** тестовый контур документирован и готов к повторному запуску.

## 2026-04-15 — Шаг 31: Негативные интеграционные сценарии (RBAC и конфликты)

- **Что сделано:** добавлен второй интеграционный тестовый файл с негативными кейсами: `doctor -> POST /patients` возвращает `403`, повторный `POST /labs/results` для того же `lab_order_item_id` возвращает `409`; расширены тестовые фикстуры (дополнительный слот и учётные данные тестового врача).
- **Зачем:** покрыть критичные риски регрессий по безопасности доступа и конфликтам данных.
- **Артефакты:** `backend/tests/test_integration_negative_cases.py`, `backend/tests/conftest.py`.
- **Результат:** полный интеграционный набор (`happy-path + negative`) проходит: `3 passed`.

## 2026-04-15 — Шаг 32: Актуализация документации по покрытию тестов

- **Что сделано:** обновлены README и контрактная документация: добавлено текущее состояние интеграционных тестов и перечень проверяемых сценариев.
- **Зачем:** зафиксировать тестовое покрытие как часть готовности backend и упростить проверку проекта при демонстрации.
- **Артефакты:** `README.md`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/WORKLOG.md`.
- **Результат:** документация отражает не только API-контракты, но и фактическое интеграционное покрытие.

## 2026-04-15 — Шаг 33: Интеграционные валидационные сценарии (`422`)

- **Что сделано:** добавлен третий интеграционный файл `backend/tests/test_integration_validation_cases.py` с проверками ошибок валидации запросов.
- **Зачем:** закрыть класс регрессий по `422 Unprocessable Entity` на ключевых эндпоинтах, где строгая валидация особенно важна.
- **Артефакты:** `backend/tests/test_integration_validation_cases.py`.
- **Результат:** покрыты сценарии `invalid icd10`, `invalid dosage`, `invalid referral specialty`, `invalid lab result payload`, `invalid report limit`.

## 2026-04-15 — Шаг 34: Усиление тестовых фикстур для независимости сценариев

- **Что сделано:** в `seeded_entities` добавлен отдельный слот `slot_id_validation` для валидационных тестов.
- **Зачем:** исключить пересечения по слотам между разными интеграционными файлами и сделать прогоны стабильнее.
- **Артефакты:** `backend/tests/conftest.py`.
- **Результат:** сценарии `happy-path`, negative и validation не конфликтуют между собой по тестовым данным.

## 2026-04-15 — Шаг 35: Проверка полного интеграционного набора после расширения

- **Что сделано:** выполнен полный прогон `pytest -q` внутри контейнера backend после добавления валидационного файла.
- **Зачем:** подтвердить, что новое покрытие не ломает уже реализованные сценарии.
- **Артефакты:** `backend/tests/test_integration_api_flow.py`, `backend/tests/test_integration_negative_cases.py`, `backend/tests/test_integration_validation_cases.py`.
- **Результат:** весь набор проходит успешно — `4 passed`.

## 2026-04-15 — Шаг 36: Интеграционные тесты граничных периодов дат

- **Что сделано:** добавлен новый файл `backend/tests/test_integration_period_boundaries.py` с тремя сценариями: валидный однодневный период для генерации слотов, невалидные диапазоны дат (`date_to < date_from`) для расписаний и однодневные периоды для отчетов.
- **Зачем:** покрыть класс регрессий на границах диапазонов дат в расписаниях и аналитике.
- **Артефакты:** `backend/tests/test_integration_period_boundaries.py`.
- **Результат:** подтверждена корректная обработка `date_from=date_to` и валидационные ошибки `422` для обратных диапазонов.

## 2026-04-15 — Шаг 37: Перепроверка полного набора после добавления period-boundary тестов

- **Что сделано:** выполнен прогон `docker compose up -d --build backend` и затем `docker compose exec -T backend pytest -q`.
- **Зачем:** убедиться, что новый тестовый файл включен в контейнерный образ и не ломает существующие сценарии.
- **Артефакты:** `backend/tests/test_integration_api_flow.py`, `backend/tests/test_integration_negative_cases.py`, `backend/tests/test_integration_validation_cases.py`, `backend/tests/test_integration_period_boundaries.py`.
- **Результат:** полный интеграционный набор проходит успешно — `7 passed`.

## 2026-04-15 — Шаг 38: Синхронная актуализация документации по тестовому покрытию

- **Что сделано:** обновлены разделы про интеграционные тесты в `README.md` и `Documentation/API_ENDPOINTS_AND_CONTRACTS.md` с добавлением period-boundary покрытия.
- **Зачем:** сохранить документацию в полном соответствии с фактическим состоянием backend и тестового контура.
- **Артефакты:** `README.md`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/WORKLOG.md`.
- **Результат:** документация отражает 4 интеграционных файла и актуальный результат прогона.

## 2026-04-15 — Шаг 39: Интеграционная RBAC-матрица для отчетов

- **Что сделано:** добавлен файл `backend/tests/test_integration_rbac_reports_matrix.py` с проверкой матрицы доступов `admin/registrar/doctor` для всех endpoint модуля `reports`.
- **Зачем:** закрыть риск регрессий в разграничении ролей не только по негативным кейсам, но и по разрешенным сценариям доступа.
- **Артефакты:** `backend/tests/test_integration_rbac_reports_matrix.py`.
- **Результат:** подтверждены ожидаемые права: `admin` — все отчеты, `registrar` — все кроме `finance`, `doctor` — только `diagnoses`.

## 2026-04-15 — Шаг 40: Расширение тестового seed под роль registrar

- **Что сделано:** в `seeded_entities` добавлен отдельный пользователь с ролью `registrar` и тестовыми credentials для авторизации в интеграционных проверках.
- **Зачем:** обеспечить воспроизводимые проверки RBAC-матрицы без зависимости от внешних данных БД.
- **Артефакты:** `backend/tests/conftest.py`.
- **Результат:** тесты могут самостоятельно получать токены `doctor` и `registrar` и проверять роль-специфичное поведение API.

## 2026-04-15 — Шаг 41: Прогон полного интеграционного набора после RBAC-расширения

- **Что сделано:** выполнен `docker compose up -d --build backend` и затем `docker compose exec -T backend pytest -q`.
- **Зачем:** подтвердить корректность всего набора после добавления нового тестового файла и расширения фикстур.
- **Артефакты:** `backend/tests/test_integration_api_flow.py`, `backend/tests/test_integration_negative_cases.py`, `backend/tests/test_integration_validation_cases.py`, `backend/tests/test_integration_period_boundaries.py`, `backend/tests/test_integration_rbac_reports_matrix.py`, `backend/tests/conftest.py`.
- **Результат:** интеграционный набор проходит полностью — `8 passed`; документация синхронно обновлена.

## 2026-04-15 — Шаг 42: Интеграционные тесты фильтров и пагинации

- **Что сделано:** добавлен файл `backend/tests/test_integration_filters_pagination.py` с проверками списка пациентов и записей на прием по `q/status/patient_id` и `skip/limit`.
- **Зачем:** покрыть частый класс регрессий API в списочных endpoint (фильтрация, пагинация, границы параметров).
- **Артефакты:** `backend/tests/test_integration_filters_pagination.py`.
- **Результат:** подтверждена корректность постраничного вывода и фильтрации; зафиксированы ожидаемые `422` для `limit=0`.

## 2026-04-15 — Шаг 43: Подготовка изолированных данных для pagination-case в appointments

- **Что сделано:** в тесте фильтров добавлена локальная подготовка отдельного `schedule` и двух `schedule_slots` через `db_conn`, затем через API созданы и отфильтрованы `appointments`.
- **Зачем:** избежать конфликтов с уже занятыми слотами из других интеграционных файлов и сделать сценарий детерминированным.
- **Артефакты:** `backend/tests/test_integration_filters_pagination.py`.
- **Результат:** сценарий стабилен и не зависит от порядка запуска остальных тестов.

## 2026-04-15 — Шаг 44: Полный прогон после добавления filters/pagination покрытия

- **Что сделано:** выполнен `docker compose up -d --build backend` и затем `docker compose exec -T backend pytest -q`.
- **Зачем:** подтвердить, что добавленный файл корректно включен в контейнерный запуск и совместим с текущим набором.
- **Артефакты:** `backend/tests/test_integration_api_flow.py`, `backend/tests/test_integration_negative_cases.py`, `backend/tests/test_integration_validation_cases.py`, `backend/tests/test_integration_period_boundaries.py`, `backend/tests/test_integration_rbac_reports_matrix.py`, `backend/tests/test_integration_filters_pagination.py`.
- **Результат:** полный интеграционный набор проходит — `10 passed`; документация обновлена синхронно.

## 2026-04-15 — Шаг 45: Переход к frontend и запуск рабочего SPA-каркаса

- **Что сделано:** вместо placeholder собран реальный frontend на `React + TypeScript + Vite`; добавлены конфиги (`vite.config.ts`, `tsconfig*.json`, `index.html`) и обновлены npm-скрипты.
- **Зачем:** начать реализацию клиентской части и сразу перейти к интеграции с backend API.
- **Артефакты:** `frontend/package.json`, `frontend/package-lock.json`, `frontend/index.html`, `frontend/tsconfig.json`, `frontend/tsconfig.node.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`.
- **Результат:** frontend собирается (`npm run build`) и готов к запуску как локально, так и через Docker.

## 2026-04-15 — Шаг 46: Прямая интеграция frontend с backend endpoint-ами

- **Что сделано:** реализован API-клиент и UI-экран с авторизацией и загрузкой данных из backend (`auth/login`, `auth/me`, `patients`, `appointments`), добавлена пагинация по `skip/limit` на стороне UI.
- **Зачем:** получить сразу рабочую связку фронт-бэк и сократить цикл ручной проверки функциональности.
- **Артефакты:** `frontend/src/api.ts`, `frontend/src/types.ts`, `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/src/vite-env.d.ts`.
- **Результат:** после логина `admin/admin12345` frontend получает токен и отображает данные из backend.

## 2026-04-15 — Шаг 47: Инфраструктурная связка и CORS для браузерного доступа

- **Что сделано:** backend дополнен CORS middleware с настройкой из переменной окружения; в `docker-compose` добавлен сервис `frontend` и переменные интеграции.
- **Зачем:** обеспечить корректные браузерные запросы между `localhost:5173` и `localhost:8000` без CORS-блокировок.
- **Артефакты:** `backend/app/main.py`, `backend/app/core/settings.py`, `infra/docker-compose.yml`, `infra/.env.example`, `frontend/Dockerfile`, `frontend/.env.example`.
- **Результат:** preflight на `POST /api/v1/auth/login` возвращает `200` с корректными `Access-Control-*` заголовками.

## 2026-04-15 — Шаг 48: Актуализация документации и проверка запуска frontend+backend

- **Что сделано:** обновлены инструкции и статус в документации для нового frontend-контурa и связки с backend; выполнен запуск `docker compose up -d --build backend frontend`.
- **Зачем:** синхронизировать документацию с текущим состоянием проекта и зафиксировать воспроизводимый сценарий проверки.
- **Артефакты:** `README.md`, `frontend/README.md`, `Documentation/PROJECT_STRUCTURE.md`, `Documentation/WORKLOG.md`.
- **Результат:** сервисы `frontend` и `backend` доступны на `http://localhost:5173` и `http://localhost:8000`.

## 2026-04-15 — Шаг 49: Role-aware UI и первые write-сценарии из frontend

- **Что сделано:** в frontend добавлены ролевые блоки и формы записи данных в backend: создание пациента (`POST /patients`) и создание записи на прием (`POST /appointments`) для ролей `admin/registrar`; для ролей `admin/registrar/doctor` добавлена загрузка отчета `GET /reports/diagnoses`.
- **Зачем:** перейти от read-only демо к рабочей связке frontend->backend с базовыми бизнес-действиями в UI.
- **Артефакты:** `frontend/src/App.tsx`, `frontend/src/api.ts`, `frontend/src/types.ts`.
- **Результат:** интерфейс отображает доступные действия в зависимости от роли текущего пользователя.

## 2026-04-15 — Шаг 50: Проверка сборки и контейнерного запуска после role-aware расширения

- **Что сделано:** выполнены `npm run build` в `frontend` и `docker compose up -d --build frontend` в `infra`, затем проверена доступность UI.
- **Зачем:** подтвердить, что изменения стабильны и воспроизводимы в основном docker-сценарии.
- **Артефакты:** `frontend/Dockerfile`, `infra/docker-compose.yml`, `frontend/src/*`.
- **Результат:** frontend успешно собирается и доступен на `http://localhost:5173`.

## 2026-04-15 — Шаг 51: Синхронная актуализация документации по frontend-возможностям

- **Что сделано:** обновлены инструкции по проверке role-aware UI и backend-интеграции в корневом и frontend README.
- **Зачем:** сохранить документацию в полном соответствии с текущей реализацией интерфейса.
- **Артефакты:** `README.md`, `frontend/README.md`, `Documentation/WORKLOG.md`.
- **Результат:** ручная проверка ролей и новых UI-сценариев описана пошагово.

## 2026-04-15 — Шаг 52: Архитектурный рефакторинг frontend по слоям

- **Что сделано:** фронтенд полностью переведен с монолитного `App.tsx` на структуру `app/pages/widgets/features/entities/shared`; вынесены сущностные API-клиенты, типы и переиспользуемые UI-компоненты.
- **Зачем:** обеспечить масштабируемую архитектуру и снизить связность между UI, сетью и бизнес-логикой.
- **Артефакты:** `frontend/src/app/*`, `frontend/src/pages/*`, `frontend/src/widgets/*`, `frontend/src/features/*`, `frontend/src/entities/*`, `frontend/src/shared/*`, `frontend/src/main.tsx`.
- **Результат:** логика приложения декомпозирована по канонам слоистой frontend-архитектуры, сборка проходит.

## 2026-04-15 — Шаг 53: Modern SaaS дизайн-система и role-aware маршрутизация

- **Что сделано:** добавлены дизайн-токены и глобальная тема, внедрен `AppLayout`, UI-kit (`Button/Input/Select/Card/Alert/Badge/EmptyState`), добавлены маршруты `/dashboard`, `/patients`, `/appointments`, `/reports` и route guards по ролям.
- **Зачем:** улучшить UI/UX, сделать интерфейс визуально консистентным и безопасно ограничить доступ к страницам по RBAC.
- **Артефакты:** `frontend/src/app/styles/*`, `frontend/src/app/layouts/AppLayout.tsx`, `frontend/src/app/providers/*`, `frontend/src/pages/*`, `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`.
- **Результат:** интерфейс стал структурированным, читаемым и role-aware на уровне маршрутов и элементов.

## 2026-04-15 — Шаг 54: Закрытие backend UX-gap для создания appointment без UUID вручную

- **Что сделано:** добавлены read endpoint-ы `GET /api/v1/doctors` и `GET /api/v1/schedule-slots` (с фильтрами по врачу, датам и статусу), подключены в API-роутер и сервисный слой.
- **Зачем:** убрать ручной ввод UUID врача/слота во frontend-форме записи на прием.
- **Артефакты:** `backend/app/api/v1/doctors.py`, `backend/app/api/v1/schedule_slots.py`, `backend/app/api/router.py`, `backend/app/api/deps.py`, `backend/app/services/doctor_service.py`, `backend/app/services/schedule_service.py`, `backend/app/infrastructure/repositories/doctor_repository.py`, `backend/app/infrastructure/repositories/schedule_repository.py`, `backend/app/schemas/doctors.py`, `backend/app/schemas/schedules.py`.
- **Результат:** frontend получает список врачей и доступные слоты через API, форма записи работает без ручного UUID слота.

## 2026-04-15 — Шаг 55: Верификация и синхронное обновление спецификаций

- **Что сделано:** выполнены `npm run build`, `docker compose up -d --build backend frontend`, `docker compose exec -T backend pytest -q`, а также smoke-проверки новых endpoint-ов (`/doctors`, `/schedule-slots`).
- **Зачем:** подтвердить стабильность после большого рефакторинга и корректность нового API-контракта.
- **Артефакты:** `README.md`, `frontend/README.md`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `Documentation/openapi.yaml`, `Documentation/PROJECT_STRUCTURE.md`, `Documentation/WORKLOG.md`.
- **Результат:** frontend и backend запускаются согласованно, регрессии в интеграционных тестах отсутствуют (`10 passed`), документация синхронизирована.

## 2026-04-15 — Шаг 56: UX-рефакторинг навигации и разделение страниц без дублей

- **Что сделано:** убрана концепция «супер-страницы» с дублирующим контентом; `dashboard` оставлен как обзорный экран (KPI + быстрые переходы), а детальные блоки и формы перенесены в профильные страницы `patients`, `appointments`, `reports`.
- **Зачем:** устранить UX-проблему дублирования функциональности в одном экране и сделать навигацию семантически чистой: каждый пункт меню = отдельный фокусный workflow.
- **Артефакты:** `frontend/src/pages/dashboard/ui/DashboardPage.tsx`, `frontend/src/pages/patients/ui/PatientsPage.tsx`, `frontend/src/pages/appointments/ui/AppointmentsPage.tsx`, `frontend/src/pages/reports/ui/ReportsPage.tsx`.
- **Результат:** UX стал предсказуемым: пользователь не видит одинаковый контент и в меню, и в длинной прокрутке dashboard.

## 2026-04-15 — Шаг 57: Улучшение поведения левой панели и визуальной иерархии

- **Что сделано:** для layout внедрено стабильное поведение скролла (`sticky` sidebar, отдельная прокрутка main-зоны), обновлены сетки обзорных карточек и адаптивные брейкпоинты.
- **Зачем:** повысить читаемость и контроль контекста при длинных страницах, особенно в рабочем сценарии регистратуры.
- **Артефакты:** `frontend/src/app/styles/global.css`.
- **Результат:** левая навигация остается структурным ориентиром и больше не воспринимается как повторяющийся контент.

## 2026-04-15 — Шаг 58: Дополнительная UX-полировка по замечаниям пользователя

- **Что сделано:** добавлены breadcrumbs и унифицированный page header, переработаны `Patients`/`Appointments` таблицы (сортировка + управление видимостью колонок), dashboard оставлен строго обзорным без дублирования функциональных блоков.
- **Зачем:** устранить перегруженность и повторяемость интерфейса, повысить информативность таблиц и сделать навигацию предсказуемой.
- **Артефакты:** `frontend/src/app/layouts/AppLayout.tsx`, `frontend/src/pages/dashboard/ui/DashboardPage.tsx`, `frontend/src/pages/patients/ui/PatientsPage.tsx`, `frontend/src/pages/appointments/ui/AppointmentsPage.tsx`, `frontend/src/pages/reports/ui/ReportsPage.tsx`, `frontend/src/widgets/patients/ui/PatientsWidget.tsx`, `frontend/src/widgets/appointments/ui/AppointmentsWidget.tsx`, `frontend/src/app/styles/global.css`.
- **Результат:** UI стал чище и более продуктовым: левая панель не дублирует контент, а каждая страница отвечает только за свой workflow.

## 2026-04-15 — Шаг 59: UX next-step — анимации, toast и сохранение пользовательских предпочтений

- **Что сделано:** внедрены глобальные toast-уведомления через `ToastProvider` (успех/ошибка/инфо), подключены в сценарии `patients/appointments/reports`; добавлен generic-хук `usePersistentState` и сохранение настроек таблиц (`sort` и видимость колонок) в `localStorage`; добавлены плавные анимации переходов контента, карточек, кнопок, строк таблиц и уведомлений.
- **Зачем:** повысить perceived performance и отзывчивость UI, сократить повторные действия пользователя после перезагрузки страницы и улучшить UX-feedback без перегрузки страниц alert-блоками.
- **Артефакты:** `frontend/src/app/providers/AppProviders.tsx`, `frontend/src/app/providers/ToastProvider.tsx`, `frontend/src/shared/ui/ToastViewport.tsx`, `frontend/src/shared/lib/usePersistentState.ts`, `frontend/src/widgets/patients/ui/PatientsWidget.tsx`, `frontend/src/widgets/appointments/ui/AppointmentsWidget.tsx`, `frontend/src/pages/patients/ui/PatientsPage.tsx`, `frontend/src/pages/appointments/ui/AppointmentsPage.tsx`, `frontend/src/pages/reports/ui/ReportsPage.tsx`, `frontend/src/app/styles/global.css`, `frontend/README.md`.
- **Результат:** интерфейс стал более «живым» и продуктовым: переходы воспринимаются плавнее, пользовательские настройки таблиц сохраняются между сессиями, а ключевые действия подтверждаются ненавязчивыми toast-уведомлениями.

## 2026-04-15 — Шаг 60: Кадровый контур врачей (создание + управление записями)

- **Что сделано:** на backend добавлен endpoint `POST /api/v1/doctors` с созданием `users(role=doctor)` и `doctors` в одной транзакции; на frontend добавлен раздел `Doctors` для ролей `admin/registrar`: создание врача, просмотр списка врачей, загрузка записей выбранного врача, отмена и перенос записи на новый доступный слот.
- **Зачем:** закрыть практический сценарий управления персоналом врачей и их расписанием записи из UI без ручных SQL/UUID-операций.
- **Артефакты:** `backend/app/schemas/doctors.py`, `backend/app/infrastructure/repositories/doctor_repository.py`, `backend/app/services/doctor_service.py`, `backend/app/api/v1/doctors.py`, `frontend/src/pages/doctors/ui/DoctorsPage.tsx`, `frontend/src/entities/doctor/model/types.ts`, `frontend/src/entities/doctor/api/doctorApi.ts`, `frontend/src/entities/appointment/model/types.ts`, `frontend/src/entities/appointment/api/appointmentApi.ts`, `frontend/src/app/providers/AppRouter.tsx`, `frontend/src/app/layouts/AppLayout.tsx`, `frontend/src/entities/user/model/permissions.ts`, `frontend/src/pages/dashboard/ui/DashboardPage.tsx`, `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `README.md`, `frontend/README.md`.
- **Результат:** система поддерживает полный кадровый workflow по врачам в web-интерфейсе: добавить врача, выбрать врача, увидеть его записи и оперативно выполнить перенос/отмену записи.

## 2026-04-15 — Шаг 61: Диагнозы для admin/doctor + расширение списка врачей (ФИО/специализация)

- **Что сделано:** внедрены ролевые ограничения назначения диагноза в backend: `admin` может назначать диагноз любому визиту, `doctor` — только собственным пациентам и только после завершения приема (`appointment=completed`, `visit=completed`); добавлена страница `Diagnoses` (`/visits`) для назначения диагноза из UI; расширен список врачей полями ФИО и специализаций, а форма создания врача дополнена ФИО и `specialty_ids`.
- **Зачем:** закрыть бизнес-правила медицинского процесса по ролям и сделать список врачей понятным для администратора без переходов в сторонние справочники.
- **Артефакты:** `backend/app/services/visit_service.py`, `backend/app/infrastructure/repositories/visit_repository.py`, `backend/app/schemas/doctors.py`, `backend/app/infrastructure/repositories/doctor_repository.py`, `backend/app/services/doctor_service.py`, `frontend/src/pages/visits/ui/VisitsPage.tsx`, `frontend/src/entities/visit/api/visitApi.ts`, `frontend/src/entities/visit/model/types.ts`, `frontend/src/app/providers/AppRouter.tsx`, `frontend/src/app/layouts/AppLayout.tsx`, `frontend/src/pages/doctors/ui/DoctorsPage.tsx`, `frontend/src/entities/doctor/model/types.ts`, `frontend/src/entities/user/model/permissions.ts`, `frontend/src/pages/dashboard/ui/DashboardPage.tsx`, `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `README.md`, `frontend/README.md`.
- **Результат:** администратор и врач получили рабочий UI/API контур назначения диагнозов с корректным RBAC, а список врачей стал информативным за счет ФИО и специализаций.

## 2026-04-15 — Шаг 62: Русификация UI, кадровые параметры врача и демо-наполнение БД

- **Что сделано:** фронтенд дополнительно русифицирован (навигация, формы, разделы), в модуле `Doctors` добавлены кадровые функции администратора (`оклад`, `премия`, `увольнение/восстановление`) и endpoint `PATCH /api/v1/doctors/{doctor_id}/employment`; добавлен endpoint `GET /api/v1/specialties` и мультивыбор специализаций по названиям; в API `appointments/visits` добавлены `patient_full_name` и `doctor_full_name`; подготовлен идемпотентный SQL `seed_demo_data.sql` и скрипты запуска для реалистичного наполнения БД.
- **Зачем:** убрать «сырые» UUID из ключевых экранов, сделать кадровый контур полноценным для админа и обеспечить сразу понятные демонстрационные данные для проверки бизнес-сценариев.
- **Артефакты:** `backend/app/api/v1/doctors.py`, `backend/app/api/v1/specialties.py`, `backend/app/services/doctor_service.py`, `backend/app/infrastructure/repositories/doctor_repository.py`, `backend/app/services/appointment_service.py`, `backend/app/infrastructure/repositories/appointment_repository.py`, `backend/app/services/visit_service.py`, `backend/app/infrastructure/repositories/visit_repository.py`, `backend/app/schemas/doctors.py`, `backend/app/schemas/appointments.py`, `backend/app/schemas/visits.py`, `backend/app/schemas/specialties.py`, `frontend/src/pages/doctors/ui/DoctorsPage.tsx`, `frontend/src/pages/visits/ui/VisitsPage.tsx`, `frontend/src/app/layouts/AppLayout.tsx`, `frontend/src/features/auth/login-form/ui/LoginForm.tsx`, `frontend/src/entities/specialty/*`, `infra/db/seed_demo_data.sql`, `infra/scripts/seed_data.py`, `infra/scripts/seed_data.ps1`, `infra/scripts/seed_data.sh`, `Documentation/openapi.yaml`, `Documentation/API_ENDPOINTS_AND_CONTRACTS.md`, `README.md`, `frontend/README.md`.
- **Результат:** интерфейс стал более понятным русскоязычному пользователю, админ получил инструменты кадрового управления врачами, а демо-база теперь содержит реалистичные ФИО/специализации/приемы/диагнозы для проверки без ручного заполнения.
