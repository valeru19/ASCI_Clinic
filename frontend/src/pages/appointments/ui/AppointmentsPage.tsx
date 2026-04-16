import { useEffect, useState } from "react";

import { AppLayout } from "@/app/layouts/AppLayout";
import { useAuth } from "@/app/providers/AuthProvider";
import { useToast } from "@/app/providers/ToastProvider";
import { appointmentApi } from "@/entities/appointment/api/appointmentApi";
import type { Appointment, AppointmentCreatePayload } from "@/entities/appointment/model/types";
import { doctorApi } from "@/entities/doctor/api/doctorApi";
import type { Doctor } from "@/entities/doctor/model/types";
import { patientApi } from "@/entities/patient/api/patientApi";
import type { Patient } from "@/entities/patient/model/types";
import { scheduleSlotApi } from "@/entities/scheduleSlot/api/scheduleSlotApi";
import type { ScheduleSlot } from "@/entities/scheduleSlot/model/types";
import { CreateAppointmentForm } from "@/features/appointment/create-appointment/ui/CreateAppointmentForm";
import { isoDateOffset } from "@/shared/lib/date";
import { Alert, Card } from "@/shared/ui";
import { AppointmentsWidget } from "@/widgets/appointments/ui/AppointmentsWidget";

export function AppointmentsPage() {
  const { token } = useAuth();
  const { pushToast } = useToast();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [appointmentsTotal, setAppointmentsTotal] = useState(0);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [slots, setSlots] = useState<ScheduleSlot[]>([]);
  const [dateFrom, setDateFrom] = useState(isoDateOffset(1));
  const [dateTo, setDateTo] = useState(isoDateOffset(1));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }
    void Promise.all([loadAppointments(), loadPatients(), loadDoctors()]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadAppointments() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await appointmentApi.list(token, 0, 20);
      setAppointments(data.items);
      setAppointmentsTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки записей");
    } finally {
      setLoading(false);
    }
  }

  async function loadPatients() {
    if (!token) {
      return;
    }
    try {
      const data = await patientApi.list(token, "", 0, 200);
      setPatients(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки пациентов");
    }
  }

  async function loadDoctors() {
    if (!token) {
      return;
    }
    try {
      const data = await doctorApi.list(token);
      setDoctors(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки врачей");
    }
  }

  async function handleLoadSlots(nextFrom: string, nextTo: string, doctorId: string) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await scheduleSlotApi.listAvailableByDoctor(
        token,
        doctorId,
        nextFrom,
        nextTo,
      );
      setDateFrom(nextFrom);
      setDateTo(nextTo);
      setSlots(data.items);
      setSuccess(`Доступных слотов: ${data.total}`);
      pushToast(`Доступных слотов: ${data.total}`, "info");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки слотов";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(payload: AppointmentCreatePayload) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await appointmentApi.create(token, payload);
      setSuccess("Запись успешно создана.");
      pushToast("Запись успешно создана.", "success");
      await loadAppointments();
      setSlots((prev) => prev.filter((item) => item.id !== payload.slot_id));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка создания записи";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Записи к врачу"
      subtitle="Запись к врачу через выбор доступного слота без ручного ввода UUID"
      breadcrumbs={["Главная", "Записи"]}
    >
      {error && <Alert variant="error">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <div className="dashboard-grid">
        <div className="dashboard-grid__main">
          <AppointmentsWidget appointments={appointments} total={appointmentsTotal} />
        </div>
        <div className="dashboard-grid__side">
          <Card title="Новая запись" subtitle="Выберите врача, диапазон дат и доступный слот">
            <CreateAppointmentForm
              loading={loading}
              patients={patients}
              doctors={doctors}
              slots={slots}
              dateFrom={dateFrom}
              dateTo={dateTo}
              onDateChange={handleLoadSlots}
              onCreate={handleCreate}
            />
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
