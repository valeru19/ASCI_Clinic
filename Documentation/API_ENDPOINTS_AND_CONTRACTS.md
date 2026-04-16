# Взаимодействия, эндпоинты и JSON-контракты

## 1) Как фронтенд и внешние системы взаимодействуют с backend (по C4 Level 3)

### 1.1 Frontend -> Backend

Поток запроса:
1. `Frontend SPA` отправляет HTTP-запрос в `REST Controllers` (Presentation Layer).
2. `Controllers` валидируют входные данные (Pydantic) и передают сценарий в `Application Services`.
3. `Application Services` выполняют бизнес-логику, проверяют RBAC (`Strategy`) и формируют транзакцию (`Unit of Work`).
4. Доступ к БД идет только через интерфейсы репозиториев (`Repository Interfaces`) и их реализации (`SQLAlchemy Repositories`, `Adapter`).
5. Ответ сериализуется в JSON и возвращается на фронтенд.

### 1.2 Внешние системы

- **Сервис уведомлений:** backend передает события (подтверждение/отмена/перенос записи, готовность результатов).
- **Лабораторная система (опционально):** backend принимает/отправляет статусы и результаты исследований через адаптер интеграции.

### 1.3 Почему это безопасно для медицинских данных

- Валидация на входе: типы, диапазоны, обязательные поля, форматы дозировок и дат.
- Ролевая проверка (RBAC): врач не может выполнять административные операции, пациент не может редактировать медицинские записи.
- Транзакции ACID: визит, диагнозы, назначения и лабораторные назначения сохраняются согласованно.

---

## 2) Каталог эндпоинтов (фактическое состояние на текущий момент)

Ниже указаны эндпоинты в трех статусах:
- `implemented` — реализовано и доступно в коде;
- `partial` — реализована только часть целевого функционала;
- `planned` — запланировано, но пока не реализовано.

## Auth
- `POST /api/v1/auth/login` — вход и выдача JWT (`implemented`).
  - Формат запроса: `application/x-www-form-urlencoded` (`username`, `password`).
  - Это сделано для корректной работы кнопки **Authorize** в Swagger.
- `GET /api/v1/auth/me` — профиль текущего пользователя по Bearer JWT (`implemented`).
- `POST /api/v1/auth/refresh` — обновление access token (`planned`).

## Patients
- `POST /api/v1/patients` — регистрация пациента (`implemented`).
- `GET /api/v1/patients` — поиск/фильтрация пациентов (`implemented`).
- `GET /api/v1/patients/{patient_id}` — карточка пациента (`implemented`).
- `PATCH /api/v1/patients/{patient_id}` — частичное обновление (`implemented`).
- `DELETE /api/v1/patients/{patient_id}` — soft delete (`implemented`).

## Schedules
- `POST /api/v1/schedules` — создание расписания (`implemented`).
- `GET /api/v1/schedules` — просмотр расписаний (`implemented`).
- `GET /api/v1/schedule-slots` — просмотр слотов по врачу и диапазону дат (`implemented`).
- `POST /api/v1/schedule-slots/generate` — генерация слотов (`implemented`).
- `POST /api/v1/schedule-exceptions` — исключения расписания (`implemented`).
  - Автоматическое применение исключений к уже созданным слотам/записям: (`planned`).

## Doctors
- `POST /api/v1/doctors` — создание врача с user-аккаунтом (`implemented`).
- `GET /api/v1/doctors` — список врачей для UI и фильтров (`implemented`).
- `PATCH /api/v1/doctors/{doctor_id}/employment` — кадровые изменения (оклад, премия, увольнение) (`implemented`).
- `GET /api/v1/specialties` — справочник специализаций (`implemented`).

## Appointments
- `POST /api/v1/appointments` — запись пациента на прием (`implemented`).
- `GET /api/v1/appointments` — список записей с фильтрами (`implemented`).
- `PATCH /api/v1/appointments/{appointment_id}/cancel` — отмена (`implemented`).
- `PATCH /api/v1/appointments/{appointment_id}/reschedule` — перенос (`implemented`).
- `PATCH /api/v1/appointments/{appointment_id}/confirm` — отдельное подтверждение (`planned`).

