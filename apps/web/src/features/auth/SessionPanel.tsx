"use client";

import { FormEvent, useState } from "react";

import { authCopy, AuthLocale } from "./i18n";

type SessionPanelProps = { locale?: AuthLocale };

export function SessionPanel({ locale = "es-MX" }: SessionPanelProps) {
  const copy = authCopy[locale];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [signedIn, setSignedIn] = useState(false);
  const [message, setMessage] = useState(copy.anonymous);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch("/v1/auth/session", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      setMessage(copy.invalid);
      return;
    }
    setSignedIn(true);
    setMessage(copy.signedIn);
  }

  async function signOut() {
    await fetch("/v1/auth/session", { method: "DELETE", credentials: "include" });
    setSignedIn(false);
    setMessage(copy.anonymous);
  }

  return (
    <section aria-labelledby="auth-title">
      <h2 id="auth-title">{copy.title}</h2>
      {signedIn ? (
        <button type="button" onClick={signOut}>{copy.signOut}</button>
      ) : (
        <form onSubmit={submit}>
          <label>{copy.email}<input value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
          <label>{copy.password}<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
          <button type="submit">{copy.signIn}</button>
        </form>
      )}
      <p aria-live="polite" data-testid="auth-status">{message}</p>
    </section>
  );
}
