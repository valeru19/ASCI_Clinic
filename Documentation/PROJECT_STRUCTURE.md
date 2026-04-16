# Проектная файловая структура

Ниже приведена рекомендуемая структура репозитория для АИС "Клиника" с разделением по слоям и зонам ответственности.

```text
Course/
├─ Documentation/
│  ├─ README.md
│  ├─ PROJECT_STRUCTURE.md
│  └─ WORKLOG.md
├─ uml/
│  ├─ c4-context.puml
│  ├─ c4-container.puml
│  └─ c4-component-backend.puml
├─ backend/
│  ├─ app/
│  │  ├─ api/                  # Presentation Layer: роутеры FastAPI
│  │  │  ├─ deps.py
│  │  │  └─ v1/
│  │  │     ├─ auth.py
│  │  │     ├─ patients.py
│  │  │     ├─ schedules.py
│  │  │     ├─ appointments.py
│  │  │     ├─ visits.py
│  │  │     ├─ labs.py
│  │  │     └─ reports.py
│  │  ├─ services/             # Application Layer: use cases
│  │  │  ├─ auth_service.py
│  │  │  ├─ patient_service.py
│  │  │  ├─ schedule_service.py
│  │  │  ├─ appointment_service.py
│  │  │  ├─ visit_service.py
│  │  │  ├─ lab_service.py
│  │  │  └─ report_service.py
│  │  ├─ domain/               # Domain Layer: сущности, VO, доменные правила
│  │  │  ├─ entities/
│  │  │  ├─ value_objects/
│  │  │  ├─ policies/
│  │  │  └─ repositories.py    # интерфейсы репозиториев
│  │  ├─ infrastructure/       # Infrastructure Layer: SQLAlchemy, внешние адаптеры
│  │  │  ├─ db/
│  │  │  │  ├─ base.py
│  │  │  │  ├─ session.py
│  │  │  │  └─ models/
│  │  │  ├─ repositories/
│  │  │  ├─ unit_of_work.py
│  │  │  └─ notifications/
│  │  ├─ schemas/              # Pydantic DTO
│  │  ├─ core/                 # config, security, logging
│  │  └─ main.py
│  ├─ alembic/
│  ├─ tests/
│  │  ├─ unit/
│  │  ├─ integration/
│  │  └─ conftest.py
│  ├─ pyproject.toml
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  │  ├─ app/                  # роутинг, провайдеры, layout
│  │  ├─ pages/
│  │  ├─ widgets/
│  │  ├─ features/
│  │  ├─ entities/
│  │  ├─ shared/
│  │  └─ main.tsx
│  ├─ public/
│  ├─ package.json
│  └─ Dockerfile
├─ infra/
│  ├─ docker-compose.yml
│  ├─ .env.example
│  └─ scripts/
│     ├─ backup_db.sh
│     └─ seed_data.py
├─ .gitignore
└─ README.md
```

## Зачем такая структура

- Четко разделяет слои (`api`, `services`, `domain`, `infrastructure`), что упрощает сопровождение.
- Поддерживает принципы GoF/DDD-подхода: интерфейсы в домене, реализации в инфраструктуре.
- Ускоряет тестирование: unit-тесты для `services/domain`, integration-тесты для API и БД.
- Упрощает защиту курсового: легко показать архитектуру от C4 до конкретных каталогов.

## Текущее состояние

На текущий момент в репозитории уже созданы и активно используются:
- `backend/` (FastAPI + слои `api/services/infrastructure/schemas/core`);
- `frontend/` (React + Vite + route/role-aware UI по слоям `app/pages/widgets/features/entities/shared`, интеграция с `auth/patients/appointments/doctors/schedule-slots/reports`);
- `infra/` (docker-compose, init SQL, seed-скрипты);
- `Documentation/` и `uml/`;
- корневой `README.md` и `TECHNICAL_SPECIFICATION.md`.

### Реализованные backend-модули
- `auth` (JWT, `/auth/login`, `/auth/me`, RBAC dependency);
- `patients` (CRUD + soft delete);
- `schedules` (расписания, генерация слотов, исключения);
- `appointments` (создание, список, отмена, перенос);
- `visits` (создание, список, получение, завершение, diagnoses, prescriptions, referrals);
- `labs` (создание направлений, добавление тестов, внесение и просмотр результатов);
- `reports` (нагрузка врачей, статистика диагнозов/записей, финансовая сводка).
