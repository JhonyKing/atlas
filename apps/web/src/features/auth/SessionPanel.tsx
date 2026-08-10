"use client";

import { FormEvent, useState } from "react";

import { authCopy, AuthLocale } from "./i18n";
import { Button, Field, Input } from "@/components/forms";

type SessionPanelProps = { locale?: AuthLocale };

export function SessionPanel({ locale = "es-MX" }: SessionPanelProps) {
  const copy = authCopy[locale];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [signedIn, setSignedIn] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const response = await fetch("/v1/auth/session", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        setError(copy.invalid ?? "Could not authenticate.");
        return;
      }
      setSignedIn(true);
      setMessage(copy.signedIn ?? "Signed in");
    } catch {
      setError(copy.invalid ?? "Could not authenticate.");
    } finally {
      setBusy(false);
    }
  }

  async function signOut() {
    setBusy(true);
    setError(null);
    try {
      await fetch("/v1/auth/session", { method: "DELETE", credentials: "include" });
      setSignedIn(false);
      setMessage(copy.anonymous ?? "Anonymous mode remains available.");
    } catch {
      setError(copy.invalid ?? "Could not authenticate.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="account-panel account-session-panel" aria-labelledby="auth-title">
      <h2 id="auth-title">{copy.title}</h2>
      {signedIn ? (
        <div className="account-authenticated-state"><p className="account-state-label">{copy.signedIn}</p><Button type="button" variant="secondary" loading={busy} onClick={signOut}>{copy.signOut}</Button></div>
      ) : (
        <form className="account-form" onSubmit={submit}>
          <Field id="account-email" label={copy.email} helper={locale === "es-MX" ? "Usa el correo asociado a tu cuenta." : "Use the email associated with your account."}>
            <Input id="account-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required />
          </Field>
          <Field id="account-password" label={copy.password}>
            <Input id="account-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
          </Field>
          <Button type="submit" loading={busy}>{copy.signIn}</Button>
        </form>
      )}
      {error ? <p className="account-error" role="alert">{error}</p> : null}
      <p className="account-status" aria-live="polite" data-testid="auth-status">{message ?? copy.anonymous}</p>
    </section>
  );
}
