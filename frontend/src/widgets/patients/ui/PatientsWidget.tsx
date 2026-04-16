import { useMemo } from "react";

import type { Patient } from "@/entities/patient/model/types";
import { usePersistentState } from "@/shared/lib/usePersistentState";
import { Badge, Button, Card, EmptyState, Input, Select } from "@/shared/ui";

type PatientsWidgetProps = {
  loading: boolean;
  patients: Patient[];
  total: number;
  query: string;
  skip: number;
  limit: number;
  onQueryChange: (value: string) => void;
  onSearch: () => Promise<void>;
  onPrev: () => void;
  onNext: () => void;
  onLimitChange: (value: number) => void;
};

export function PatientsWidget({
  loading,
  patients,
  total,
  query,
  skip,
  limit,
  onQueryChange,
  onSearch,
  onPrev,
  onNext,
  onLimitChange,
}: PatientsWidgetProps) {
  const [sortBy, setSortBy] = usePersistentState<"name" | "birth_date" | "gender" | "status">(
    "patients-sort-by",
    "name",
  );
  const [sortDir, setSortDir] = usePersistentState<"asc" | "desc">(
    "patients-sort-dir",
    "asc",
  );
  const [showBirthDate, setShowBirthDate] = usePersistentState<boolean>(
    "patients-col-birthdate",
    true,
  );
  const [showGender, setShowGender] = usePersistentState<boolean>(
    "patients-col-gender",
    true,
  );
  const [showStatus, setShowStatus] = usePersistentState<boolean>(
    "patients-col-status",
    true,
  );

  const sortedPatients = useMemo(() => {
    const copy = [...patients];
    const dir = sortDir === "asc" ? 1 : -1;
    copy.sort((a, b) => {
      if (sortBy === "name") {
        const aName = `${a.last_name} ${a.first_name}`.toLowerCase();
        const bName = `${b.last_name} ${b.first_name}`.toLowerCase();
        return aName.localeCompare(bName) * dir;
      }
      if (sortBy === "birth_date") {
        return a.birth_date.localeCompare(b.birth_date) * dir;
      }
      if (sortBy === "gender") {
        return a.gender.localeCompare(b.gender) * dir;
      }
      const aStatus = a.is_active ? "active" : "inactive";
      const bStatus = b.is_active ? "active" : "inactive";
      return aStatus.localeCompare(bStatus) * dir;
    });
    return copy;
  }, [patients, sortBy, sortDir]);

  return (
    <Card
      title="Пациенты"
      subtitle="Поиск, пагинация и быстрый обзор карточек"
      action={<Badge variant="neutral">всего {total}</Badge>}
    >
      <div className="ui-stack">
        <form
          className="ui-row"
          onSubmit={(event) => {
            event.preventDefault();
            void onSearch();
          }}
        >
          <Input
            label="Поиск"
            name="patients-search"
            placeholder="Поиск по ФИО"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
          <Button type="submit" disabled={loading}>
            Найти
          </Button>
        </form>

        <div className="ui-row ui-row--spread">
          <div className="ui-row">
            <Button type="button" variant="ghost" onClick={onPrev} disabled={skip === 0 || loading}>
              Назад
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={onNext}
              disabled={skip + limit >= total || loading}
            >
              Вперед
            </Button>
          </div>
          <div className="ui-row">
            <span className="ui-muted">
              пропуск={skip} лимит={limit}
            </span>
            <Select
              aria-label="Размер страницы пациентов"
              value={limit}
              onChange={(event) => onLimitChange(Number(event.target.value))}
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
            </Select>
          </div>
        </div>

        <div className="ui-toolbar">
          <Select
            label="Сортировка"
            aria-label="Сортировка пациентов"
            value={sortBy}
            onChange={(event) =>
              setSortBy(event.target.value as "name" | "birth_date" | "gender" | "status")
            }
          >
            <option value="name">По имени</option>
            <option value="birth_date">По дате рождения</option>
            <option value="gender">По полу</option>
            <option value="status">По статусу</option>
          </Select>
          <Select
            label="Направление"
            aria-label="Направление сортировки пациентов"
            value={sortDir}
            onChange={(event) => setSortDir(event.target.value as "asc" | "desc")}
          >
            <option value="asc">По возрастанию</option>
            <option value="desc">По убыванию</option>
          </Select>
          <div className="ui-toggle-group">
            <label className="ui-toggle">
              <input
                type="checkbox"
                checked={showBirthDate}
                onChange={(event) => setShowBirthDate(event.target.checked)}
              />
              Дата рождения
            </label>
            <label className="ui-toggle">
              <input
                type="checkbox"
                checked={showGender}
                onChange={(event) => setShowGender(event.target.checked)}
              />
              Пол
            </label>
            <label className="ui-toggle">
              <input
                type="checkbox"
                checked={showStatus}
                onChange={(event) => setShowStatus(event.target.checked)}
              />
              Статус
            </label>
          </div>
        </div>

        {patients.length === 0 ? (
          <EmptyState title="Нет данных" description="Попробуйте изменить фильтр поиска." />
        ) : (
          <div className="ui-table-wrap">
            <table className="ui-table">
              <thead>
                <tr>
                  <th>ФИО</th>
                  {showBirthDate && <th>Дата рождения</th>}
                  {showGender && <th>Пол</th>}
                  {showStatus && <th>Статус</th>}
                </tr>
              </thead>
              <tbody>
                {sortedPatients.map((patient) => (
                  <tr key={patient.id}>
                    <td>
                      {patient.last_name} {patient.first_name}
                    </td>
                    {showBirthDate && <td>{patient.birth_date}</td>}
                    {showGender && <td>{patient.gender}</td>}
                    {showStatus && <td>{patient.is_active ? "Активен" : "Неактивен"}</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Card>
  );
}