## Visits
- `POST /api/v1/visits` — создание визита по записи (`implemented`).
- `GET /api/v1/visits` — список визитов с фильтрами (`implemented`).
- `GET /api/v1/visits/{visit_id}` — получение визита (`implemented`).
- `PATCH /api/v1/visits/{visit_id}/complete` — завершение визита (`implemented`).
- `POST /api/v1/visits/{visit_id}/diagnoses` — добавление диагнозов (`implemented`).
- `POST /api/v1/visits/{visit_id}/prescriptions` — назначения (`implemented`).
- `POST /api/v1/visits/{visit_id}/referrals` — направления (`implemented`).

## Laboratory
- `POST /api/v1/labs/orders` — создание лабораторного направления (`implemented`).
- `POST /api/v1/labs/orders/{order_id}/items` — добавление тестов в направление (`implemented`).
- `POST /api/v1/labs/results` — внесение результата анализа (`implemented`).
- `GET /api/v1/labs/results` — список результатов с фильтрами (`implemented`).

## Reporting
- `GET /api/v1/reports/doctor-workload` — нагрузка врачей за период (`implemented`).
- `GET /api/v1/reports/diagnoses` — топ диагнозов за период (`implemented`).
- `GET /api/v1/reports/appointments` — сводка записей по статусам (`implemented`).
- `GET /api/v1/reports/finance` — финансовая сводка по счетам (`implemented`).

---

## 3) Контракты JSON (запрос/ответ)

Ниже — базовые контракты, которые должны быть отражены в Swagger/OpenAPI.

### 3.1 POST /api/v1/appointments

**Request**
```json
{
  "patient_id": "b7f2de71-a3f8-44d5-a0d2-1b8ec3a9a5bd",
  "doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
  "slot_id": "80e7f4ee-ec7d-40f9-8be9-43b436e8f41c",
  "reason": "Боль в горле, температура 37.8"
}
```

**Response 201**
```json
{
  "id": "957dc8f4-a974-42aa-b969-ae0f4f1f573f",
  "status": "planned",
  "patient_id": "b7f2de71-a3f8-44d5-a0d2-1b8ec3a9a5bd",
  "doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
  "slot_id": "80e7f4ee-ec7d-40f9-8be9-43b436e8f41c",
  "created_at": "2026-04-15T20:30:00Z"
}
```

**Валидация**
- `patient_id`, `doctor_id`, `slot_id`: валидный UUID, обязательны.
- `reason`: до 2000 символов.
- `slot_id` должен быть в статусе `available`.

### 3.2 POST /api/v1/auth/login

**Content-Type:** `application/x-www-form-urlencoded`

**Request (form fields)**
- `username` (string, required)
- `password` (string, required)

**Response 200**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Важно**
- формат формы обязателен для совместимости с OAuth2-окном **Authorize** в Swagger;
- при неверных данных — `401 Unauthorized`.

### 3.3 GET /api/v1/visits

**Query-параметры**
- `doctor_id` (uuid, optional);
- `patient_id` (uuid, optional);
- `status` (`in_progress | completed | cancelled`, optional);
- `skip` (int >= 0);
- `limit` (int 1..200).

**Response 200**
```json
{
  "items": [
    {
      "id": "0be95c72-1c6e-4892-b18d-cfe1317f564f",
      "appointment_id": "957dc8f4-a974-42aa-b969-ae0f4f1f573f",
      "patient_id": "b7f2de71-a3f8-44d5-a0d2-1b8ec3a9a5bd",
      "doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
      "chief_complaint": "Боль в горле",
      "exam_notes": "Гиперемия зева",
      "treatment_plan": "Симптоматическая терапия",
      "visit_status": "in_progress",
      "closed_at": null
    }
  ],
  "total": 1
}
```

### 3.4 PATCH /api/v1/visits/{visit_id}/complete

