import { type FormEvent, useState } from "react";

import type { Gender, PatientCreatePayload } from "@/entities/patient/model/types";
import { Button, Input, Select } from "@/shared/ui";

type CreatePatientFormProps = {
  loading: boolean;
  onCreate: (payload: PatientCreatePayload) => Promise<void>;
};

export function CreatePatientForm({ loading, onCreate }: CreatePatientFormProps) {
  const [lastName, setLastName] = useState("Петров");
  const [firstName, setFirstName] = useState("Илья");
  const [birthDate, setBirthDate] = useState("1995-05-15");
  const [gender, setGender] = useState<Gender>("M");
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!lastName.trim() || !firstName.trim() || !birthDate) {
      setError("Заполните обязательные поля.");
      return;
    }
    await onCreate({
      last_name: lastName.trim(),
      first_name: firstName.trim(),
      birth_date: birthDate,
      gender,
    });
  }

  return (
    <form className="ui-form-grid" onSubmit={handleSubmit}>
      <Input
        label="Фамилия"
        name="patient-last-name"
        value={lastName}
        onChange={(event) => setLastName(event.target.value)}
        error={error}
      />
      <Input
        label="Имя"
        name="patient-first-name"
        value={firstName}
        onChange={(event) => setFirstName(event.target.value)}
      />
      <Input
        label="Дата рождения"
        type="date"
        name="patient-birth-date"
        value={birthDate}
        onChange={(event) => setBirthDate(event.target.value)}
      />
      <Select
        label="Пол"
        name="patient-gender"
        value={gender}
        onChange={(event) => setGender(event.target.value as Gender)}
      >
        <option value="M">M</option>
        <option value="F">F</option>
        <option value="O">O</option>
      </Select>
      <Button type="submit" disabled={loading}>
        Создать пациента
      </Button>
    </form>
  );
}
