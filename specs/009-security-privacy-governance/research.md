# Research Notes

- Validate SSRF at both hostname and resolved-IP layers; redirects are not trusted implicitly.
- Treat source content as data, never as executable policy or tool authorization.
- Use append-only redacted audit records with irreversible identifiers rather than raw content.
- Keep external security review status separate from local automated test evidence.
