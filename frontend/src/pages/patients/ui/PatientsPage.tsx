import { useEffect, useState } from "react";

import { AppLayout } from "@/app/layouts/AppLayout";
import { useAuth } from "@/app/providers/AuthProvider";
import { useToast } from "@/app/providers/ToastProvider";
import { patientApi } from "@/entities/patient/api/patientApi";
import type { PatientCreatePayload, Patient } from "@/entities/patient/model/types";
import { CreatePatientForm } from "@/features/patient/create-patient/ui/CreatePatientForm";
import { Alert, Card } from "@/shared/ui";
import { PatientsWidget } from "@/widgets/patients/ui/PatientsWidget";

export function PatientsPage() {
  const { token } = useAuth();
  const { pushToast } = useToast();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }
    void loadPatients();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, skip, limit]);

  async function loadPatients() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await patientApi.list(token, query, skip, limit);
      setPatients(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки пациентов");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreatePatient(payload: PatientCreatePayload) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await patientApi.create(token, payload);
      setSuccess("Пациент успешно создан.");
      pushToast("Пациент успешно создан.", "success");
      await loadPatients();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка создания пациента";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Пациенты"
      subtitle="Управление пациентами и быстрый доступ к регистрации новых записей"
      breadcrumbs={["Главная", "Пациенты"]}
    >
      {error && <Alert variant="error">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <div className="dashboard-grid">
        <div className="dashboard-grid__main">
          <PatientsWidget
            loading={loading}
            patients={patients}
            total={total}
            query={query}
            skip={skip}
            limit={limit}
            onQueryChange={setQuery}
            onSearch={async () => {
              setSkip(0);
              await loadPatients();
            }}
            onPrev={() => setSkip((prev) => Math.max(prev - limit, 0))}
            onNext={() => setSkip((prev) => prev + limit)}
            onLimitChange={(value) => {
              setLimit(value);
              setSkip(0);
            }}
          />
        </div>
        <div className="dashboard-grid__side">
          <Card title="Новый пациент" subtitle="Заполните минимальные поля для регистрации">
            <CreatePatientForm loading={loading} onCreate={handleCreatePatient} />
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
