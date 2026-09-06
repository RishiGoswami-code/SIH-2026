# DRISHTI-UGV — live prototype

A runnable demonstration of the terrain reasoning and the safety supervisor,
on your machine, with no ROS, no GPU and no install.

```bash
cd prototype
python run_demo.py
```

Python 3.8+ and nothing else. `tkinter` ships with Python; if it is missing,
`--headless` prints the same run to the terminal.

---

## The one thing that matters about this demo

**It runs the real decision logic, not a lookalike.**

The shipping traversability cost function and safety supervisor are C++ and
cannot be imported from Python without ROS, so `drishti_proto/` ports them.
A port is worthless unless it is proven equal, so:

```bash
python tools/check_parity.py
```

builds `tools/parity_oracle.cpp` against the **actual** C++ sources in
`drishti-ugv/ugv_ws/src/`, feeds 8000 input cases through both — including
NaN, infinities and every threshold boundary — and demands identical answers.

```
compared 8000 decisions against the shipping C++ cores
parity: OK
```

It needs a C++ compiler. Without one it exits non-zero and says the logic is
unverified, rather than passing quietly. The semantic taxonomy is not ported at
all: `drishti_perception.taxonomy` is imported directly from the workspace.

---

## What you are looking at

Three panels:

| Panel | Shows |
|---|---|
| **GROUND TRUTH** | the world as it is — the vehicle cannot see this |
| **BELIEF** | traversability cost from what has been observed, computed by the real cost function |
| **STATUS** | what the real supervisor decided this tick, and the evidence |

The gap between the first two panels is the point. Dark grey is unobserved, and
it is **not** free — SPEC.md §6.2 prices it at 0.85, so the planner prefers
ground it has actually seen. Green is cheap, amber expensive, red lethal.

Controls: `space` pause, `s` single step, `r` restart, `q` quit.

---

## Scenarios worth showing

```bash
python run_demo.py --world hard              # T07: the ditch
python run_demo.py --fault camera_freeze     # D19: the frozen camera
python run_demo.py --world medium
python run_demo.py --list
```

### The ditch (`--world hard`)

A ditch is a **negative** obstacle: nothing sticks up, so a conventional
occupancy grid sees free space and drives in. Here it is refused on the step
height alone — 0.55 m against a `step_lethal` of 0.25 m — with no semantic
model involved. Watch the plan bend north through the gap.

Verified, not asserted: `tools/test_demo.py` checks the trajectory never enters
the ditch footprint and never stands on lethal terrain.

### The frozen camera (`--fault camera_freeze`)

The failure a liveness check cannot see. Frames keep arriving with **fresh
timestamps** and unchanging content, so `rgb age` stays near zero while the view
of the world becomes minutes old. `t_camera_stale` never fires.

The supervisor stops at **exactly 11.0 s** — fault at 9.0 s plus the 2.0 s
`t_frame_static` — with reason `camera frozen; frames unchanging`.

This gap was found while building the Phase 5 fault harness, recorded as D18,
and closed by D19. The demo exists partly to make it visible.

### The other faults

| Fault | Stops at | Reason |
|---|---|---|
| `camera_silence` | 9.4 s | camera stale |
| `depth_silence` | 9.4 s | depth stale |
| `slam_loss` | 9.1 s | localisation lost |

Each reports **its own** reason. An earlier version let a camera dropout also
suppress depth, so it reported `depth stale` — the right action for the wrong
reason, which is worse than a wrong action because it sends you debugging the
wrong sensor.

---

## What is real and what is not

**Real, and parity-checked against the shipping C++:**
- the SPEC.md §6.1 traversability cost function, every term and threshold
- the SPEC.md §9 safety supervisor, all nine conditions in evaluation order
- the SPEC.md §5.2 semantic taxonomy, imported rather than copied
- the `/cmd_vel_nav → supervisor → /cmd_vel` seam: only the supervisor's
  output ever moves the vehicle

**Stand-ins, chosen to produce the same *kind* of input as the real thing:**

| Real | Here |
|---|---|
| Gazebo + stereo camera | raycast over a height field |
| `elevation_mapping_cupy` | observed cells with slope, step, roughness |
| Nav2 planner + MPPI | A\* over the cost grid + pure pursuit |
| Nav2 inflation layer | the same idea, 0.40 m inscribed / 1.10 m inflation |

**Not modelled at all — do not claim otherwise:**
- **Visual SLAM.** The vehicle knows exactly where it is. This demonstrates
  terrain reasoning and the safety gate, **not** that GPS-denied localisation
  works. That claim needs the real RTAB-Map stack and ATE measured against
  ground truth.
- Physics, wheel slip, image formation, or a real detector.

If someone asks "is this the real system?", the honest answer is: *the
decisions are, the sensing is not.*

---

## Files

```
prototype/
├── run_demo.py                  entry point
├── drishti_proto/
│   ├── supervisor.py            port of drishti_safety::SupervisorCore
│   ├── traversability.py        port of TraversabilityCore
│   ├── world.py                 height field + semantics; mirrors the SDF worlds
│   ├── sim.py                   sense → cost → plan → supervise → move
│   ├── planner.py               A* over cost, pure pursuit, inflation
│   └── gui.py                   tkinter view
└── tools/
    ├── parity_oracle.cpp        emits the C++ answers
    ├── check_parity.py          proves the ports match  (8000 cases)
    └── test_demo.py             pins what the demo claims  (43 checks)
```

## Tests

```bash
python tools/check_parity.py     # ports match the shipping C++
python tools/test_demo.py        # the demo still demonstrates what it claims
```

`test_demo.py` pins the claims: every world is solvable, the ditch is gone
around and not across, no run ever stands on lethal terrain, each fault reports
its own reason, unobserved space starts expensive, A\* treats lethal as a
constraint rather than a high price, and runs are deterministic.

## Performance

About 3–4 ms per simulated step, so the live view runs comfortably faster than
real time. An earlier version re-evaluated the terrain cost for every cell in
the sensor cone on every tick — 2,200 evaluations per step, nearly all of them
recomputing a known answer. Caching observed cells took a full run from 16.8 s
to 0.8 s.