**Request**
```json
{
  "treatment_plan": "Амбулаторное лечение 5 дней"
}
```

**Response 200**
```json
{
  "id": "0be95c72-1c6e-4892-b18d-cfe1317f564f",
  "appointment_id": "957dc8f4-a974-42aa-b969-ae0f4f1f573f",
  "patient_id": "b7f2de71-a3f8-44d5-a0d2-1b8ec3a9a5bd",
  "doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
  "chief_complaint": "Боль в горле",
  "exam_notes": "Гиперемия зева",
  "treatment_plan": "Амбулаторное лечение 5 дней",
  "visit_status": "completed",
  "closed_at": "2026-04-15T21:20:00Z"
}
```

**Бизнес-правила**
- завершать можно только визит со статусом `in_progress`;
- при завершении визита запись (`appointment`) переводится в `completed`, если не была в финальном статусе;
- если `visit_id` не найден — `404 Not Found`.

### 3.5 POST /api/v1/visits/{visit_id}/diagnoses

**Request**
```json
{
  "items": [
    {
      "icd10_code": "J06.9",
      "is_primary": true,
      "comment": "ОРВИ, без осложнений"
    }
  ]
}
```

**Response 201**
```json
{
  "visit_id": "1962cdf8-d39a-45cc-8a9a-c2ec9ffad6de",
  "created": 1,
  "diagnoses": [
    {
      "id": "4df2c678-0963-4e4f-a595-a3bf88f6ca35",
      "icd10_code": "J06.9",
      "is_primary": true,
      "comment": "ОРВИ, без осложнений"
    }
  ]
}
```

**Бизнес-правила**
- добавление диагнозов доступно только для визита в статусе `in_progress`;
- в одном запросе допускается не более одного `is_primary=true`;
- если первичный диагноз уже существует, новый первичный диагноз вернет `409 Conflict`;
- `icd10_code` должен существовать в `clinic.icd10_codes`, иначе `404 Not Found`.

### 3.6 POST /api/v1/visits/{visit_id}/prescriptions

**Request**
```json
{
  "items": [
    {
      "medication_id": "e7f98f69-cc01-4930-a5c6-faf851715574",
      "dosage": "500 mg",
      "frequency": "2 раза в день",
      "duration_days": 5,
      "instructions": "После еды"
    }
  ]
}
```

**Response 201**
```json
{
  "visit_id": "1962cdf8-d39a-45cc-8a9a-c2ec9ffad6de",
  "created": 1
}
```

**Бизнес-правила**
- назначения добавляются только к визиту в статусе `in_progress`;
- `medication_id` должен существовать в `clinic.medications`, иначе `404 Not Found`;
- `dosage` валидируется по шаблону `^\d+(\.\d+)?\s?(mg|ml|g|mcg)$`;
- `duration_days` в диапазоне `1..365`.

### 3.7 POST /api/v1/labs/orders

**Request**
```json
{
  "visit_id": "1962cdf8-d39a-45cc-8a9a-c2ec9ffad6de"
}
```

**Response 201**
```json
{
  "id": "89fb9d6f-7f1e-4238-b050-cc898947edb2",
  "visit_id": "1962cdf8-d39a-45cc-8a9a-c2ec9ffad6de",
  "patient_id": "b7f2de71-a3f8-44d5-a0d2-1b8ec3a9a5bd",
  "ordered_by_doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
  "status": "created",
  "ordered_at": "2026-04-15T22:15:00Z"
}
```

### 3.8 POST /api/v1/labs/orders/{order_id}/items

**Request**
```json
{
  "items": [
    {
      "test_type_id": "d4401e73-7214-4e3b-90bf-5d76a0bd99ce",
      "priority": "urgent"
    }
  ]
}
```

