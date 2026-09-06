#!/usr/bin/env python3
"""Enforce the command-path invariant statically.

SPEC.md 9.4.1: the safety supervisor is the ONLY publisher on /cmd_vel. Nav2
publishes to /cmd_vel_nav and must have no route to the base. If that is ever
broken, the vehicle can be driven by a planner with no stop authority above it,
and every claim about deterministic safety becomes false.

That invariant is easy to break with a one-word edit in a YAML file and
invisible until something drives into a wall. This checks it without ROS:

  1. no Nav2 parameter anywhere names /cmd_vel as an output
  2. the supervisor reads /cmd_vel_nav and writes /cmd_vel
  3. the bridge carries exactly one ROS -> Gazebo command topic, and it is
     /cmd_vel
  4. ground truth is read-only and never subscribed by the runtime graph
  5. /clock is bridged, or use_sim_time is a lie (SPEC.md 3.2 rule 4)
  6. every SPEC.md 4.1 input topic is actually bridged

    python tools/check_wiring.py
"""
import os
import re
import sys

import yaml

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV2 = os.path.join(WS, "src", "drishti_bringup", "config", "nav2.yaml")
DRISHTI = os.path.join(WS, "src", "drishti_bringup", "config", "drishti.yaml")
BRIDGE = os.path.join(WS, "src", "drishti_sim", "config", "bridge.yaml")
LAUNCH_DIRS = [
    os.path.join(WS, "src", "drishti_bringup", "launch"),
    os.path.join(WS, "src", "drishti_sim", "launch"),
    os.path.join(WS, "src", "drishti_description", "launch"),
]

CMD_OUT = "/cmd_vel"
CMD_NAV = "/cmd_vel_nav"

# SPEC.md 4.1 -- the inputs the stack is written against.
SPEC_INPUTS = {
    "/camera/rgb/image_raw",
    "/camera/depth/image_rect_raw",
    "/camera/camera_info",
    "/camera/points",
    "/imu/data",
    "/odom",
}

failures = []


def fail(msg):
    failures.append(msg)
    print("  FAIL  " + msg)


def ok(msg):
    print("  ok    " + msg)


def walk(node, path=()):
    """Yield (dotted-path, value) for every scalar in a nested structure."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + ("[%d]" % i,))
    else:
        yield ".".join(path), node


nav2 = yaml.safe_load(open(NAV2, encoding="utf-8"))
drishti = yaml.safe_load(open(DRISHTI, encoding="utf-8"))
bridge = yaml.safe_load(open(BRIDGE, encoding="utf-8"))

print("1. Nav2 never names /cmd_vel as an output")
offenders = []
for dotted, value in walk(nav2):
    if not isinstance(value, str):
        continue
    key = dotted.split(".")[-1]
    if "cmd_vel" in key or key.endswith("_topic"):
        if value.strip() == CMD_OUT:
            offenders.append((dotted, value))
if offenders:
    for dotted, value in offenders:
        fail("nav2.yaml %s = %r -- Nav2 must publish to %s, never %s"
             % (dotted, value, CMD_NAV, CMD_OUT))
else:
    declared = [(d, v) for d, v in walk(nav2)
                if isinstance(v, str) and "cmd_vel" in str(v)]
    for dotted, value in declared:
        if value.strip() != CMD_NAV:
            fail("nav2.yaml %s = %r -- expected %s" % (dotted, value, CMD_NAV))
    if not failures:
        ok("%d Nav2 command topics, all %s" % (len(declared), CMD_NAV))

print("\n2. the supervisor sits on the seam")
sup = drishti.get("safety_supervisor", {}).get("ros__parameters", {})
if sup.get("cmd_vel_in") != CMD_NAV:
    fail("drishti.yaml cmd_vel_in = %r, expected %s" % (sup.get("cmd_vel_in"), CMD_NAV))
else:
    ok("supervisor reads %s" % CMD_NAV)
if sup.get("cmd_vel_out") != CMD_OUT:
    fail("drishti.yaml cmd_vel_out = %r, expected %s" % (sup.get("cmd_vel_out"), CMD_OUT))
else:
    ok("supervisor writes %s" % CMD_OUT)

print("\n3. the bridge carries one inbound command path")
inbound = [e for e in bridge if e.get("direction") in ("ROS_TO_GZ", "BIDIRECTIONAL")]
if len(inbound) != 1:
    fail("expected exactly 1 ROS->GZ bridge entry, found %d: %s"
         % (len(inbound), [e.get("ros_topic_name") for e in inbound]))
elif inbound[0].get("ros_topic_name") != CMD_OUT:
    fail("the inbound bridge entry is %r, expected %s"
         % (inbound[0].get("ros_topic_name"), CMD_OUT))
else:
    ok("one inbound topic, %s, fed by the supervisor alone" % CMD_OUT)

print("\n4. ground truth stays out of the runtime graph")
gt = [e for e in bridge if "ground_truth" in str(e.get("ros_topic_name"))]
for e in gt:
    if e.get("direction") != "GZ_TO_ROS":
        fail("ground truth %r is %s; it must be read-only"
             % (e.get("ros_topic_name"), e.get("direction")))
for d in LAUNCH_DIRS:
    if not os.path.isdir(d):
        continue
    for name in os.listdir(d):
        if not name.endswith(".py"):
            continue
        text = open(os.path.join(d, name), encoding="utf-8")
        body = "\n".join(
            ln for ln in text.read().splitlines() if not ln.strip().startswith("#"))
        if "ground_truth" in body:
            fail("%s references ground_truth outside a comment" % name)
if gt and not any("ground truth" in f for f in failures):
    ok("ground truth is GZ_TO_ROS only and unreferenced by any launch file")

print("\n5. the clock is bridged (SPEC 3.2 rule 4)")
if not any(e.get("ros_topic_name") == "/clock" for e in bridge):
    fail("/clock is not bridged -- use_sim_time cannot work and every "
         "timestamp in the system is wrong")
else:
    ok("/clock bridged")

print("\n6. SPEC 4.1 inputs are bridged")
bridged = {e.get("ros_topic_name") for e in bridge}
missing = SPEC_INPUTS - bridged
if missing:
    fail("SPEC 4.1 input topics not bridged: %s" % sorted(missing))
else:
    ok("all %d SPEC 4.1 input topics present" % len(SPEC_INPUTS))

print("\n7. no launch file remaps anything onto %s" % CMD_OUT)
remap_re = re.compile(r"remappings\s*=", re.S)
suspicious = []
for d in LAUNCH_DIRS:
    if not os.path.isdir(d):
        continue
    for name in os.listdir(d):
        if not name.endswith(".py"):
            continue
        path = os.path.join(d, name)
        body = "\n".join(
            ln for ln in open(path, encoding="utf-8").read().splitlines()
            if not ln.strip().startswith("#"))
        if remap_re.search(body) and CMD_OUT in body:
            suspicious.append(name)
if suspicious:
    fail("launch files remap near %s, check by hand: %s" % (CMD_OUT, suspicious))
else:
    ok("no launch-level remapping onto %s" % CMD_OUT)

print()
if failures:
    print("%d PROBLEM(S)" % len(failures))
    sys.exit(1)
print("command path intact: Nav2 -> %s -> supervisor -> %s -> base"
      % (CMD_NAV, CMD_OUT))
