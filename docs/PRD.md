# HoneyDesk — Product Requirements Document (PRD)

| Field | Value |
|-------|-------|
| **Product** | HoneyDesk |
| **Event** | STEMist Hacks IV (Jul 31 – Aug 2, 2026) |
| **Tracks** | Best Security Hack · Best AI/LLM Hack · Best Overall |
| **Version** | 1.0 MVP |
| **Status** | Ready for build |
| **Last updated** | 2026-08-02 |

---

## 1. Vision

HoneyDesk is a **student-threat deception platform**: fake student surfaces (portal login, scholarship form, Discord verify flow) that trap scam/phishing behavior, classify the attack in real time, and generate a plain-English brief any teenager can act on — plus an export schools can share with IT.

> One-liner for judges: *Trap the scammer. Teach the student. Brief the school.*

---

## 2. Problem Statement

Students are not primarily attacked by Hollywood APTs. They are hit by:

- Fake school / Canvas / Google logins (credential harvest)
- “You’ve been selected” scholarship / aid forms (PII + urgency scams)
- Discord “verify to keep access” bots (token / account theft)
- Typosquat lookalike domains
- Fake internship / job offers

Passive tools (“paste a link, get a score”) help, but they don’t show **attacker behavior**. Attackers already build fake student portals — HoneyDesk builds them **on purpose for defense**, captures the full interaction, and turns it into education + actionable intel.

**Thesis:** The memorable security hack for STEMist IV is not another phishing classifier chat UI — it is a **live honeypot that springs in front of the judge**, with AI explaining what just happened.

---

## 3. Goals & Non-Goals

### 3.1 Goals (MVP)

| ID | Goal | Success signal |
|----|------|----------------|
| G1 | Demo a visceral trap spring in ≤90 seconds | Judge (or presenter) submits to decoy → dashboard lights up |
| G2 | Classify attacks into clear technique tags | ≥3 techniques labeled correctly on seeded scenarios |
| G3 | AI generates a victim-ready brief | 1-paragraph “what happened + what to do” per event |
| G4 | Make analysis pipeline visible | Judges can name Capture → Classify → Enrich → Brief |
| G5 | Demo never depends on random internet attackers | 3 one-click replay scenarios + simulate button |
| G6 | Ship stable deploy + 3–5 min video | Happy path succeeds 5/5 dry runs |

### 3.2 Non-Goals (out of MVP)

- Production-grade OPSEC / anti-fingerprinting (Cowrie-level disguise)
- Real SSH/Telnet honeypots
- Training a custom ML model from scratch on large datasets
- Phishing real people or unsolicited Discord spam
- Multi-tenant school SSO / admin orgs
- Storing real user passwords in plaintext
- Mobile native apps
- Full SOC replacement / SIEM

---

## 4. Target Users

| Persona | Need | Role in product |
|---------|------|-----------------|
| **Primary: Student (13–19)** | Understand scams targeting them | Victim brief consumer; demo actor |
| **Secondary: School IT / club blue-team** | Shareable incident summary | STIX / IT brief consumer |
| **Tertiary: Hackathon judge** | Instant wow + clear security value | Demo audience |
| **Operator (team during event)** | Watch traps, replay attacks | Dashboard user |

STEMist eligibility: ages 13–19. All copy must be age-appropriate and educational.

---

## 5. Product Principles

1. **Theater with integrity** — Demo is dramatic; ethics are explicit (authorized deception / training only).
2. **Fail closed on secrets** — Never display or persist raw passwords; store flags/hashes/redactions.
3. **Explain, don’t just alert** — Every catch produces a human brief.
4. **Seeded reliability** — Live traffic is a bonus; replay is the contract.
5. **One spring moment** — Link → decoy → dashboard detonation → brief. Everything else supports that.
6. **Blue-team framing** — We are not shipping a phishing kit; we are shipping a defense classroom.

---

## 6. User Stories

### 6.1 Must-have (P0)