**Response 201**
```json
{
  "lab_order_id": "89fb9d6f-7f1e-4238-b050-cc898947edb2",
  "created": 1,
  "items": [
    {
      "id": "a2c9708d-7a8f-448f-bb38-9a2f45bffbf2",
      "lab_order_id": "89fb9d6f-7f1e-4238-b050-cc898947edb2",
      "test_type_id": "d4401e73-7214-4e3b-90bf-5d76a0bd99ce",
      "priority": "urgent"
    }
  ]
}
```

### 3.9 POST /api/v1/labs/results

**Request**
```json
{
  "lab_order_item_id": "a2c9708d-7a8f-448f-bb38-9a2f45bffbf2",
  "value_numeric": 5.2,
  "unit": "mmol/L",
  "reference_range": "3.9-5.5",
  "flag": "normal",
  "validated_by_doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c"
}
```

**Response 201**
```json
{
  "id": "07020a15-b6f4-4be5-bbd6-7cc3263c58a2",
  "lab_order_item_id": "a2c9708d-7a8f-448f-bb38-9a2f45bffbf2",
  "lab_order_id": "89fb9d6f-7f1e-4238-b050-cc898947edb2",
  "patient_id": "b7f2de71-a3f8-44d5-a0d2-1b8ec3a9a5bd",
  "value_numeric": 5.2,
  "flag": "normal",
  "resulted_at": "2026-04-15T22:20:00Z",
  "validated_by_doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c"
}
```

**Бизнес-правила лаборатории**
- направление создается только для существующего визита;
- в закрытое направление (`completed`, `cancelled`) нельзя добавлять новые тесты;
- для одного `lab_order_item_id` допускается только один результат;
- в результате должно быть заполнено минимум одно из полей: `value_text` или `value_numeric`.

### 3.10 POST /api/v1/visits/{visit_id}/referrals

**Request**
```json
{
  "items": [
    {
      "target_specialty_id": 2,
      "target_doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
      "reason": "Нужна консультация кардиолога",
      "comment": "Повышенное АД на приеме"
    }
  ]
}
```

**Response 201**
```json
{
  "visit_id": "1962cdf8-d39a-45cc-8a9a-c2ec9ffad6de",
  "created": 1,
  "referrals": [
    {
      "id": "caa6bf3e-c7d6-462f-a4f2-9bbebd6fef8f",
      "target_specialty_id": 2,
      "target_doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
      "reason": "Нужна консультация кардиолога",
      "status": "created",
      "comment": "Повышенное АД на приеме",
      "created_at": "2026-04-15T22:40:00Z"
    }
  ]
}
```

**Бизнес-правила направлений**
- направления можно добавить только к визиту в статусе `in_progress`;
- `target_specialty_id` должен существовать в `clinic.specialties`;
- если передан `target_doctor_id`, такой врач должен существовать;
- создаваемый статус направления по умолчанию — `created`.

### 3.11 GET /api/v1/reports/doctor-workload

**Query**
- `date_from` (required, date)
- `date_to` (required, date)

**Response 200**
```json
{
  "items": [
    {
      "doctor_id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
      "doctor_name": "doctor_ivanov",
      "appointments_count": 38,
      "completed_count": 31,
      "cancelled_count": 4
    }
  ]
}
```

### 3.12 GET /api/v1/reports/diagnoses

**Query**
- `date_from` (required, date)
- `date_to` (required, date)
- `limit` (optional, 1..200, default 20)

**Response 200**
```json
{
  "date_from": "2026-01-01",
  "date_to": "2026-12-31",
  "items": [
    {
      "icd10_code": "J06.9",
      "title": "Острая инфекция верхних дыхательных путей неуточненная",
      "total": 12
    }
  ]
}
```

### 3.13 GET /api/v1/reports/appointments

**Query**
- `date_from` (required, date)
- `date_to` (required, date)

**Response 200**
```json
{
  "date_from": "2026-01-01",
  "date_to": "2026-12-31",
  "total": 120,
  "planned": 21,
  "confirmed": 8,
  "completed": 79,
  "cancelled": 9,
  "no_show": 3
}
```

### 3.14 GET /api/v1/reports/finance

**Query**
- `date_from` (required, date)
- `date_to` (required, date)

