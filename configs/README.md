# Example Configurations

This directory contains example Aegis database snapshots that can be imported via **Gateway → Import**.

> **Note**: On first boot, Aegis automatically seeds a working baseline configuration — an HTTP listener (port 10080), HTTPS listener (port 10443), and the `acme-renewer` cluster. You do not need to import any file to get started.

These snapshots are useful when you need a non-standard starting point or want to replicate a specific topology.

## After importing

1. **Add your TLS certificates** — Certificates → issue via ACME or Local CA
2. **Update filter chains** — edit `https_listener` to add your domain's SNI match, cluster, and TLS secret
3. **Point clusters at your services** — add clusters for each upstream service

## Secrets are not included

TLS private keys are never exported or committed to source control. Add them via the Certificates page after importing.
