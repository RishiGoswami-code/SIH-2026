# SIH 2026 — Problem Statement 26126

Smart India Hackathon 2026 entry by **Team The Vikings** (SIH 2025 Grand Finale
finalists).

| | |
|---|---|
| Problem Statement ID | 26126 (`SIH26126`) |
| Title | Vision Based Autonomous Navigation for Unmanned Ground Vehicle for Outdoor environment |
| Organisation | Bharat Electronics Limited (BEL) |
| Category | **Software** |
| Theme | Smart Automation |
| Idea submission deadline | **30 September 2026** |

Build an autonomous navigation system for a UGV operating in a **GPS-denied
outdoor environment using camera feeds as the primary sensor** — path
detection, visual localisation, and dynamic collision avoidance.

Our answer is **DRISHTI-UGV**: a ROS 2 module that scores terrain rather than
merely marking it occupied, localises visually without GPS, and puts a small
deterministic safety supervisor — not a neural network — in charge of the stop
decision.

---

## Layout

```
.
├── drishti-ugv/     the project: requirements, spec, backlog, evaluation
├── deck/            SIH idea submission and the generator that builds it
└── source/          upstream source material (blueprint, official template)
```

### `drishti-ugv/` — the project

Start at [drishti-ugv/README.md](drishti-ugv/README.md). Nine documents:
[PRD](drishti-ugv/PRD.md) ·
[SPEC](drishti-ugv/SPEC.md) ·
[SETUP](drishti-ugv/SETUP.md) ·
[TASK](drishti-ugv/TASK.md) ·
[EVALUATION](drishti-ugv/EVALUATION.md) ·
[REFERENCES](drishti-ugv/REFERENCES.md) ·
[STATUS](drishti-ugv/STATUS.md) ·
[CLAUDE](drishti-ugv/CLAUDE.md)

`SPEC.md` is the contract every node is written against. `STATUS.md` is the
handover document — read it to find out where things actually stand.

**No source code yet.** Phase 0 (environment bring-up) is the next action.

### `deck/` — the submission

Six slides on the official SIH 2026 template, generated rather than
hand-edited, so it re-exports cleanly whenever team details change.

```bash
cd deck && python build_deck.py
```

Reads `source/SIH2026-IDEA-Presentation-Format.pptx`, writes
`SIH2026_PS26126_Idea_Presentation.pptx`. Team name and Team ID are constants
at the top of the script.

`prep_logos.py` re-fetches and normalises the technology logos into
`assets/logos/` — only needed to add a logo or refresh a source.

> **The portal accepts PDF only.** Export from PowerPoint after any edit; the
> committed PDF is the upload artefact.

### `source/` — upstream material

The BEL research blueprint (architecture baseline, information cutoff
4 September 2026) and the unmodified official SIH 2026 idea template.

---

## Outstanding

| Item | Blocks |
|---|---|
| **Team ID** from the SIH portal | Title slide of the submission |
| Workstation GPU confirmation against the Isaac Sim floor | Phase 0 simulator choice |
| Upload the PDF to the portal | **Due 30 September 2026** |

Tracked in [drishti-ugv/STATUS.md](drishti-ugv/STATUS.md).

---

## A note on the numbers

Every performance figure in the deck and the docs is a stated engineering
*target* with a defined measurement method, not a claim about what the software
already does — and not a claim of "100% accuracy", which no outdoor autonomy
stack can honestly make. See
[drishti-ugv/EVALUATION.md](drishti-ugv/EVALUATION.md).

Version and licence facts quoted from the blueprint are stamped with their
as-of date and must be re-verified upstream before they are relied on.
