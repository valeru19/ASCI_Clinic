import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AppLayout } from "@/app/layouts/AppLayout";
import { useAuth } from "@/app/providers/AuthProvider";
import { appointmentApi } from "@/entities/appointment/api/appointmentApi";
import { doctorApi } from "@/entities/doctor/api/doctorApi";
import { patientApi } from "@/entities/patient/api/patientApi";
import { reportApi } from "@/entities/report/api/reportApi";
import {
  canManageAppointments,
  canManageDiagnoses,
  canManageDoctors,
  canManagePatients,
  canViewDiagnosesReport,
} from "@/entities/user/model/permissions";
import { isoDateOffset } from "@/shared/lib/date";
import { Alert, Badge, Button, Card, EmptyState } from "@/shared/ui";

type OverviewMetrics = {
  patientsTotal: number;
  appointmentsTotal: number;
  doctorsTotal: number;
  topDiagnosesCount: number;
};

const DEFAULT_METRICS: OverviewMetrics = {
  patientsTotal: 0,
  appointmentsTotal: 0,
  doctorsTotal: 0,
  topDiagnosesCount: 0,
};

export function DashboardPage() {
  const { token, user } = useAuth();
  const [metrics, setMetrics] = useState<OverviewMetrics>(DEFAULT_METRICS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canPatients = canManagePatients(user);
  const canAppointments = canManageAppointments(user);
  const canDiagnoses = canManageDiagnoses(user);
  const canDoctors = canManageDoctors(user);
  const canReports = canViewDiagnosesReport(user);

  useEffect(() => {
    if (!token) {
      return;
    }
    void loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadOverview() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const [patients, appointments, doctors, diagnoses] = await Promise.all([
        patientApi.list(token, "", 0, 1),
        appointmentApi.list(token, 0, 1),
        doctorApi.list(token, 0, 1),
        canReports
          ? reportApi.diagnoses(token, isoDateOffset(-30), isoDateOffset(0), 10)
          : Promise.resolve({ items: [] }),
      ]);

      setMetrics({
        patientsTotal: patients.total,
        appointmentsTotal: appointments.total,
        doctorsTotal: doctors.total,
        topDiagnosesCount: diagnoses.items.length,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить обзорные данные");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Главная"
      subtitle="Обзор системы без дублей контента. Детальные операции вынесены в отдельные разделы меню."
      breadcrumbs={["Главная"]}
      headerActions={
        <Button variant="ghost" onClick={() => void loadOverview()} disabled={loading}>
          {loading ? "Обновление..." : "Обновить обзор"}
        </Button>
      }
    >
      {error && <Alert variant="error">{error}</Alert>}

      <div className="overview-grid">
        <Card title="Пациенты" action={<Badge>{metrics.patientsTotal}</Badge>}>
          <p className="ui-muted">Общее количество пациентов в системе.</p>
          {canPatients && (
            <div className="ui-row">
              <Link to="/patients">
                <Button variant="secondary">Открыть раздел</Button>
              </Link>
            </div>
          )}
        </Card>

        <Card title="Записи" action={<Badge>{metrics.appointmentsTotal}</Badge>}>
          <p className="ui-muted">Общее количество записей на прием.</p>
          {canAppointments && (
            <div className="ui-row">
              <Link to="/appointments">
                <Button variant="secondary">Открыть раздел</Button>
              </Link>
            </div>
          )}
        </Card>

        <Card title="Врачи" action={<Badge>{metrics.doctorsTotal}</Badge>}>
          <p className="ui-muted">Активные и неактивные врачи в справочнике.</p>
          {canDoctors && (
            <div className="ui-row">
              <Link to="/doctors">
                <Button variant="secondary">Управление врачами</Button>
              </Link>
            </div>
          )}
        </Card>

        <Card title="Диагнозы (30 дней)" action={<Badge>{metrics.topDiagnosesCount}</Badge>}>
          <p className="ui-muted">Количество позиций в топ-диагнозах за период.</p>
          {canReports && (
            <div className="ui-row">
              <Link to="/reports">
                <Button variant="secondary">Открыть отчет</Button>
              </Link>
            </div>
          )}
        </Card>
      </div>

      <Card title="Быстрые действия" subtitle="Навигация по основным рабочим сценариям">
        <div className="ui-row">
          {canPatients && (
            <Link to="/patients">
              <Button>Пациенты</Button>
            </Link>
          )}
          {canAppointments && (
            <Link to="/appointments">
              <Button>Записи</Button>
            </Link>
          )}
          {canDoctors && (
            <Link to="/doctors">
              <Button variant="secondary">Врачи</Button>
            </Link>
          )}
          {canDiagnoses && (
            <Link to="/visits">
              <Button>Диагнозы</Button>
            </Link>
          )}
          {canReports && (
            <Link to="/reports">
              <Button variant="secondary">Отчеты</Button>
            </Link>
          )}
        </div>
        {!canPatients && !canAppointments && !canReports && (
          <EmptyState title="Нет доступных действий" description="Проверьте права пользователя." />
        )}
      </Card>

    </AppLayout>
  );
}
