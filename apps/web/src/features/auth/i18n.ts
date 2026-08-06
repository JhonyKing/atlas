export type AuthLocale = "en-US" | "es-MX";

export const authCopy: Record<AuthLocale, Record<string, string>> = {
  "en-US": {
    title: "Optional sign in",
    email: "Email",
    password: "Password",
    signIn: "Sign in",
    signOut: "Sign out",
    signedIn: "Signed in",
    anonymous: "Anonymous mode remains available.",
    invalid: "Could not authenticate.",
  },
  "es-MX": {
    title: "Inicio de sesión opcional",
    email: "Correo",
    password: "Contraseña",
    signIn: "Iniciar sesión",
    signOut: "Cerrar sesión",
    signedIn: "Sesión iniciada",
    anonymous: "El modo anónimo sigue disponible.",
    invalid: "No se pudo autenticar.",
  },
};
