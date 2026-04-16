import { useId } from "react";
import type { SelectHTMLAttributes } from "react";

type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  hint?: string;
  error?: string;
};

export function Select({ label, hint, error, id, className, children, ...rest }: SelectProps) {
  const generatedId = useId();
  const selectId = id ?? rest.name ?? generatedId;

  return (
    <label className="ui-field" htmlFor={selectId}>
      {label && <span className="ui-field__label">{label}</span>}
      <select
        id={selectId}
        className={["ui-select", error ? "is-error" : "", className ?? ""].join(" ").trim()}
        {...rest}
      >
        {children}
      </select>
      {error ? <span className="ui-field__error">{error}</span> : hint && <span className="ui-field__hint">{hint}</span>}
    </label>
  );
}
