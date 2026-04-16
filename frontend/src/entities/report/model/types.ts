export type DiagnosesStatsItem = {
  icd10_code: string;
  title: string;
  total: number;
};

export type DiagnosesStatsResponse = {
  date_from: string;
  date_to: string;
  items: DiagnosesStatsItem[];
};
