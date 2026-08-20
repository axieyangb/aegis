# Aegis Roadmap

**Updated:** 2026-08-20

Three sections: what exists, what makes it sellable, what makes it defensible.
Dates are deliberately absent below the first section — a roadmap with dates on
unstarted work is a wish list.

> The previous version of this file listed a container manager, a Docker
> registry, an embedded DNS server and AI-driven deployment orchestration as
> future phases. All four shipped. It is rewritten rather than amended, because
> a roadmap that describes shipped features as upcoming is worse than no
> roadmap.

---

## Built

Available today and running on a live nine-node fleet.

**Fleet** — one-line enrolment, per-node mTLS identity from the hub's own CA,
digest-verified agent upgrades with systemd auto-rollback, idempotent repair,
activity log.

**Networking** — WireGuard overlay mesh, STUN NAT traversal, automatic
LAN-direct routing with mesh fallback, embedded fleet DNS covering hosts and
bridge containers.

**Gateway** — Envoy with a full xDS control plane, SDS certificate management,
automated TLS issuance, staged pending→apply configuration, rate limiting,
maintenance pages, one-click Expose.

**Bare metal** — Redfish/BMC power control, UEFI HTTP Boot with no L2 adjacency
required, serial console, libvirt/KVM provisioning with cloud-init.

**Kubernetes** — create, scale, upgrade, back up, restore and tear down via a
reconciler, on k3s or kubeadm. Air-gapped installs validated live on a 5-node HA
cluster.

**Models and data** — catalogue with versions, digests, lineage and per-owner
quotas; HuggingFace and URL ingest; LAN staging so the hub egresses once;
pluggable storage backends (local, mounted share, cloud bucket) switchable at
runtime; reference-only artifacts that catalogue without copying.

**Workloads** — GPU-aware scheduling, managed volumes, notebooks, serving,
promote-to-catalogue.

**AI operations** — Owl acting through risk-classified tools with
prompt-injection defences; AI threat analysis over gateway access logs.

---

## Next — what makes it sellable

The gap between "impressive" and "a customer can run this without us".

**Multi-user, roles and service accounts.** Today there is one operator account
and `authenticated` means `admin` everywhere. Ownership already threads through
the data model — artifacts, workloads and projects all carry an owner, and
quotas are per-owner — so this is adding an identity layer on top of existing
scoping rather than retrofitting ownership. This is the single largest gap.

**Training as a managed workload.** The GPU scheduler, artifact capture, managed
volumes and result promotion all exist; training is simply not modelled as a
workload yet, so a run is still started by hand and observed with `tail -f`. The
defining workload of an AI platform should not be the one the platform cannot
see.

**Control-plane backup and documented recovery.** Cluster backup and restore
exist. The hub's own state does not have an equivalent a customer could follow.

**Audit trail.** Node lifecycle is recorded; a general who-did-what across
Depot, clusters, gateway and secrets is not.

**A quickstart a stranger can complete.** If we have to install it, it is a
service rather than a product.

---

## Then — what makes it defensible

**Control-plane high availability.** One hub and one database today. Workloads
survive a hub outage; management does not.

**Serving as a product surface** — autoscaling, canary rollouts, token metering.
Serving works; it is not yet something you sell by the seat.

**Experiment tracking and lineage** across runs, so results are comparable
rather than merely stored.

**Supply chain** — signed artifacts, SBOM, dependency CVE scanning.

**Scale validation** well beyond a single site. Nine nodes is what we have
tested, and it is the number we quote.

---

## Deliberately not doing yet

- **Multi-region / federation.** One site per hub until one site is excellent.
- **A custom scheduler beyond GPU awareness.** Kubernetes exists; we orchestrate
  it rather than replace it.
- **Billing and metering.** Not until someone is billed.
- **A Windows agent.** Linux edge is the market.

---

Questions about any of this are welcome at
[aegis.jerxie.com](https://aegis.jerxie.com), where an assistant answers from
this documentation — including the parts about what is missing.
