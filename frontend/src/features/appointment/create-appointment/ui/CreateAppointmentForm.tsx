import { type FormEvent, useMemo, useState } from "react";

import type { AppointmentCreatePayload } from "@/entities/appointment/model/types";
import type { Doctor } from "@/entities/doctor/model/types";
import type { Patient } from "@/entities/patient/model/types";
import type { ScheduleSlot } from "@/entities/scheduleSlot/model/types";
import { Button, Input, Select } from "@/shared/ui";

type CreateAppointmentFormProps = {
  loading: boolean;
  patients: Patient[];
  doctors: Doctor[];
  slots: ScheduleSlot[];
  dateFrom: string;
  dateTo: string;
  onDateChange: (dateFrom: string, dateTo: string, doctorId: string) => Promise<void>;
  onCreate: (payload: AppointmentCreatePayload) => Promise<void>;
};

function initialDate(): string {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().slice(0, 10);
}

export function CreateAppointmentForm({
  loading,
  patients,
  doctors,
  slots,
  dateFrom,
  dateTo,
  onDateChange,
  onCreate,
}: CreateAppointmentFormProps) {
  const [patientId, setPatientId] = useState("");
  const [doctorId, setDoctorId] = useState("");
  const [slotId, setSlotId] = useState("");
  const [reason, setReason] = useState("Запись через frontend");
  const [localDateFrom, setLocalDateFrom] = useState(dateFrom || initialDate());
  const [localDateTo, setLocalDateTo] = useState(dateTo || initialDate());
  const [error, setError] = useState("");

  const hasEnoughData = useMemo(
    () => patientId.trim() && doctorId.trim() && slotId.trim(),
    [doctorId, patientId, slotId],
  );

  async function handleLoadSlots(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!doctorId) {
      setError("Выберите врача перед загрузкой слотов.");
      return;
    }
    if (localDateTo < localDateFrom) {
      setError("Дата 'по' должна быть не меньше даты 'с'.");
      return;
    }
    await onDateChange(localDateFrom, localDateTo, doctorId);
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!hasEnoughData) {
      setError("Заполните пациента, врача и слот.");
      return;
    }
    await onCreate({
      patient_id: patientId,
      doctor_id: doctorId,
      slot_id: slotId,
      reason: reason.trim() || undefined,
    });
  }

  return (
    <div className="ui-stack">
      <form className="ui-form-grid" onSubmit={handleLoadSlots}>
        <div className="ui-row ui-row--three">
          <Input
            label="С"
            type="date"
            name="slot-date-from"
            value={localDateFrom}
            onChange={(event) => setLocalDateFrom(event.target.value)}
          />
          <Input
            label="По"
            type="date"
            name="slot-date-to"
            value={localDateTo}
            onChange={(event) => setLocalDateTo(event.target.value)}
          />
          <Select
            label="Врач"
            name="slot-doctor-id"
            value={doctorId}
            onChange={(event) => {
              setDoctorId(event.target.value);
              setSlotId("");
            }}
          >
            <option value="">Выберите врача</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.username ?? doctor.id.slice(0, 8)} ({doctor.license_number})
              </option>
            ))}
          </Select>
        </div>
        <Button type="submit" variant="secondary" disabled={loading}>
          Загрузить доступные слоты
        </Button>
      </form>

      <form className="ui-form-grid" onSubmit={handleCreate}>
        <Select
          label="Пациент"
          name="appointment-patient-id"
          value={patientId}
          onChange={(event) => setPatientId(event.target.value)}
        >
          <option value="">Выберите пациента</option>
          {patients.map((patient) => (
            <option key={patient.id} value={patient.id}>
              {patient.last_name} {patient.first_name}
            </option>
          ))}
        </Select>
        <Select
          label="Слот"
          name="appointment-slot-id"
          value={slotId}
          onChange={(event) => setSlotId(event.target.value)}
          hint={slots.length === 0 ? "Сначала загрузите слоты по врачу и дате" : undefined}
        >
          <option value="">Выберите слот</option>
          {slots.map((slot) => (
            <option key={slot.id} value={slot.id}>
              {new Date(slot.start_at).toLocaleString()} - {new Date(slot.end_at).toLocaleTimeString()}
            </option>
          ))}
        </Select>
        <Input
          label="Причина"
          name="appointment-reason"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
        {error && <p className="ui-inline-error">{error}</p>}
        <Button type="submit" disabled={loading || !hasEnoughData}>
          Создать запись
        </Button>
      </form>
    </div>
  );
}