| ID | As a… | I want to… | So that… | Acceptance |
|----|-------|------------|----------|------------|
| US-01 | Operator | Open a live dashboard | I see attacks as they happen | Feed updates within 2s of capture |
| US-02 | Demo presenter | Open a fake student portal decoy | Judges experience a real-looking trap | Decoy looks credible at a glance |
| US-03 | Demo presenter | Submit fake credentials on the decoy | An event is captured | Event appears with technique tag |
| US-04 | Operator | See technique classification | I know what kind of scam it is | Tag from controlled enum |
| US-05 | Student | Read a plain-English brief | I know what happened and what to do | Brief ≤120 words, actionable |
| US-06 | Operator | Replay 3 seeded scenarios | Demo never fails | One-click replay each scenario |
| US-07 | Judge/viewer | Watch analysis steps stream | I trust it’s multi-step AI, not one prompt | Pipeline panel shows steps |
| US-08 | Operator | See aggregate “attacks caught” | Impact feels real | Counter + simple breakdown |
| US-09 | School IT (persona) | Export incident as structured intel | I can share with others | JSON download (STIX-shaped) |
| US-10 | Builder | Ensure ethics are visible | Project isn’t misread as malware | Ethics note in UI + README |

### 6.2 Should-have (P1)

| ID | Story | Acceptance |
|----|-------|------------|
| US-11 | Scholarship / aid form decoy | Separate technique: urgency/PII scam |
| US-12 | Attack map (geo) | Map updates on events (demo geo OK if noted) |
| US-13 | Leaderboard of attacks / scenarios | Gamified strip on dashboard |
| US-14 | Discord verify decoy (or simulated) | Third technique path in demo |
| US-15 | “What they tried to steal” panel | Sponsor-aligned privacy beat |
| US-16 | IT-flavored brief (more technical) | Toggle Victim / IT brief |

### 6.3 Nice-to-have (P2)

| ID | Story |
|----|-------|
| US-17 | Typosquat teaching landing page |
| US-18 | AbuseIPDB / external enrichment |
| US-19 | MITRE ATT&CK mapping chips |
| US-20 | Discord bot live (not simulated) |
| US-21 | PDF one-pager export of brief |

---

## 7. Core User Flows

### 7.1 Happy path — Trap spring (demo)

```
1. Presenter opens Ops Dashboard (live)
2. Presenter sends / opens decoy link (fake aid or portal)
3. Actor submits synthetic credentials / form fields
4. Capture API records event (redacted)
5. Pipeline: Capture → Classify → Enrich → Brief
6. Dashboard: row highlights, technique tag, severity
7. Detail drawer: AI victim brief + “data they tried to steal”
8. Optional: Export STIX/JSON → “Share with school IT”
```

### 7.2 Replay path (reliability)

```
1. Operator clicks “Replay: Credential Harvest”
2. System injects a prebuilt event timeline via same pipeline
3. Dashboard behaves identically to live capture
4. Brief regenerates or loads cached brief for speed
```

### 7.3 Multi-scenario path

```
1. Replay scholarship PII scam
2. Replay Discord verify scam
3. Show technique breakdown chart + weekend counter
```

### 7.4 Ethics / misuse path

```
1. User tries to use decoys to phish real targets
2. Product copy + README forbid this
3. Decoys hosted under clearly project-controlled domains
4. No bulk mailer / target importer features exist (by design)
```

---

## 8. Functional Requirements

### 8.1 Decoys

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Fake student portal login page (email + password) | P0 |
| FR-02 | On submit: do not authenticate anyone; capture event; show benign “Verification failed / try later” or educational interstitial | P0 |
| FR-03 | Scholarship / financial aid confirmation form decoy | P1 |
| FR-04 | Discord-style “Verify” landing or bot simulation | P1 |
| FR-05 | Decoys parameterized by `decoy_id` and campaign label | P0 |
| FR-06 | Admin/ops UI clearly labels surfaces as honeypots | P0 |

### 8.2 Capture

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10 | Capture timestamp, decoy_id, IP, user-agent, path | P0 |
| FR-11 | Capture which fields were filled (names only) + password_entered boolean | P0 |
| FR-12 | Never store plaintext passwords; hash or discard | P0 |
| FR-13 | Capture timing metrics (ms on page / submit speed) when available | P1 |
| FR-14 | Accept simulated events from trusted simulate endpoint | P0 |

