import type {
  ButtonHTMLAttributes,
  InputHTMLAttributes,
  LabelHTMLAttributes,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from "react";

export function Button({
  children,
  variant = "primary",
  loading = false,
  className,
  disabled,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "tertiary" | "danger";
  loading?: boolean;
}) {
  return (
    <button
      {...props}
      className={["atlas-button", `atlas-button-${variant}`, className].filter(Boolean).join(" ")}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
    >
      {loading ? <span className="atlas-button-spinner" aria-hidden="true" /> : null}
      {children}
    </button>
  );
}

export function Label({ children, className, ...props }: LabelHTMLAttributes<HTMLLabelElement>) {
  return <label {...props} className={["atlas-label", className].filter(Boolean).join(" ")}>{children}</label>;
}

export function HelperText({ children, id }: { children: ReactNode; id?: string }) {
  return <p className="atlas-helper-text" id={id}>{children}</p>;
}

export function ErrorMessage({ children, id }: { children: ReactNode; id?: string }) {
  return <p className="atlas-error-message" id={id} role="alert">{children}</p>;
}

export function Field({
  id,
  label,
  helper,
  error,
  children,
}: {
  id: string;
  label: ReactNode;
  helper?: ReactNode;
  error?: ReactNode;
  children: ReactNode;
}) {
  const describedBy = [helper ? `${id}-helper` : null, error ? `${id}-error` : null].filter(Boolean).join(" ") || undefined;
  return (
    <div className="atlas-field" data-field={id}>
      <Label htmlFor={id}>{label}</Label>
      <div aria-describedby={describedBy}>{children}</div>
      {helper ? <HelperText id={`${id}-helper`}>{helper}</HelperText> : null}
      {error ? <ErrorMessage id={`${id}-error`}>{error}</ErrorMessage> : null}
    </div>
  );
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={["atlas-input", props.className].filter(Boolean).join(" ")} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={["atlas-textarea", props.className].filter(Boolean).join(" ")} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={["atlas-select", props.className].filter(Boolean).join(" ")} />;
}

export function Checkbox({ label, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: ReactNode }) {
  return <label className="atlas-checkbox"><input {...props} type="checkbox" /> <span>{label}</span></label>;
}

export function FileUpload({ label, helper, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: ReactNode; helper?: ReactNode }) {
  return (
    <label className="atlas-file-upload">
      <span className="atlas-label">{label}</span>
      <input {...props} type="file" />
      {helper ? <span className="atlas-helper-text">{helper}</span> : null}
    </label>
  );
}
