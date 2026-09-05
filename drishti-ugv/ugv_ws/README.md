# `ugv_ws` — ROS 2 workspace

The colcon workspace for DRISHTI-UGV. Built against **ROS 2 Jazzy** on Ubuntu
24.04 (SETUP.md §1).

```bash
cd ugv_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

> **`colcon build` is unverified.** No machine on the project has ROS 2
> installed yet — STATUS.md blocker **B3**. Treat the first successful build as
> the real Phase 0 acceptance event and record the exact toolchain versions in
> STATUS.md when it happens.

### What *is* verified

The supervisor's decision core has no ROS dependency, by design, so it can be
compiled and tested on any machine with a C++17 compiler — including one that
cannot run ROS at all. **It compiles clean under `-Wall -Wextra -Wpedantic
-Werror` and passes 377 checks.**

```bash
cd src/drishti_safety
g++ -std=c++17 -Wall -Wextra -Wpedantic -Iinclude \
    src/supervisor_core.cpp test/test_supervisor_core.cpp -o test_sup && ./test_sup
```

The same file is registered as a CTest target, so `colcon test` runs it too.

```bash
python tools/check_contract_sync.py
```

catches the drift a compiler cannot see: `SafetyState.msg` constants against the
C++ `Action`/`Reason` enums, and the `Params` defaults in the header against
`drishti.yaml`. Run it after touching any of those three files.

Everything else — the ROS node, the launch file — is **uncompiled and
unexecuted**.

## Packages

| Package | Type | Contents | State |
|---|---|---|---|
| `drishti_msgs` | `ament_cmake` + rosidl | `SafetyState`, `PerceptionHealth` | syntax-checked |
| `drishti_bringup` | `ament_cmake` | shared params, `safety.launch.py` | syntax-checked |
| `drishti_safety` | `ament_cmake` | supervisor core + ROS node | **core tested**, node uncompiled |

Everything else in the system uses standard ROS 2 interfaces. Two custom
messages exist because nothing standard carries them (SPEC.md §4).

### `drishti_msgs`

**`SafetyState`** — published every supervisor tick on `/safety/state`. It is
the audit record of the stop decision: the action taken, the reason code, what
was actually published on `/cmd_vel`, and the evidence behind it. The evidence
fields are populated even when the action is `ACTION_PASS`, so a recorded run
can be replayed and the decision boundary inspected without re-running
perception.

Reason codes are numbered in the SPEC.md §9.1 evaluation order, so a higher
code means "checked later, and everything before it passed".

**`PerceptionHealth`** — published on `/perception/health`. Liveness and
quality only. The supervisor consumes this to decide whether perception can be
trusted at all; it never looks inside the model.

### `drishti_bringup`

Holds no algorithm code. It exists so every node reads its thresholds and its
clock setting from one file, `config/drishti.yaml`.

**The values in that file are initial defaults, not tuned numbers.** SPEC.md
§9.3 fixes the parameter names and meanings; it does not fix the values. Phase
5 tunes them against the randomised suite.

## Two things to check on the first real build

1. **`use_twist_stamped`** — Nav2 accepts `Twist` or `TwistStamped` depending
   on version and configuration. Pin it once against the Nav2 actually
   installed and keep it identical across Nav2, the supervisor and the base.
   Do not assume.
2. **The `/cmd_vel_nav` → `/cmd_vel` split** — Nav2 must publish to
   `cmd_vel_in` and must have no route to the base. The supervisor is the only
   publisher on `/cmd_vel`. If Nav2 can reach the base directly, the safety
   design is void (SPEC.md §4.3, §9.4.1).

### `drishti_safety`

The supervisor, split in two on purpose:

- **`supervisor_core.{hpp,cpp}`** — all the policy, zero dependencies beyond
  the standard library. One function, `evaluate()`, decides everything. It is
  pure: same inputs, same decision, no clock, no I/O.
- **`safety_supervisor_node.cpp`** — collects evidence, ticks on its own timer,
  calls `evaluate()`, publishes. Holds no policy.

That split is what makes invariant 9.4.5 real rather than aspirational.

**The evaluation order diverges from the SPEC.md §9.1 pseudocode as originally
written, and the spec has been corrected to match** — see §9.1 and D13. Briefly:
every STOP condition is now checked before the single SLOW branch, because the
original order let low perception confidence mask a missing path and forward a
command anyway.

## Layout

```
ugv_ws/
├── tools/check_contract_sync.py     cross-file consistency checks
└── src/
    ├── drishti_msgs/
    │   └── msg/{SafetyState,PerceptionHealth}.msg
    ├── drishti_bringup/
    │   ├── config/drishti.yaml
    │   └── launch/safety.launch.py
    └── drishti_safety/
        ├── include/drishti_safety/supervisor_core.hpp
        ├── src/{supervisor_core,safety_supervisor_node}.cpp
        └── test/test_supervisor_core.cpp
```

`build/`, `install/` and `log/` are ignored.
