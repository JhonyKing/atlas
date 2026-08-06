"use client";

import { ChangeEvent, useState } from "react";

export function PrivateUploadPanel() {
  const [message, setMessage] = useState("Selecciona un archivo privado.");
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
    setMessage(response.ok ? "Archivo validado y puesto a disposición privada." : "Archivo rechazado por seguridad.");
  }
  return <section aria-label="Private upload"><h2>Material privado</h2><input type="file" onChange={upload} /><p role="status">{message}</p></section>;
}
