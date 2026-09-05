# `ugv_ws` — ROS 2 workspace

The colcon workspace for DRISHTI-UGV. Built against **ROS 2 Jazzy** on Ubuntu
24.04 (SETUP.md §1).

```bash
cd ugv_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

> **Not yet built.** No machine in the project currently has ROS 2 installed,
> so `colcon build` is **unverified** — see STATUS.md blocker **B2**. The
> package manifests, message definitions and parameter file below have been
> syntax-checked only. Treat the first successful build as the real Phase 0
> acceptance event and record the exact toolchain versions in STATUS.md when it
> happens.

## Packages

| Package | Type | Contents |
|---|---|---|
| `drishti_msgs` | `ament_cmake` + rosidl | `SafetyState`, `PerceptionHealth` |
| `drishti_bringup` | `ament_cmake` | shared params, launch files |

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

## Layout

```
ugv_ws/
└── src/
    ├── drishti_msgs/
    │   ├── msg/SafetyState.msg
    │   └── msg/PerceptionHealth.msg
    └── drishti_bringup/
        ├── config/drishti.yaml
        └── launch/
```

`build/`, `install/` and `log/` are ignored.
