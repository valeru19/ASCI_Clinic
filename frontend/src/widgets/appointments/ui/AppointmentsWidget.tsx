import { useMemo } from "react";

import type { Appointment } from "@/entities/appointment/model/types";
import { usePersistentState } from "@/shared/lib/usePersistentState";
import { Badge, Card, EmptyState, Select } from "@/shared/ui";

type AppointmentsWidgetProps = {
  appointments: Appointment[];
  total: number;
};

export function AppointmentsWidget({ appointments, total }: AppointmentsWidgetProps) {
  const [sortBy, setSortBy] = usePersistentState<"created_at" | "status" | "id">(
    "appointments-sort-by",
    "created_at",
  );
  const [sortDir, setSortDir] = usePersistentState<"asc" | "desc">(
    "appointments-sort-dir",
    "desc",
  );

  const sortedAppointments = useMemo(() => {
    const copy = [...appointments];
    const dir = sortDir === "asc" ? 1 : -1;
    copy.sort((a, b) => {
      if (sortBy === "created_at") {
        return a.created_at.localeCompare(b.created_at) * dir;
      }
      if (sortBy === "status") {
        return a.status.localeCompare(b.status) * dir;
      }
      return a.id.localeCompare(b.id) * dir;
    });
    return copy;
  }, [appointments, sortBy, sortDir]);

  return (
    <Card
      title="Записи на прием"
      subtitle="Актуальные записи по текущей пагинации"
      action={<Badge variant="neutral">всего {total}</Badge>}
    >
      <div className="ui-toolbar">
        <Select
          label="Сортировка"
          aria-label="Сортировка записей"
          value={sortBy}
          onChange={(event) => setSortBy(event.target.value as "created_at" | "status" | "id")}
        >
          <option value="created_at">По дате создания</option>
          <option value="status">По статусу</option>
          <option value="id">По ID</option>
        </Select>
        <Select
          label="Направление"
          aria-label="Направление сортировки записей"
          value={sortDir}
          onChange={(event) => setSortDir(event.target.value as "asc" | "desc")}
        >
          <option value="desc">Новые сверху</option>
          <option value="asc">Старые сверху</option>
        </Select>
      </div>
      {appointments.length === 0 ? (
        <EmptyState title="Записей нет" description="Создайте новую запись через форму справа." />
      ) : (
        <div className="ui-table-wrap">
          <table className="ui-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Статус</th>
                <th>Создана</th>
              </tr>
            </thead>
            <tbody>
              {sortedAppointments.map((appointment) => (
                <tr key={appointment.id}>
                  <td>{appointment.id.slice(0, 8)}...</td>
                  <td>{appointment.status}</td>
                  <td>{new Date(appointment.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
