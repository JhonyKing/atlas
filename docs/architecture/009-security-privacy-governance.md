# Architecture — security, privacy, and governance

Security controls are layered at the boundary: `SafeFetcher` validates HTTPS allowlists, every
redirect and resolved IP; `atlas.security` treats source text as inert and exposes only allowlisted
actions; `atlas.privacy` owns consent, ownership, redaction and deletion semantics; CI runs the
security suite and a frontend secret scan.

Private data remains tenant-scoped and cannot be promoted without a tenant boundary. Audit and trace
metadata are content-free. External review is tracked separately so automated local tests are not
misrepresented as a production security certification.
