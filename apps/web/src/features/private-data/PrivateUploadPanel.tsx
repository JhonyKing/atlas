"use client";

import { ChangeEvent, useState } from "react";

type UploadLocale = "en-US" | "es-MX";

const copy = {
  "en-US": {
    title: "Private material",
    select: "Choose a private file.",
    accepted: "File validated and kept private.",
    rejected: "File rejected by security checks.",
  },
  "es-MX": {
    title: "Material privado",
    select: "Selecciona un archivo privado.",
    accepted: "Archivo validado y puesto a disposición privada.",
    rejected: "Archivo rechazado por seguridad.",
  },
} satisfies Record<UploadLocale, Record<string, string>>;

export function PrivateUploadPanel({ locale = "es-MX" }: { locale?: UploadLocale }) {
  const labels = copy[locale];
  const [message, setMessage] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedFileName(file.name);
    setBusy(true);
    setError(null);
    try {
      const bytes = await file.arrayBuffer();
      const contentBase64 = btoa(String.fromCharCode(...new Uint8Array(bytes)));
      const response = await fetch("/v1/private/uploads", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "Idempotency-Key": crypto.randomUUID() },
        body: JSON.stringify({ filename: file.name, declared_content_type: file.type, content_base64: contentBase64 }),
      });
      if (!response.ok) {
        setMessage(null);
        setError(labels.rejected);
        return;
      }
      setMessage(labels.accepted);
    } catch {
      setMessage(null);
      setError(labels.rejected);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="account-panel" aria-label={locale === "es-MX" ? "Carga privada" : "Private upload"}>
      <h2>{labels.title}</h2>
      <label className="atlas-file-upload" aria-describedby="private-upload-helper">
        <span className="atlas-file-upload-title">{selectedFileName ?? labels.select}</span>
        <span className="atlas-file-upload-control">
          <span className="atlas-file-upload-button">{busy ? (locale === "es-MX" ? "Validando…" : "Validating…") : locale === "es-MX" ? "Elegir archivo" : "Choose file"}</span>
          <span className="atlas-file-upload-name">{selectedFileName ?? (locale === "es-MX" ? "Ningún archivo seleccionado" : "No file selected")}</span>
        </span>
        <span id="private-upload-helper" className="atlas-helper-text">{locale === "es-MX" ? "Los archivos se validan y permanecen asociados a tu cuenta." : "Files are validated and remain associated with your account."}</span>
        <input className="atlas-file-input-hidden" type="file" accept=".pdf,.docx,.txt,.md" disabled={busy} onChange={upload} />
      </label>
      {error ? <p className="account-error" role="alert">{error}</p> : null}
      <p className="account-status" aria-live="polite">{message ?? labels.select}</p>
    </section>
  );
}
