# Copyright 2026 The Vikings. Licensed under the Apache License, Version 2.0.
"""Perception liveness and quality, as consumed by the safety supervisor.

SPEC.md §5.3 and §9.2. This computes what goes on `/perception/health`. The
supervisor reads it to decide whether perception can be trusted at all; it
never looks inside the model.

No ROS. Pure arithmetic on timestamps and confidences, so it is testable.

---------------------------------------------------------------------------
THE DECISION THIS MODULE EXISTS TO GET RIGHT

What is the confidence of a frame in which the detector found nothing?

Both obvious answers are wrong:

  1.0 -- "nothing to be unsure about". Then a detector that has silently died
         and returns an empty list every frame reports perfect confidence, and
         the supervisor runs at full speed into whatever it stopped seeing.

  0.0 -- "we saw nothing". Then open safe terrain, which is the common case
         and the one the vehicle should cross briskly, permanently pins the
         supervisor into SLOW. A safety mechanism that fires constantly gets
         turned off.

The distinction that actually matters is not how many objects were found but
whether the pipeline RAN. So:

  pipeline did not run, or errored     -> 0.0, and the supervisor stops
  a segmenter produced a mask          -> its coverage-weighted confidence
  detections exist, no mask            -> mean detection confidence
  ran fine, found nothing, no mask     -> `nominal_confidence`

Finding nothing is not evidence of danger. A pipeline that did not run is.
---------------------------------------------------------------------------
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

#: Age reported when a stream has never produced a frame. Chosen over
#: `inf` so it survives serialisation into a float32 message field.
NEVER_SEEN_AGE = 1.0e9


@dataclass
class FrameStats:
    """What the perception node knows at the moment it publishes health."""

    now: float                                  #: s, on the node's clock
    last_rgb_stamp: Optional[float] = None      #: s, sensor stamp
    last_depth_stamp: Optional[float] = None    #: s, sensor stamp

    pipeline_ok: bool = False                   #: inference ran without error
    detection_confidences: Sequence[float] = field(default_factory=tuple)
    #: Mean confidence over the semantic mask, if a segmenter ran.
    segmentation_confidence: Optional[float] = None
    #: Fraction of pixels the segmenter actually classified, [0, 1].
    segmentation_coverage: float = 0.0

    #: Wall time from frame arrival to outputs ready.
    latency_ms: float = float("nan")


@dataclass
class Health:
    """The `/perception/health` payload, as plain numbers."""

    rgb_age: float
    depth_age: float
    rgb_ok: bool
    depth_ok: bool
    mean_confidence: float
    latency_ms: float
    detection_count: int
    #: Why the confidence took the value it did. Logged, not published: it is
    #: for the person reading a bag six weeks later.
    confidence_basis: str = ""


def stamp_age(now: float, stamp: Optional[float],
              future_tolerance: float = 0.05) -> float:
    """Age of a timestamped frame in seconds.

    Mirrors `drishti_safety::stamp_age`. Nothing received, non-finite values,
    or a stamp meaningfully in the future all return NEVER_SEEN_AGE: clocks
    that disagree are no evidence at all (SPEC.md §3.2 rule 4).
    """
    if stamp is None:
        return NEVER_SEEN_AGE
    if not math.isfinite(now) or not math.isfinite(stamp):
        return NEVER_SEEN_AGE
    age = now - stamp
    if age < -abs(future_tolerance):
        return NEVER_SEEN_AGE
    return max(age, 0.0)


def _clean(values: Sequence[float]) -> List[float]:
    """Finite values clamped to [0, 1]; anything else is discarded."""
    return [min(max(float(v), 0.0), 1.0)
            for v in values if isinstance(v, (int, float)) and math.isfinite(v)]


def frame_confidence(stats: FrameStats,
                     nominal_confidence: float = 0.80,
                     min_coverage: float = 0.20) -> tuple:
    """Confidence for this frame, and the reason for it.

    See the module docstring. Returns (confidence, basis).
    """
    if not stats.pipeline_ok:
        return 0.0, "pipeline did not run"

    seg = stats.segmentation_confidence
    if seg is not None and math.isfinite(seg):
        coverage = stats.segmentation_coverage
        if not math.isfinite(coverage):
            coverage = 0.0
        coverage = min(max(coverage, 0.0), 1.0)
        if coverage < min_coverage:
            # A mask covering a sliver of the image says almost nothing about
            # the frame. Scale the confidence by how much was actually
            # classified rather than trusting a confident opinion about 3% of
            # the pixels.
            return (min(max(seg, 0.0), 1.0) * coverage,
                    "segmentation coverage %.2f below %.2f" % (coverage, min_coverage))
        return min(max(seg, 0.0), 1.0), "segmentation"

    detections = _clean(stats.detection_confidences)
    if detections:
        # The mean, not the max: one certain detection does not make the rest
        # of the frame understood.
        return sum(detections) / len(detections), "detections"

    return (min(max(nominal_confidence, 0.0), 1.0),
            "pipeline ran, nothing detected")


def compute(stats: FrameStats,
            t_camera_stale: float = 0.30,
            t_depth_stale: float = 0.30,
            nominal_confidence: float = 0.80,
            min_coverage: float = 0.20) -> Health:
    """Build the health report for one frame.

    Staleness thresholds default to the same values as the supervisor's
    `t_camera_stale` and `t_depth_stale` so the two agree about what "fresh"
    means. They are passed in rather than imported because both sides read them
    from the shared params file at run time.
    """
    rgb_age = stamp_age(stats.now, stats.last_rgb_stamp)
    depth_age = stamp_age(stats.now, stats.last_depth_stamp)
    confidence, basis = frame_confidence(stats, nominal_confidence, min_coverage)

    return Health(
        rgb_age=rgb_age,
        depth_age=depth_age,
        rgb_ok=rgb_age <= t_camera_stale,
        depth_ok=depth_age <= t_depth_stale,
        mean_confidence=confidence,
        latency_ms=stats.latency_ms,
        detection_count=len(_clean(stats.detection_confidences)),
        confidence_basis=basis,
    )