### 8.3 Classification

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-20 | Assign technique from enum: `credential_harvest`, `urgency_pii_scam`, `social_verify`, `typosquat`, `bot_probe`, `unknown` | P0 |
| FR-21 | Assign severity: `low` \| `medium` \| `high` \| `critical` | P0 |
| FR-22 | Hybrid scoring: deterministic rules first, optional model/LLM assist | P0 |
| FR-23 | Explainability: top reasons listed for the label | P0 |
| FR-24 | Classification latency target ≤100ms for rules path | P0 |

### 8.4 AI briefing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-30 | Generate victim brief (what happened, why risky, 2–3 actions) | P0 |
| FR-31 | Stream or step-announce Brief agent in pipeline UI | P0 |
| FR-32 | Optional IT brief with more technical language | P1 |
| FR-33 | Cache briefs for seeded scenarios for demo failover | P0 |
| FR-34 | Age-appropriate tone; no fearmongering gore | P0 |

### 8.5 Dashboard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-40 | Live event feed | P0 |
| FR-41 | Event detail drawer: timeline, technique, reasons, brief | P0 |
| FR-42 | Visible pipeline steps per event | P0 |
| FR-43 | Attacks-caught counter + technique breakdown | P0 |
| FR-44 | One-click replay for 3 scenarios | P0 |
| FR-45 | Attack map | P1 |
| FR-46 | Leaderboard | P1 |
| FR-47 | “Data targeted” panel (email, password, SSN-field, etc.) | P1 |

### 8.6 Export & sharing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-50 | Export event/intel as STIX 2.1-shaped JSON bundle (best-effort MVP) | P0 |
| FR-51 | Include indicator (IP/UA pattern), attack pattern note, description | P0 |
| FR-52 | Download button labeled “Share with school IT” | P0 |

### 8.7 Demo & education

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-60 | Seeded scenario pack (3) with stable IDs | P0 |
| FR-61 | Simulate-attack control on dashboard | P0 |
| FR-62 | Ethics / authorized-use notice on dashboard and README | P0 |
| FR-63 | Compare strip: “Raw event JSON” vs “AI brief” | P1 |

---

## 9. Seeded Scenarios (Product Spec)

| ID | Name | Decoy | Technique | Brief punchline |
|----|------|-------|-----------|-----------------|
| SC-1 | Aid Portal Login | Student portal | `credential_harvest` | They wanted your school password to take over email/identity |
| SC-2 | Scholarship Confirm | Aid form | `urgency_pii_scam` | Real aid doesn’t demand bank/SSN via random links |
| SC-3 | Discord Verify | Verify landing | `social_verify` | “Verify” bots steal accounts/tokens, not Nitro |

Each scenario must be replayable without external network attackers.

---

## 10. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-01 | Latency | Event visible on dashboard ≤2s after decoy submit |
| NFR-02 | Reliability | Replay paths succeed 5/5 before recording video |
| NFR-03 | Privacy | No plaintext secrets persisted; redact in UI |
| NFR-04 | Safety | No tooling for mass messaging / target lists |
| NFR-05 | Age safety | Content appropriate for 13–19 |
| NFR-06 | Cost | Cache scenario briefs; prefer small/fast LLM |
| NFR-07 | Availability | Public decoy + dashboard URLs for judges |
| NFR-08 | Observability | Structured logs of pipeline steps (no secrets) |

---

## 11. Competitive Differentiation

| Alternative | Gap | HoneyDesk |
|-------------|-----|-----------|
| Link scanners / ChatGPT “is this phishing?” | Passive, no trap theater | Live decoy + capture |
| Cyfer Trace-style SSH honeypots | Infra-focused, less teen-relatable | Student surfaces |
| JobShield-style paste detectors | No active deception | Honeypot + ops desk |
| STEMist III security-ish apps | Rarely deception platforms | Novel for this event |

---

## 12. Demo Script (Product Spec)

**Duration:** ~90 seconds core.

| Time | On screen | Spoken |
|------|-----------|--------|
| 0:00 | Problem slide / title | Students get scholarship and portal scams, not movie hackers |
| 0:10 | Send/open decoy link | Here’s a link a student might trust |
| 0:20 | Decoy page | Looks like aid verification |
| 0:30 | Submit synthetic creds | Watch what happens when it springs |
| 0:35 | Dashboard detonation | IP, technique, severity |
| 0:50 | Pipeline animation | Capture → Classify → Enrich → Brief |
| 1:00 | Victim brief | Plain English + actions |
| 1:15 | Counter + map/leaderboard | Attacks caught this weekend |
| 1:25 | STIX export click | Share with school IT |

