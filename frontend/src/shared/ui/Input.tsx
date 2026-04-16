import { useId } from "react";
import type { InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  error?: string;
};

export function Input({ label, hint, error, id, className, ...rest }: InputProps) {
  const generatedId = useId();
  const inputId = id ?? rest.name ?? generatedId;

  return (
    <label className="ui-field" htmlFor={inputId}>
      {label && <span className="ui-field__label">{label}</span>}
      <input
        id={inputId}
        className={["ui-input", error ? "is-error" : "", className ?? ""].join(" ").trim()}
        {...rest}
      />
      {error ? <span className="ui-field__error">{error}</span> : hint && <span className="ui-field__hint">{hint}</span>}
    </label>
  );
}
