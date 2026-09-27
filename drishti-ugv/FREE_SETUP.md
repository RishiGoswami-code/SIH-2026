# FREE_SETUP — end to end, with no money and no billing risk

For when [CLOUD_SETUP.md](CLOUD_SETUP.md)'s AWS path isn't an option because
there's no budget to put behind it. AWS "free tier" still requires a card on
file and can genuinely bill you on a mistake (wrong instance type, forgetting
to terminate, data transfer overage) — that's real risk against a real
constraint, so this document doesn't use it at all.

> **!! UNVERIFIED !!** Nothing below has been executed. It's built from
> reading the actual repo (launch files, message definitions, the existing
> `docker/Dockerfile`), not from running any of it — consistent with every
> other UNVERIFIED banner in this project. Expect the first attempt to fail
> and need iteration; that is the plan working as intended, not a sign
> something is wrong.
>
> As of **27 September 2026**. Submission deadline: **30 September 2026** —
> **3 days.** Nothing in this repo has been built or run anywhere yet. Scope
> is triaged hard below because of that, not because of ambition.

---

## 1. The idea that makes this tractable

Only **one** part of this stack genuinely needs a GPU: `elevation_mapping_cupy`
(Phase 3), because CuPy is CUDA. Nav2, RTAB-Map (CPU/ORB features), the safety
supervisor, and perception on CPU all run without one — slower per frame,
which doesn't matter for a short demo mission.

That splits the problem in two, with very different platforms for each half:

| Need | Platform | Cost | Billing risk |
|---|---|---|---|
| Everything except Phase 3 | **GitHub Codespaces / Actions** | Free (see §2) | None — no card needed for the free quota |
| The one CUDA-specific check (Phase 3) | **Kaggle Notebooks**, T4, via RoboStack | Free, 30 GPU-hrs/week | None — no card at all; it just cuts you off at quota, it cannot bill you |

---

## 2. Why GitHub, and why it's actually zero risk

- A **public** repo gets unlimited free Actions minutes. A **private** repo
  gets 2,000 free minutes/month (~33 hours) on the same no-card basis — it
  stops running when exhausted; it does not bill you unless you've explicitly
  added a payment method **and** raised the spending limit above $0. Check
  that no payment method is on file if you want a hard guarantee.
- GitHub's `ubuntu-24.04` hosted runner (and the Codespaces devcontainer
  below, pinned to the same image) is **the one Linux version ROS 2 Jazzy
  actually ships binaries for**. This is the single biggest bug the earlier
  Kaggle-based `ALTERNATIVE.md` had — it assumed Jazzy installs cleanly on
  Ubuntu 22.04, which it doesn't. Using the matching OS here means the apt
  commands below are the same ones the project's own `docker/Dockerfile`
  already uses correctly, not new guesses.
- **Codespaces** gives an interactive shell in that same environment for the
  messy first pass — actually debugging the `rclcpp` API fixes STATUS.md
  already expects, which is much harder blind in batch CI logs. Once
  something builds clean there, the Actions workflow repeats it for free,
  every push, with logs saved as downloadable artifacts.

Files already in the repo for this:

```
.devcontainer/devcontainer.json          Codespaces: Ubuntu 24.04, no GPU
.devcontainer/setup.sh                   installs ROS 2 Jazzy + Gazebo Harmonic
                                          bridge + Nav2 + RTAB-Map (no CUDA/CuPy)
.github/workflows/free-tier-verify.yml   the same steps, as CI, on every push
```

---

## 3. A finding that changes the plan: Phase 1 needs a stub