**Backup:** If live submit fails, hit Replay SC-1 immediately (same visuals).

---

## 13. Metrics (Judge-Facing)

| Metric | MVP target |
|--------|------------|
| Time-to-dashboard | ≤2s |
| Rules classify seeded scenarios | 3/3 correct technique |
| Brief generation success | 100% on seeded (cached failover OK) |
| Replay reliability | 5/5 dry runs |
| Secrets in DB/UI | 0 plaintext passwords |

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No real attackers during judging | Dead demo | Replay + simulate |
| Project read as phishing kit | Ethics / DQ risk | Framing, no spam tools, notices |
| Thin AI accusation | Lose AI track | Multi-agent pipeline UI + structured briefs |
| Scope to full honeypot stack | Incomplete | HTTP decoys only |
| Ugly decoy breaks immersion | Weak wow | One highly polished P0 decoy |
| LLM outage | No brief | Cached briefs for SC-1..3 |

---

## 15. Track Mapping

| Track | How HoneyDesk scores |
|-------|----------------------|
| **Best Security** | Deception, capture, classification, export — TryHackMe-aligned |
| **Best AI/LLM** | Multi-step analyst agents, streaming briefs, explainability |
| **Best Overall** | Novel for STEMist, visceral demo, clear impact story |

Judging criteria:

| Criterion | Product answer |
|-----------|----------------|
| Originality | Student-threat honeypot + AI brief, not another chatbot |
| Effort | Decoys + pipeline + dashboard + export + seeded pack |
| Impact | Real student scam problem; school-shareable output |
| Project Condition | Replay-hardened demo path |

---

## 16. Sponsor Alignment

| Sponsor angle | Product hook |
|---------------|--------------|
| TryHackMe | Blue-team room vibe: trap fired, analyze, brief |
| NordVPN / NordPass / Incogni | “Here’s what they tried to steal / expose” |
| Tavily | Optional enrichment of lookalike/scam patterns |
| Render | Host decoys, API, dashboard (Workflows if useful) |

---

## 17. Release Scope

### P0 — Must ship

- Portal login decoy
- Capture API with redaction
- Classifier (rules + technique tags)
- LLM victim brief + pipeline UI
- Ops dashboard (feed, detail, counter)
- 3 replay scenarios + simulate
- STIX-shaped JSON export
- Ethics copy + README
- Deploy + video

### P1 — If P0 solid

- Scholarship form decoy
- Discord verify path
- Map + leaderboard
- Data-targeted panel
- IT brief toggle

### P2 — Only if ahead

- Typosquat page
- External intel enrichment
- ATT&CK chips
- PDF export

---

## 18. Open Questions (resolve in first build hour)

1. Public decoy hostname strategy (Render subdomain vs custom)?
2. Single polished decoy first (portal) vs portal+scholarship in parallel?
3. LLM provider key availability?
4. Team roles: decoys / API / dashboard / briefs?
5. Record video from deployed URL or localhost + backup?

**Defaults:** Render subdomains; portal first; OpenAI-compatible API; video from deployed URL with replay backup.

---

## 19. Success Definition

HoneyDesk succeeds at STEMist Hacks IV if:

1. Judges remember the trap spring and can retell it.
2. Seeded scenarios classify correctly and produce briefs.
3. Security + AI narratives are both obvious without apologizing.
4. Ethics framing is clear and credible.
5. Submission is competitive for Security first, Overall/AI second.

---

## 20. Glossary

| Term | Meaning |
|------|---------|
| **Decoy** | Fake student-facing surface designed to attract scam behavior |
| **Trap spring** | Moment a submission generates a visible ops alert |
| **Technique tag** | Controlled label for attack type |
| **Victim brief** | Plain-English explanation + actions |
| **Replay** | Injected scenario using the real pipeline |
| **STIX-shaped** | JSON approximating STIX 2.1 objects for sharing |
| **Redaction** | Secrets not stored/shown in usable plaintext |