**Response 200**
```json
{
  "date_from": "2026-01-01",
  "date_to": "2026-12-31",
  "invoices_count": 88,
  "total_amount": 523400.0,
  "paid_amount": 471200.0,
  "issued_amount": 52200.0
}
```

### 3.15 POST /api/v1/doctors

**Request**
```json
{
  "username": "doctor_petrov",
  "email": "doctor_petrov@clinic.local",
  "password": "doctor12345",
  "last_name": "Петров",
  "first_name": "Петр",
  "middle_name": "Петрович",
  "license_number": "LIC-778899",
  "experience_years": 9,
  "specialty_ids": [1, 2],
  "monthly_salary": 170000,
  "bonus_percent": 18,
  "is_active": true
}
```

**Response 201**
```json
{
  "id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
  "username": "doctor_petrov",
  "email": "doctor_petrov@clinic.local",
  "last_name": "Петров",
  "first_name": "Петр",
  "middle_name": "Петрович",
  "full_name": "Петров Петр Петрович",
  "license_number": "LIC-778899",
  "experience_years": 9,
  "specializations": ["Терапевт", "Кардиолог"],
  "monthly_salary": 170000,
  "bonus_percent": 18,
  "is_active": true
}
```

**Бизнес-правила**
- создаются сразу две сущности: `clinic.users` (`role=doctor`) и `clinic.doctors`;
- `username`, `email` и `license_number` должны быть уникальными, иначе `409 Conflict`;
- `specialty_ids` (если переданы) должны существовать в `clinic.specialties`, иначе `404`;
- доступ: `admin`, `registrar`.

### 3.16 GET /api/v1/doctors

**Query**
- `include_inactive` (optional, bool, default `false`)
- `skip` (optional, int >= 0)
- `limit` (optional, int 1..200)

**Response 200**
```json
{
  "items": [
    {
      "id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
      "username": "doctor_ivanov",
      "email": "doctor_ivanov@clinic.local",
      "last_name": "Иванов",
      "first_name": "Иван",
      "middle_name": "Иванович",
      "full_name": "Иванов Иван Иванович",
      "license_number": "LIC-123456",
      "experience_years": 7,
      "specializations": ["Терапевт"],
      "monthly_salary": 160000,
      "bonus_percent": 20,
      "is_active": true
    }
  ],
  "total": 1
}
```

### 3.17 PATCH /api/v1/doctors/{doctor_id}/employment

**Request**
```json
{
  "monthly_salary": 180000,
  "bonus_percent": 25,
  "is_active": false
}
```

**Response 200**
```json
{
  "id": "f3204ec5-a58b-42f4-b82b-02bf8094372c",
  "full_name": "Иванов Иван Иванович",
  "license_number": "LIC-123456",
  "experience_years": 7,
  "specializations": ["Терапевт", "Кардиолог"],
  "monthly_salary": 180000,
  "bonus_percent": 25,
  "is_active": false
}
```

**Бизнес-правила**
- доступно только роли `admin`;
- `is_active=false` соответствует увольнению врача (врач деактивируется и в `users`, и в `doctors`);
- `bonus_percent` ограничен диапазоном `0..100`.

### 3.18 GET /api/v1/specialties

**Response 200**
```json
{
  "items": [
    { "id": 1, "name": "Терапевт" },
    { "id": 2, "name": "Педиатр" },
    { "id": 3, "name": "Хирург" }
  ],
  "total": 3
}
```

### 3.19 GET /api/v1/schedule-slots

**Query**
- `doctor_id` (optional, uuid)
- `date_from` (required, date)
- `date_to` (required, date)
- `status` (optional, one of `available|booked|blocked|cancelled`, default `available`)
- `skip` (optional, int >= 0)
- `limit` (optional, int 1..200)

**Response 200**
```json
{
  "items": [
    {
      "id": "80e7f4ee-ec7d-40f9-8be9-43b436e8f41c",
      "schedule_id": "2de5f3dc-c95d-4a20-8611-9308dd9cb22b",
      "start_at": "2026-04-16T10:00:00Z",
      "end_at": "2026-04-16T10:30:00Z",
      "status": "available"
    }
  ],
  "total": 1
}
```

