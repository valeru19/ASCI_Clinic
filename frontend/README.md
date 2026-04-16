# Frontend (React + Vite)

SPA для быстрой работы с backend API АИС "Клиника".

## Что реализовано

- React + TypeScript + Vite + `react-router-dom`.
- Архитектура слоев: `app/pages/widgets/features/entities/shared`.
- Modern SaaS дизайн:
  - токены темы, единый layout, карточки, таблицы, alert/empty states;
  - единые состояния `loading/error/success`.
- UX-полировка страниц:
  - breadcrumbs и единый page header;
  - sticky левая панель + отдельный scroll main-контента;
  - dashboard только обзорный (без дублирования контента разделов);
  - таблицы пациентов и записей получили сортировку и управление видимостью колонок;
  - настройки сортировки/колонок сохраняются в `localStorage`;
  - глобальные toast-уведомления для успешных/ошибочных действий;
  - плавные micro-interactions (появление страниц, hover карточек/кнопок, анимация уведомлений).
- Role-aware маршруты и доступ:
  - `admin/registrar` — страницы `patients`, `appointments`, `doctors`, формы создания;
  - `admin/doctor` — страница `visits` (назначение диагнозов);
  - `admin/registrar/doctor` — страница `reports` (диагнозы).
  - `dashboard` теперь обзорный (KPI + быстрые действия), без дублирования детальных блоков из других разделов.
- Интеграция с backend endpoint-ами:
  - `POST /api/v1/auth/login`, `GET /api/v1/auth/me`;
  - `POST/GET /api/v1/doctors`, `PATCH /api/v1/doctors/{doctor_id}/employment`;
  - `GET /api/v1/specialties`;
  - `GET /api/v1/visits`, `POST /api/v1/visits/{visit_id}/diagnoses`;
  - `GET/POST /api/v1/patients`;
  - `GET/POST /api/v1/appointments`;
  - `GET /api/v1/doctors`;
  - `GET /api/v1/schedule-slots` (доступные слоты по врачу и датам);
  - `GET /api/v1/reports/diagnoses`.

## Локальный запуск

```powershell
cd D:\GorohProd\Course\frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:5173`.

По умолчанию API URL: `http://localhost:8000/api/v1` (переменная `VITE_API_BASE_URL`).

## Запуск через Docker Compose

Из `infra/`:

```powershell
docker compose up -d --build backend frontend
```

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`

## Тестовые учетные данные

- `username`: `admin`
- `password`: `admin12345`

## Что проверить вручную

1. Войти под `admin/admin12345`.
2. Перейти по маршрутам:
   - `/dashboard` (общий обзор),
   - `/patients`,
   - `/appointments`,
   - `/doctors`,
   - `/visits`,
   - `/reports`.
3. На `/dashboard` проверить, что видны только обзорные карточки и переходы, а не полные дубли разделов.
4. На `/appointments`:
   - выбрать врача;
   - загрузить слоты по дате (`schedule-slots`);
   - создать запись без ручного ввода UUID слота.
5. На `/reports` загрузить отчет по диагнозам за период.
6. На `/patients` и `/appointments` проверить сортировку таблиц и переключение колонок.
7. Обновить страницу и убедиться, что настройки сортировки/колонок не сбрасываются.
8. На `/doctors`:
   - добавить врача с ФИО/специализациями/окладом/премией;
   - проверить колонки ФИО и специализации;
   - изменить оклад/премию выбранного врача;
   - уволить и восстановить врача;
   - выбрать врача и проверить список его записей;
   - отменить запись и перенести запись на другой доступный слот.
9. На `/visits` назначить диагноз:
   - под `admin` — любому визиту;
   - под `doctor` — только своим завершенным визитам.
10. Проверить toast-уведомления при успешных/ошибочных действиях.
11. Убедиться, что при смене роли скрываются нерелевантные действия.
