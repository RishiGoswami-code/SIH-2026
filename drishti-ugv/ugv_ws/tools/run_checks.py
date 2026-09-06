#!/usr/bin/env python3
"""Run every offline check in one go.

None of these need ROS, a GPU or a simulator, so they run on any machine the
team happens to have open. They are the only automated confidence this project
has until the first colcon build (STATUS.md).

    python tools/run_checks.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS = [
    ("contract sync (msg constants, param defaults)", "check_contract_sync.py"),
    ("robot description (SPEC 3 frame tree)", "check_robot_description.py"),
    ("command path (SPEC 9.4.1 /cmd_vel ownership)", "check_wiring.py"),
]

results = []
for title, script in CHECKS:
    print("=" * 72)
    print(title)
    print("=" * 72)
    code = subprocess.call([sys.executable, os.path.join(HERE, script)])
    results.append((title, code))
    print()

print("=" * 72)
for title, code in results:
    print("%-4s %s" % ("PASS" if code == 0 else "FAIL", title))

failed = [t for t, c in results if c != 0]
print()
print("NOTE: the C++ supervisor tests are separate and need a compiler:")
print("  cd src/drishti_safety && g++ -std=c++17 -Iinclude "
      "src/supervisor_core.cpp test/test_supervisor_core.cpp -o t && ./t")
sys.exit(1 if failed else 0)
