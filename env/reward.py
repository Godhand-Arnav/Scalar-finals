"""
reward.py — Potential-based reward shaping for FORGE.

Implements:
  Φ(s) = w1 * evidence_coverage
       + w2 * source_diversity
       + w3 * contradiction_surface (normalised)
       + w4 * 1/(network_diameter+1)

Step reward: r_shaped = r_base + γ * Φ(s') - Φ(s)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import config

if TYPE_CHECKING:
    from env.claim_graph import ClaimGraph


def compute_potential(graph: "ClaimGraph") -> float:
    """
    Compute Φ(s) — the graph-state potential used in reward shaping.

    Returns a scalar in [0, 1].
    """
    if graph is None:
        return 0.0

    coverage = graph.evidence_coverage
    diversity = graph.source_diversity_entropy
    # Normalise contradictions: clip at 5 for stability
    contra = min(graph.contradiction_surface_area, 5) / 5.0
    # Diameter term — higher diameter means more explored propagation chain
    diameter = graph.network_diameter
    diameter_term = 1.0 / (diameter + 1) if diameter >= 0 else 0.0

    phi = (
        config.POTENTIAL_W1 * coverage
        + config.POTENTIAL_W2 * diversity
        + config.POTENTIAL_W3 * contra
        + config.POTENTIAL_W4 * diameter_term
    )
    return min(max(phi, 0.0), 1.0)
