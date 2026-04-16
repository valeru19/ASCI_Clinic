import { useState } from "react";

import { AppLayout } from "@/app/layouts/AppLayout";
import { useAuth } from "@/app/providers/AuthProvider";
import { useToast } from "@/app/providers/ToastProvider";
import { reportApi } from "@/entities/report/api/reportApi";
import type { DiagnosesStatsItem } from "@/entities/report/model/types";
import { DiagnosesReportFilter } from "@/features/report/diagnoses-filter/ui/DiagnosesReportFilter";
import { isoDateOffset } from "@/shared/lib/date";
import { Alert, Card } from "@/shared/ui";
import { DiagnosesReportWidget } from "@/widgets/reports/ui/DiagnosesReportWidget";

export function ReportsPage() {
  const { token } = useAuth();
  const { pushToast } = useToast();
  const [items, setItems] = useState<DiagnosesStatsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [defaultFrom, setDefaultFrom] = useState(isoDateOffset(-30));
  const [defaultTo, setDefaultTo] = useState(isoDateOffset(0));

  async function handleApply(dateFrom: string, dateTo: string) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await reportApi.diagnoses(token, dateFrom, dateTo, 20);
      setItems(data.items);
      setDefaultFrom(dateFrom);
      setDefaultTo(dateTo);
      pushToast("Отчет успешно обновлен.", "success");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки отчета";
      setError(message);
      pushToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout
      title="Отчеты"
      subtitle="Аналитика и диагностическая статистика по периоду"
      breadcrumbs={["Главная", "Отчеты"]}
    >
      {error && <Alert variant="error">{error}</Alert>}
      <div className="dashboard-grid">
        <div className="dashboard-grid__main">
          <DiagnosesReportWidget items={items} />
        </div>
        <div className="dashboard-grid__side">
          <Card title="Фильтр отчета" subtitle="Выберите период для обновления данных">
            <DiagnosesReportFilter
              loading={loading}
              defaultFrom={defaultFrom}
              defaultTo={defaultTo}
              onApply={handleApply}
            />
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
