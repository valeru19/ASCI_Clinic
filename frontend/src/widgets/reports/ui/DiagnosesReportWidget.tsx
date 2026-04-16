import type { DiagnosesStatsItem } from "@/entities/report/model/types";
import { Card, EmptyState } from "@/shared/ui";

type DiagnosesReportWidgetProps = {
  items: DiagnosesStatsItem[];
};

export function DiagnosesReportWidget({ items }: DiagnosesReportWidgetProps) {
  return (
    <Card title="Отчет по диагнозам" subtitle="Топ диагнозов за выбранный период">
      {items.length === 0 ? (
        <EmptyState title="Отчет еще не загружен" description="Выберите период и нажмите загрузить." />
      ) : (
        <div className="ui-table-wrap">
          <table className="ui-table">
            <thead>
              <tr>
                <th>Код МКБ</th>
                <th>Название</th>
                <th>Количество</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.icd10_code}>
                  <td>{item.icd10_code}</td>
                  <td>{item.title}</td>
                  <td>{item.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
