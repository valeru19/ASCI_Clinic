import { type FormEvent, useEffect, useMemo, useState } from "react";

import { AppLayout } from "@/app/layouts/AppLayout";
import { useAuth } from "@/app/providers/AuthProvider";
import { useToast } from "@/app/providers/ToastProvider";
import { appointmentApi } from "@/entities/appointment/api/appointmentApi";
import type { Appointment } from "@/entities/appointment/model/types";
import { doctorApi } from "@/entities/doctor/api/doctorApi";
import type { Doctor, DoctorCreatePayload } from "@/entities/doctor/model/types";
import { specialtyApi } from "@/entities/specialty/api/specialtyApi";
import type { Specialty } from "@/entities/specialty/model/types";
import { scheduleSlotApi } from "@/entities/scheduleSlot/api/scheduleSlotApi";
import type { ScheduleSlot } from "@/entities/scheduleSlot/model/types";
import { isoDateOffset } from "@/shared/lib/date";
import { Alert, Badge, Button, Card, EmptyState, Input, Select } from "@/shared/ui";

const INITIAL_FORM: DoctorCreatePayload = {
  username: "",
  email: "",
  password: "",
  last_name: "",
  first_name: "",
  middle_name: "",
  license_number: "",
  experience_years: 0,
  specialty_ids: [],
  monthly_salary: 0,
  bonus_percent: 0,
  is_active: true,
};