Reading `bringup.launch.py` closely turned up something worth knowing before
you spend an hour confused by it: **Phase 4 perception is not wired into it
at all** yet (the launch file's own comment says so), and the safety
supervisor's rule is that *no* `/perception/health` ever arriving is itself a
stop condition (CLAUDE.md rule 2 — "loss of input is a stop condition").
Without something publishing on that topic, Nav2 can plan all it wants; the
supervisor still holds `/cmd_vel` at zero forever, and nothing moves.

`ugv_ws/tools/phase1_stub_perception_health.py` is a small, clearly-labeled
test-only node that publishes a constantly-healthy `PerceptionHealth` so
Phase 1 (Nav2 actually reaching a goal) can be exercised before Phase 4
exists for real. **Delete it, or stop launching it, the day real perception
is wired into `bringup.launch.py`.** Do not let a Phase 5 or Phase 6 result
get recorded while this stub is running — it exists to unblock Phase 1
specifically, nothing past it.

---

## 4. What's actually achievable in 3 days, in order

Lowest-risk first — this is a deliberately harder triage than the earlier
priority list, because the clock is shorter now than it was when that one was
written.

### 4.1 The safest real demo available: the supervisor, standalone

`safety.launch.py`'s own header says this is deliberate: with **nothing**
feeding it — no Gazebo, no Nav2, no perception — it must sit in `ACTION_STOP`
and publish zero velocity from the very first tick (SPEC.md §9.4.2, "the
fail-safe path observable from day one"). This needs nothing except the C++
node compiling.

```bash
ros2 launch drishti_bringup safety.launch.py
ros2 topic echo /safety/state
```

The moment `colcon build` succeeds, you have a real, camera-ready moment: a
safety-critical system correctly refusing to move with no inputs. Don't
assume which `reason` code it reports first — read what it actually says,
don't guess it in advance for the demo script.

### 4.2 Phase 0 — offline checks

```bash
cd drishti-ugv && python tools/run_checks.py
```

Should reproduce the ~5,000 assertions STATUS.md already claims — a sanity
check that the checkout and build are intact.

### 4.3 Phase 1 — Nav2 actually driving (needs the stub, §3)

```bash
python3 ugv_ws/tools/phase1_stub_perception_health.py &
ros2 launch drishti_bringup bringup.launch.py world:=easy.sdf headless:=true
```

Confirm `/cmd_vel` carries nonzero motion and `ros2 run tf2_tools view_frames`
shows a clean tree.

### 4.4 Explicitly out of scope for this deadline

- **The frozen-camera fault demo specifically** (`fault_injector` +
  `T16_camera_freeze`). `fault_injector_node.py`'s own docstring says it needs
  the bridge remapped onto a `raw_` prefix so it can sit between the sensor
  and the stack — that wiring isn't present in `safety.launch.py` as shipped.
  It's a real, doable thing, just not a "run one command" thing with 3 days
  left. If you do have the ROS param right when you get to it:
  `ros2 run drishti_eval fault_injector --ros-args -p scenario:=T16_camera_freeze`
  (not `--fault camera_freeze` — that flag doesn't exist; the scenario is a
  ROS parameter, not a CLI argument).
- **Phase 2 (SLAM), Phase 3 (terrain/CuPy), Phase 6 (the mission suite)** —
  these need either a GPU (Phase 3) or hours of runtime (Phase 6) neither of
  which fit what's left. If Codespaces goes unexpectedly smoothly and time
  remains, they're bonus, not plan.
- For anything real ROS/Gazebo doesn't produce in time, the honest fallback
  is already built and scripted: the HTML prototype
  ([prototype/DEMO_SCRIPT.md](../prototype/DEMO_SCRIPT.md)), said out loud on
  camera as what it is — see [CLOUD_DEMO_SCRIPT.md](CLOUD_DEMO_SCRIPT.md) §4.

---

## 5. If Phase 3 is worth attempting anyway (stretch, Kaggle + RoboStack)

Kaggle's notebook image is not Ubuntu 24.04, so don't repeat the mistake of
assuming `apt-get install ros-jazzy-desktop` works there the way it does on
GitHub's runner. Use **RoboStack** (`robostack.github.io`) instead — it ships
ROS 2 as conda-forge packages via `mamba`, independent of the host OS version,
specifically for situations like this one. This project has never tested
RoboStack against this exact combination (RTAB-Map + CuPy + Nav2 together);
treat it as something to try early and abandon quickly if it fights back,
not something to plan the last day around.

Scope this narrowly: don't try to run the whole stack on Kaggle. Just prove
`elevation_mapping_cupy` initializes and produces a cost grid on the T4. That
alone is worth more than a failed attempt at everything.

---

## 6. Step by step

1. Push these three files (`.devcontainer/devcontainer.json`,
   `.devcontainer/setup.sh`, `.github/workflows/free-tier-verify.yml`,
   `ugv_ws/tools/phase1_stub_perception_health.py`) to the repo.
2. Open a Codespace on the branch (GitHub → **Code** → **Codespaces** → **Create
   codespace**). Confirm no payment method is attached to the account, or that
   the spending limit is $0, before doing anything else.
3. Let `postCreateCommand` run (`.devcontainer/setup.sh`). Watch for apt
   failures — that's `rosdep`/package-name problems, fix them here first.
4. `cd drishti-ugv/ugv_ws && colcon build --symlink-install`. This is the
   actual first-ever build of this workspace. Expect and fix the `rclcpp` API
   issues STATUS.md already names.
5. Run §4.1 (the standalone supervisor) the moment the build succeeds —
   it's your first guaranteed real result, independent of everything else
   working.
6. Run §4.2, then §4.3.
7. Once something works reliably in the Codespace, push and let
   `.github/workflows/free-tier-verify.yml` reproduce it as CI — that gives
   you a repeatable, timestamped, free record and the log artifacts the
   demo video wants.
8. Record exact versions and what actually passed in STATUS.md's Pinned
   Versions / Results Log — same rule as CLOUD_SETUP.md §8: a run that isn't
   recorded didn't happen for submission purposes.
