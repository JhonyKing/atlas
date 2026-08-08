"use client";

import { FormEvent, useState } from "react";

import { authCopy, AuthLocale } from "./i18n";

type SessionPanelProps = { locale?: AuthLocale };

export function SessionPanel({ locale = "es-MX" }: SessionPanelProps) {
  const copy = authCopy[locale];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [signedIn, setSignedIn] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch("/v1/auth/session", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      setMessage(copy.invalid ?? "Could not authenticate.");
      return;
    }
    setSignedIn(true);
    setMessage(copy.signedIn ?? "Signed in");
  }

  async function signOut() {
    await fetch("/v1/auth/session", { method: "DELETE", credentials: "include" });
    setSignedIn(false);
    setMessage(copy.anonymous ?? "Anonymous mode remains available.");
  }

  return (
    <section className="account-panel account-session-panel" aria-labelledby="auth-title">
      <h2 id="auth-title">{copy.title}</h2>
      {signedIn ? (
        <button type="button" onClick={signOut}>{copy.signOut}</button>
      ) : (
        <form className="account-form" onSubmit={submit}>
          <label className="account-field">{copy.email}<input value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
          <label className="account-field">{copy.password}<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
          <button type="submit">{copy.signIn}</button>
        </form>
      )}
      <p aria-live="polite" data-testid="auth-status">{message ?? copy.anonymous}</p>
    </section>
  );
}
