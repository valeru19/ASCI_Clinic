import { type FormEvent, useState } from "react";

import { Button, Input } from "@/shared/ui";

type DiagnosesReportFilterProps = {
  loading: boolean;
  defaultFrom: string;
  defaultTo: string;
  onApply: (dateFrom: string, dateTo: string) => Promise<void>;
};

export function DiagnosesReportFilter({
  loading,
  defaultFrom,
  defaultTo,
  onApply,
}: DiagnosesReportFilterProps) {
  const [dateFrom, setDateFrom] = useState(defaultFrom);
  const [dateTo, setDateTo] = useState(defaultTo);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!dateFrom || !dateTo) {
      setError("Укажите обе даты.");
      return;
    }
    if (dateTo < dateFrom) {
      setError("Дата 'по' должна быть не меньше даты 'с'.");
      return;
    }
    await onApply(dateFrom, dateTo);
  }

  return (
    <form className="ui-form-grid" onSubmit={handleSubmit}>
      <div className="ui-row ui-row--three">
        <Input
          label="С"
          name="report-date-from"
          type="date"
          value={dateFrom}
          onChange={(event) => setDateFrom(event.target.value)}
        />
        <Input
          label="По"
          name="report-date-to"
          type="date"
          value={dateTo}
          onChange={(event) => setDateTo(event.target.value)}
        />
      </div>
      {error && <p className="ui-inline-error">{error}</p>}
      <Button type="submit" variant="secondary" disabled={loading}>
        Загрузить отчет
      </Button>
    </form>
  );
}
