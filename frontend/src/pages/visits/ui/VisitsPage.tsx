import { type FormEvent, useEffect, useState } from "react";

import { AppLayout } from "@/app/layouts/AppLayout";
import { useAuth } from "@/app/providers/AuthProvider";
import { useToast } from "@/app/providers/ToastProvider";
import { doctorApi } from "@/entities/doctor/api/doctorApi";
import type { Doctor } from "@/entities/doctor/model/types";
import { visitApi } from "@/entities/visit/api/visitApi";
import type { Visit } from "@/entities/visit/model/types";
import { Alert, Badge, Button, Card, EmptyState, Input, Select } from "@/shared/ui";

const VISIT_STATUS_LABELS: Record<string, string> = {
  in_progress: "В процессе",
  completed: "Завершен",
  cancelled: "Отменен",
};

export function VisitsPage() {
  const { token, user } = useAuth();
  const { pushToast } = useToast();

  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState("");
  const [selectedVisitId, setSelectedVisitId] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [icd10Code, setIcd10Code] = useState("");
  const [isPrimary, setIsPrimary] = useState(true);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isAdmin = user?.role === "admin";

  useEffect(() => {
    if (!token) {
      return;
    }
    if (isAdmin) {
      void loadDoctors();
    }
    void loadVisits();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isAdmin]);

  async function loadDoctors() {
    if (!token) {
      return;
    }
    try {
      const data = await doctorApi.list(token, 0, 200);
      setDoctors(data.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки врачей";
      setError(message);
      pushToast(message, "error");
    }
  }

  async function loadVisits() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await visitApi.list(token, 0, 100, {
        doctorId: isAdmin ? selectedDoctorId || undefined : undefined,
        status: statusFilter || undefined,
      });
      setVisits(data.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки визитов";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleAssignDiagnosis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedVisitId) {
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const data = await visitApi.addDiagnoses(token, selectedVisitId, {
        items: [
          {
            icd10_code: icd10Code.toUpperCase().trim(),
            is_primary: isPrimary,
            comment: comment.trim() || undefined,
          },
        ],
      });
      setSuccess(`Диагнозов добавлено: ${data.created}`);
      pushToast(`Диагноз успешно назначен (${data.created})`, "success");
      setIcd10Code("");
      setComment("");
      await loadVisits();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка назначения диагноза";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Диагнозы"
      subtitle="Назначение диагноза: admin — любому визиту, doctor — только своим завершенным приемам"
      breadcrumbs={["Главная", "Диагнозы"]}
      headerActions={
        <Button variant="ghost" onClick={() => void loadVisits()} disabled={loading}>
          {loading ? "Загрузка..." : "Обновить"}
        </Button>
      }
    >
      {error && <Alert variant="error">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <div className="dashboard-grid">
        <div className="dashboard-grid__main">
          <Card title="Визиты" action={<Badge variant="neutral">всего {visits.length}</Badge>}>
            <div className="ui-toolbar">
              {isAdmin && (
                <Select
                  label="Фильтр по врачу"
                  value={selectedDoctorId}
                  onChange={(event) => setSelectedDoctorId(event.target.value)}
                >
                  <option value="">Все врачи</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.full_name}
                    </option>
                  ))}
                </Select>
              )}
              <Select
                label="Статус визита"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
              >
                <option value="">Все</option>
                <option value="in_progress">В процессе</option>
                <option value="completed">Завершен</option>
                <option value="cancelled">Отменен</option>
              </Select>
              <Button variant="secondary" onClick={() => void loadVisits()} disabled={loading}>
                Применить
              </Button>
            </div>

            {visits.length === 0 ? (
              <EmptyState title="Визиты не найдены" description="Измени фильтры или создай визит." />
            ) : (
              <div className="ui-table-wrap">
                <table className="ui-table">
                  <thead>
                    <tr>
                      <th>Выбор</th>
                      <th>ID визита</th>
                      <th>Пациент</th>
                      <th>Врач</th>
                      <th>Статус</th>
                      <th>Закрыт</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visits.map((visit) => (
                      <tr key={visit.id}>
                        <td>
                          <Button
                            variant={selectedVisitId === visit.id ? "secondary" : "ghost"}
                            onClick={() => setSelectedVisitId(visit.id)}
                          >
                            {selectedVisitId === visit.id ? "Выбран" : "Выбрать"}
                          </Button>
                        </td>
                        <td>{visit.id.slice(0, 8)}...</td>
                        <td>{visit.patient_full_name}</td>
                        <td>{visit.doctor_full_name}</td>
                        <td>{VISIT_STATUS_LABELS[visit.visit_status] ?? visit.visit_status}</td>
                        <td>{visit.closed_at ? new Date(visit.closed_at).toLocaleString() : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div className="dashboard-grid__side">
          <Card title="Назначить диагноз" subtitle="Один диагноз за действие (ICD-10)">
            <form className="ui-form-grid" onSubmit={handleAssignDiagnosis}>
              <Select
                label="Выбранный визит"
                value={selectedVisitId}
                onChange={(event) => setSelectedVisitId(event.target.value)}
                required
              >
                <option value="">Выберите визит</option>
                {visits.map((visit) => (
                  <option key={visit.id} value={visit.id}>
                    {visit.patient_full_name} / {visit.doctor_full_name} (
                    {VISIT_STATUS_LABELS[visit.visit_status] ?? visit.visit_status})
                  </option>
                ))}
              </Select>
              <Input
                label="Код ICD-10"
                value={icd10Code}
                onChange={(event) => setIcd10Code(event.target.value.toUpperCase())}
                placeholder="Например: J06.9"
                required
              />
              <Select
                label="Тип диагноза"
                value={isPrimary ? "primary" : "secondary"}
                onChange={(event) => setIsPrimary(event.target.value === "primary")}
              >
                <option value="primary">Основной</option>
                <option value="secondary">Вторичный</option>
              </Select>
              <Input
                label="Комментарий"
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Необязательно"
              />
              <Button type="submit" disabled={!selectedVisitId || !icd10Code || loading}>
                {loading ? "Сохранение..." : "Назначить диагноз"}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
