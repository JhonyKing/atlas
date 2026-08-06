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
  const [message, setMessage] = useState(labels.select);
  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const bytes = await file.arrayBuffer();
    const contentBase64 = btoa(String.fromCharCode(...new Uint8Array(bytes)));
    const response = await fetch("/v1/private/uploads", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify({ filename: file.name, declared_content_type: file.type, content_base64: contentBase64 }),
    });
    setMessage(response.ok ? labels.accepted : labels.rejected);
  }
  return <section aria-label="Private upload"><h2>{labels.title}</h2><input type="file" onChange={upload} /><p aria-live="polite">{message}</p></section>;
}