**Назначение для frontend**
- endpoint используется в форме создания `appointments`, чтобы выбирать доступный слот без ручного ввода UUID.

### Ролевые правила для `POST /api/v1/visits/{visit_id}/diagnoses`

- `admin`: может назначать диагноз любому пациенту/визиту без ограничения по статусу визита;
- `doctor`: может назначать диагноз только пациенту из собственной записи и только после завершения приема (`appointment.status=completed` и `visit.visit_status=completed`);
- при нарушении правил доступа возвращается `403`, при нарушении бизнес-статуса — `409`.
- в `GET /api/v1/visits` и `GET /api/v1/appointments` для UI возвращаются `patient_full_name` и `doctor_full_name`, чтобы в интерфейсе не показывать «сырые» UUID.

---

## 4) Стандарт ошибок API

Единый формат ошибки:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Некорректные входные данные",
    "details": [
      {
        "field": "duration_days",
        "issue": "must be between 1 and 365"
      }
    ],
    "request_id": "7b2ad07d-c03f-4f0d-8a65-b44fecc9d42f"
  }
}
```

Рекомендуемые коды:
- `VALIDATION_ERROR` (422)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `CONFLICT` (409)
- `INTERNAL_ERROR` (500)

---

## 5) Минимальные требования к Swagger/OpenAPI

- Все эндпоинты должны содержать:
  - `summary`, `description`;
  - схемы запроса/ответа;
  - примеры (`example`);
  - коды ошибок;
  - требования авторизации (Bearer JWT).
- Для критичных медицинских полей — явные ограничения (`min/max`, `pattern`, `enum`, `format`).

---

## 6) Интеграционное тестовое покрытие (backend)

Текущий набор интеграционных тестов (`pytest`, запуск в контейнере `backend`):
- `tests/test_integration_api_flow.py` — сквозной `happy-path`:
  `auth -> appointment -> visit -> diagnoses -> prescriptions -> referrals -> labs -> reports`.
- `tests/test_integration_negative_cases.py` — негативные проверки:
  - RBAC: врач получает `403` на `POST /api/v1/patients/`;
  - конфликт: повторное внесение `lab_result` на один и тот же `lab_order_item_id` возвращает `409`.
- `tests/test_integration_validation_cases.py` — валидационные проверки:
  - некорректный `icd10_code` -> `422`;
  - некорректный `dosage` -> `422`;
  - некорректный `target_specialty_id` -> `422`;
  - `lab_result` без `value_text/value_numeric` -> `422`;
  - `reports/diagnoses` с `limit=0` -> `422`.
- `tests/test_integration_period_boundaries.py` — проверки граничных периодов:
  - генерация слотов на однодневный период (`date_from=date_to`) -> `201`, слоты создаются корректно;
  - невалидные диапазоны дат для `schedule-slots/generate` и `schedule-exceptions` (`date_to < date_from`) -> `422`;
  - однодневный период для `reports/diagnoses` и `reports/appointments` поддерживается -> `200`.
- `tests/test_integration_rbac_reports_matrix.py` — матрица доступов `reports`:
  - `admin` имеет доступ ко всем отчетам (`doctor-workload`, `diagnoses`, `appointments`, `finance`) -> `200`;
  - `registrar` имеет доступ к `doctor-workload`, `diagnoses`, `appointments` -> `200`, к `finance` -> `403`;
  - `doctor` имеет доступ только к `diagnoses` -> `200`, к остальным отчетам -> `403`.
- `tests/test_integration_filters_pagination.py` — фильтры и пагинация списков:
  - `patients`: поиск по `q` + постраничный вывод через `skip/limit`, валидация `limit=0` -> `422`;
  - `appointments`: фильтрация по `patient_id` и `status`, постраничный вывод через `skip/limit`, валидация `limit=0` -> `422`.
