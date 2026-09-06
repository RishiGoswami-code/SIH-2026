#!/usr/bin/env python3
"""Inject the recorded runs into the web console template.

Kept as a build step rather than hand-pasting, so the page can be regenerated
whenever the scenarios change:

    python tools/export_runs.py && python tools/build_page.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO = os.path.dirname(HERE)
TEMPLATE = os.path.join(PROTO, "web", "template.html")
RUNS = os.path.join(PROTO, "runs.json")
OUT = os.path.join(PROTO, "web", "drishti_console.html")

template = open(TEMPLATE, encoding="utf-8").read()
runs = open(RUNS, encoding="utf-8").read()

# Guard the one thing that would silently break the page: a "</script>" inside
# the JSON would close the data block early.
if "</script" in runs.lower():
    sys.exit("run data contains a closing script tag; escape it before embedding")

if "__RUNS_JSON__" not in template:
    sys.exit("template has no __RUNS_JSON__ placeholder")

page = template.replace("__RUNS_JSON__", runs)
open(OUT, "w", encoding="utf-8").write(page)

data = json.loads(runs)
print("scenarios embedded : %d" % len(data["runs"]))
for r in data["runs"]:
    print("  %-8s %-14s %3d frames  %s"
          % (r["id"], r["world"]["name"], len(r["frames"]), r["outcome"]))
print("wrote %s  (%.1f KB)" % (OUT, len(page) / 1024.0))