export function DoctorsPage() {
  const { token, user } = useAuth();
  const { pushToast } = useToast();
  const isAdmin = user?.role === "admin";

  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState("");
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [availableSlots, setAvailableSlots] = useState<ScheduleSlot[]>([]);
  const [selectedAppointmentId, setSelectedAppointmentId] = useState("");
  const [selectedNewSlotId, setSelectedNewSlotId] = useState("");
  const [cancelReason, setCancelReason] = useState("");
  const [slotDateFrom, setSlotDateFrom] = useState(isoDateOffset(1));
  const [slotDateTo, setSlotDateTo] = useState(isoDateOffset(7));
  const [createForm, setCreateForm] = useState<DoctorCreatePayload>(INITIAL_FORM);
  const [employmentSalary, setEmploymentSalary] = useState("0");
  const [employmentBonus, setEmploymentBonus] = useState("0");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const selectedDoctor = useMemo(
    () => doctors.find((doctor) => doctor.id === selectedDoctorId) ?? null,
    [doctors, selectedDoctorId],
  );

  useEffect(() => {
    if (!token) {
      return;
    }
    void Promise.all([loadDoctors(), loadSpecialties()]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (!token || !selectedDoctorId) {
      setAppointments([]);
      return;
    }
    void loadDoctorAppointments(selectedDoctorId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDoctorId, token]);

  useEffect(() => {
    if (!selectedDoctor) {
      return;
    }
    setEmploymentSalary(String(selectedDoctor.monthly_salary));
    setEmploymentBonus(String(selectedDoctor.bonus_percent));
  }, [selectedDoctor]);

  async function loadDoctors() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await doctorApi.list(token, 0, 200);
      setDoctors(data.items);
      if (!selectedDoctorId && data.items.length > 0) {
        setSelectedDoctorId(data.items[0].id);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки врачей";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function loadSpecialties() {
    if (!token) {
      return;
    }
    try {
      const data = await specialtyApi.list(token);
      setSpecialties(data.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки специализаций";
      setError(message);
      pushToast(message, "error");
    }
  }

  async function loadDoctorAppointments(doctorId: string) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await appointmentApi.list(token, 0, 100, { doctorId });
      setAppointments(data.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки записей врача";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateDoctor(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const created = await doctorApi.create(token, createForm);
      setSuccess("Врач успешно добавлен.");
      pushToast("Врач успешно добавлен.", "success");
      setCreateForm(INITIAL_FORM);
      await loadDoctors();
      setSelectedDoctorId(created.id);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка создания врача";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleEmploymentUpdate(isActive?: boolean) {
    if (!token || !selectedDoctorId) {
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const updated = await doctorApi.updateEmployment(token, selectedDoctorId, {
        monthly_salary: Number(employmentSalary),
        bonus_percent: Number(employmentBonus),
        is_active: isActive,
      });
      setSuccess("Кадровые данные врача обновлены.");
      pushToast("Кадровые данные врача обновлены.", "success");
      await loadDoctors();
      setSelectedDoctorId(updated.id);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка обновления кадровых данных";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleCancelAppointment(appointmentId: string) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      await appointmentApi.cancel(token, appointmentId, { reason: cancelReason || undefined });
      setSuccess("Запись отменена.");
      pushToast("Запись отменена.", "success");
      if (selectedDoctorId) {
        await loadDoctorAppointments(selectedDoctorId);
      }
      setCancelReason("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка отмены записи";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadRescheduleSlots() {
    if (!token || !selectedDoctorId) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await scheduleSlotApi.listAvailableByDoctor(
        token,
        selectedDoctorId,
        slotDateFrom,
        slotDateTo,
      );
      setAvailableSlots(data.items);
      pushToast(`Найдено слотов: ${data.total}`, "info");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки слотов";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleRescheduleAppointment() {
    if (!token || !selectedAppointmentId || !selectedNewSlotId || !selectedDoctorId) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      await appointmentApi.reschedule(token, selectedAppointmentId, { slot_id: selectedNewSlotId });
      setSuccess("Запись успешно перенесена.");
      pushToast("Запись успешно перенесена.", "success");
      setSelectedNewSlotId("");
      setSelectedAppointmentId("");
      setAvailableSlots([]);
      await loadDoctorAppointments(selectedDoctorId);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка переноса записи";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Врачи"
      subtitle="Кадровое управление: ФИО, специализации, оклад, премия, статус трудоустройства"
      breadcrumbs={["Главная", "Врачи"]}
    >
      {error && <Alert variant="error">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <div className="dashboard-grid">
        <div className="dashboard-grid__main">
          <Card
            title="Список врачей"
            subtitle="Выберите врача, чтобы увидеть записи и кадровые настройки"
            action={<Badge variant="neutral">всего {doctors.length}</Badge>}
          >
            {doctors.length === 0 ? (
              <EmptyState title="Врачи не найдены" description="Добавьте врача через форму справа." />
            ) : (
              <div className="ui-table-wrap">
                <table className="ui-table">
                  <thead>
                    <tr>
                      <th>Выбор</th>
                      <th>ФИО</th>
                      <th>Специализация</th>
                      <th>Лицензия</th>
                      <th>Оклад</th>
                      <th>Премия</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {doctors.map((doctor) => (
                      <tr key={doctor.id}>
                        <td>
                          <Button
                            variant={selectedDoctorId === doctor.id ? "secondary" : "ghost"}
                            onClick={() => setSelectedDoctorId(doctor.id)}
                          >
                            {selectedDoctorId === doctor.id ? "Выбран" : "Выбрать"}
                          </Button>
                        </td>
                        <td>{doctor.full_name}</td>
                        <td>{doctor.specializations.length > 0 ? doctor.specializations.join(", ") : "—"}</td>
                        <td>{doctor.license_number}</td>
                        <td>{doctor.monthly_salary.toLocaleString("ru-RU")} ₽</td>
                        <td>{doctor.bonus_percent}%</td>
                        <td>{doctor.is_active ? "Работает" : "Уволен"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          <Card
            title="Записи выбранного врача"
            subtitle={selectedDoctor ? `Врач: ${selectedDoctor.full_name}` : "Врач не выбран"}
          >
            {!selectedDoctor ? (
              <EmptyState
                title="Сначала выберите врача"
                description="После выбора врача здесь появятся его записи и действия."
              />
            ) : appointments.length === 0 ? (
              <EmptyState title="У врача пока нет записей" description="Создайте записи в разделе «Записи»." />
            ) : (
              <div className="ui-table-wrap">
                <table className="ui-table">
                  <thead>
                    <tr>
                      <th>Пациент</th>
                      <th>Статус</th>
                      <th>Дата создания</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map((appointment) => (
                      <tr key={appointment.id}>
                        <td>{appointment.patient_full_name ?? "Пациент"}</td>
                        <td>{appointment.status}</td>
                        <td>{new Date(appointment.created_at).toLocaleString()}</td>
                        <td>
                          <div className="ui-row">
                            <Button
                              variant="secondary"
                              onClick={() => setSelectedAppointmentId(appointment.id)}
                            >
                              Выбрать для переноса
                            </Button>
                            <Button
                              variant="danger"
                              onClick={() => void handleCancelAppointment(appointment.id)}
                              disabled={appointment.status === "cancelled" || loading}
                            >
                              Отменить
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div className="dashboard-grid__side">
          <Card title="Добавить врача" subtitle="Создание профиля врача с ФИО, оплатой и специализациями">
            <form className="ui-form-grid" onSubmit={handleCreateDoctor}>
              <Input
                label="Логин"
                value={createForm.username}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, username: event.target.value }))}
                required
              />
              <Input
                label="Email"
                type="email"
                value={createForm.email}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, email: event.target.value }))}
                required
              />
              <Input
                label="Пароль"
                type="password"
                value={createForm.password}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, password: event.target.value }))}
                required
              />
              <Input
                label="Фамилия"
                value={createForm.last_name}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, last_name: event.target.value }))}
                required
              />
              <Input
                label="Имя"
                value={createForm.first_name}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, first_name: event.target.value }))}
                required
              />
              <Input
                label="Отчество"
                value={createForm.middle_name ?? ""}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, middle_name: event.target.value }))}
              />
              <Input
                label="Номер лицензии"
                value={createForm.license_number}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, license_number: event.target.value }))}
                required
              />
              <Input
                label="Стаж (лет)"
                type="number"
                min={0}
                max={60}
                value={createForm.experience_years}
                onChange={(event) =>
                  setCreateForm((prev) => ({
                    ...prev,
                    experience_years: Number(event.target.value) || 0,
                  }))
                }
                required
              />
              <Input
                label="Оклад (₽)"
                type="number"
                min={0}
                value={createForm.monthly_salary}
                onChange={(event) =>
                  setCreateForm((prev) => ({
                    ...prev,
                    monthly_salary: Number(event.target.value) || 0,
                  }))
                }
                required
              />
              <Input
                label="Премия (%)"
                type="number"
                min={0}
                max={100}
                value={createForm.bonus_percent}
                onChange={(event) =>
                  setCreateForm((prev) => ({
                    ...prev,
                    bonus_percent: Number(event.target.value) || 0,
                  }))
                }
                required
              />
              <Select
                label="Специализации (можно несколько)"
                multiple
                size={6}
                value={createForm.specialty_ids.map(String)}
                onChange={(event) => {
                  const values = Array.from(event.target.selectedOptions).map((option) =>
                    Number(option.value),
                  );
                  setCreateForm((prev) => ({ ...prev, specialty_ids: values }));
                }}
              >
                {specialties.map((specialty) => (
                  <option key={specialty.id} value={specialty.id}>
                    {specialty.name}
                  </option>
                ))}
              </Select>
              <Button type="submit" disabled={loading}>
                {loading ? "Сохранение..." : "Добавить врача"}
              </Button>
            </form>
          </Card>

          {isAdmin && (
            <Card title="Кадровые действия" subtitle="Для выбранного врача: оклад, премия, увольнение">
              {!selectedDoctor ? (
                <EmptyState title="Врач не выбран" description="Выберите врача в таблице слева." />
              ) : (
                <div className="ui-form-grid">
                  <Input
                    label="Оклад (₽)"
                    type="number"
                    min={0}
                    value={employmentSalary}
                    onChange={(event) => setEmploymentSalary(event.target.value)}
                  />
                  <Input
                    label="Премия (%)"
                    type="number"
                    min={0}
                    max={100}
                    value={employmentBonus}
                    onChange={(event) => setEmploymentBonus(event.target.value)}
                  />
                  <Button
                    variant="secondary"
                    onClick={() => void handleEmploymentUpdate(undefined)}
                    disabled={loading}
                  >
                    Сохранить оплату
                  </Button>
                  <Button variant="danger" onClick={() => void handleEmploymentUpdate(false)} disabled={loading}>
                    Уволить врача
                  </Button>
                  <Button variant="ghost" onClick={() => void handleEmploymentUpdate(true)} disabled={loading}>
                    Восстановить врача
                  </Button>
                </div>
              )}
            </Card>
          )}

          <Card title="Перенос записи" subtitle="Выберите запись, затем подберите новый свободный слот">
            <div className="ui-form-grid">
              <Select
                label="Запись для переноса"
                value={selectedAppointmentId}
                onChange={(event) => setSelectedAppointmentId(event.target.value)}
              >
                <option value="">Выберите запись</option>
                {appointments.map((appointment) => (
                  <option key={appointment.id} value={appointment.id}>
                    {(appointment.patient_full_name ?? appointment.id.slice(0, 8))} ({appointment.status})
                  </option>
                ))}
              </Select>
              <Input
                label="Дата от"
                type="date"
                value={slotDateFrom}
                onChange={(event) => setSlotDateFrom(event.target.value)}
              />
              <Input
                label="Дата до"
                type="date"
                value={slotDateTo}
                onChange={(event) => setSlotDateTo(event.target.value)}
              />
              <Button
                variant="secondary"
                onClick={() => void handleLoadRescheduleSlots()}
                disabled={!selectedDoctorId || loading}
              >
                Загрузить слоты
              </Button>
              <Select
                label="Новый слот"
                value={selectedNewSlotId}
                onChange={(event) => setSelectedNewSlotId(event.target.value)}
              >
                <option value="">Выберите свободный слот</option>
                {availableSlots.map((slot) => (
                  <option key={slot.id} value={slot.id}>
                    {new Date(slot.start_at).toLocaleString()} -{" "}
                    {new Date(slot.end_at).toLocaleTimeString()}
                  </option>
                ))}
              </Select>
              <Input
                label="Причина отмены"
                value={cancelReason}
                onChange={(event) => setCancelReason(event.target.value)}
                placeholder="Необязательно"
              />
              <Button
                onClick={() => void handleRescheduleAppointment()}
                disabled={!selectedAppointmentId || !selectedNewSlotId || loading}
              >
                Перенести запись
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
