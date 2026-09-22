# DEMO_SCRIPT — submission video

A short, pre-recorded video for the idea submission, built from the one thing
in this project that actually runs today: the live prototype
([README.md](README.md)). Not a live demo — a screen recording, so takes are
repeatable and nothing depends on a machine behaving on the day.

> This is a **different, earlier-stage script** from
> [EVALUATION.md §8](../drishti-ugv/EVALUATION.md)'s 5-minute Grand Finale
> sequence. That one runs live, on real hardware/sim, once Phase 1–6 have
> actually executed (STATUS.md). This one runs now, on the prototype, and says
> so on camera — see §3 below.

Target length: **2:30–3:00**. Every scene maps to a scenario the prototype
already ships; nothing here needs to be built or scripted new.

---

## 1. How to record it

**Use the browser lab, not the tkinter window.** `drishti_lab.html` is a
single self-contained page — bigger, cleaner on screen, resizable to whatever
resolution you're recording at, and it doesn't depend on `tkinter` being
present on the recording machine.

```bash
cd prototype
python tools/build_page.py --target lab
# open web/drishti_lab.html in a browser, full-window it, then start recording
```

- **Recorder:** OBS Studio (free, Windows/macOS/Linux) or the OS-native one
  (Windows Game Bar `Win+G`, macOS `Cmd+Shift+5`). Capture the browser window,
  not the full screen — keeps the video clean and croppable later.
- **Narration:** record a separate voice track (or narrate live) rather than
  relying on system audio — makes it trivial to re-cut without re-running the
  demo.
- **Determinism matters here more than usual:** every scenario below is
  seeded, so a re-take reproduces pixel-identical runs. If a take goes wrong,
  redo the segment — don't try to fix it by talking over a different run.
- If you'd rather drive from the terminal (e.g. for the headless log output in
  Scene 4), `run_demo.py`'s `--speed` flag controls ms between frames —
  `--speed 90` or so plays slower than the default 60 ms, which gives
  narration room to breathe without editing video speed in post.

---

## 2. The script

### Scene 1 — the problem (0:00–0:20)

**On screen:** title card or the deck's problem-statement slide.

**Say:**
> "BEL's problem statement: drive an unmanned ground vehicle outdoors, point A
> to point B, using cameras — no GPS. The two hard parts are terrain you can't
> just paint as 'blocked', and knowing when to stop trusting your own sensors."

### Scene 2 — the lab, cold open (0:20–0:40)

**On screen:** `drishti_lab.html`, empty canvas, palette visible.

**Say:**
> "This is our live prototype. Three panels: ground truth on the left — what
> the vehicle can't see; belief in the middle — what it's built from what it
> *has* seen; status on the right — what the safety supervisor decided, and
> why."

**Action:** point out the three panels. Don't draw yet.

### Scene 3 — the ditch (0:40–1:30)

**On screen:** load the Hard world (draw or the pre-built scenario), press
**Run**.

**Say:**
> "A ditch is a negative obstacle — nothing sticks up, so an ordinary occupancy
> grid drives straight into it. Watch the belief panel: as the sensor cone
> sweeps the ditch, the cost function reads step height alone — no semantic
> model, no shortcuts — and the plan bends north around it."

**Action:** let the run play to completion. Zoom into the trace log briefly —
this is the "logs" the video needs to show, and it's the real decision trail,
not a caption someone wrote.

**Say (over the log):**
> "Every line here is a real decision with its evidence — this is what a judge
> or a reviewer would be able to audit, not a narrated animation."

### Scene 4 — the frozen camera (1:30–2:20)

**On screen:** restart, same world, trigger the `camera_freeze` fault button
(or `python run_demo.py --fault camera_freeze` in a terminal split, for the
plain-text log version).

**Say:**
> "Now the interesting failure. The camera keeps publishing — fresh
> timestamps, every frame — but the content stops changing. A liveness check
> alone can't see this. We found the gap while building the fault-injection
> harness, closed it, and the supervisor now fingerprints frame content
> directly."

**Action:** let it run to the stop. Point at the exact log line.

**Say:**
> "It stops at exactly 11 seconds — 9 seconds to the fault, plus the 2-second
> detection window — with its own reason code: camera frozen, frames
> unchanging. Not a generic fault. The right sensor, every time."

### Scene 5 — what's real (2:20–2:45)

**On screen:** the prototype README's "What is real and what is not" table, or
just say it on camera over the idle canvas.

**Say:**
> "This is not a lookalike. The cost function and the safety supervisor are
> the actual shipping C++ — we proved it with an 8,000-case parity check, and
> the browser verifies itself against 520 baked decisions on every load. What
> isn't real yet: visual SLAM — the vehicle knows its position here — and the
> physics. That's the next phase, on the simulator and the cloud GPU machine
> we've already specced."

### Scene 6 — close (2:45–3:00)

**On screen:** team slide / contact, or the repository link.

**Say:**
> "The decision logic is built, tested, and provably correct against the
> shipping code. What's left is running it inside the full simulator — which
> is scoped, costed, and ready to start."

---

## 3. Why the video says what it doesn't claim, out loud

CLAUDE.md's rule for this repo is "say what failed, don't round results up."
The honest framing in Scene 5 is not hedging for its own sake — a judge who
has seen a hundred over-claimed SIH demos will trust the ones that name their
own boundary. Don't cut that scene to save ten seconds.

Do **not** narrate this as localisation, SLAM, or a physical run — the
prototype README is explicit that position is known exactly here, and that
claim needs the real RTAB-Map stack and a measured ATE, which doesn't exist
yet (STATUS.md).

---

## 4. Quick reference — commands used above

```bash
python tools/build_page.py --target lab      # build web/drishti_lab.html
python run_demo.py                            # default: --world hard --fault none
python run_demo.py --fault camera_freeze       # Scene 4, plain-text log variant
python run_demo.py --list                      # all worlds/faults, if you want to swap a scene
```
