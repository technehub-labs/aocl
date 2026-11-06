"""aocl — Autonomous Operations & Closed Loops toolkit.

Formalizes the AOCL research corpus "Autonomous Operations and Closed Loops" guide
(v1.2.0) as a versioned, tool-supported model: L1-L5 loop maturity assessment
across three vectors, the informative realization heuristic, loop velocity
taxonomy, and a CLAM-aligned loop modeler format.

The interlock in one line: Autonomous Operations cannot exist without Closed
Loops — loops translate intent into action, action into observation, and
observation into learning.
"""

from aocl.assess import (
    DECISION_MODELS,
    FRONTIERS,
    HITL,
    LEVEL_NAMES,
    RULESET_VERSION,
    VECTORS,
    VELOCITIES,
    assess,
    frontier,
    gap_notes,
    overall_level,
    parse_vector_scores,
    recommended_hitl,
    recommended_model,
)
from aocl.realization import (
    REFERENCE_POINTS,
    assess_position,
    complexity_from_components,
    effort,
    experience_from_components,
    nearest_reference,
    realize,
    required_complexity,
    required_experience,
    sensitivity,
    value_band,
    value_exponential,
    value_logarithmic,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "RULESET_VERSION",
    "VECTORS",
    "LEVEL_NAMES",
    "FRONTIERS",
    "HITL",
    "DECISION_MODELS",
    "VELOCITIES",
    "parse_vector_scores",
    "overall_level",
    "frontier",
    "recommended_model",
    "recommended_hitl",
    "gap_notes",
    "assess",
    "realize",
    "effort",
    "experience_from_components",
    "complexity_from_components",
    "sensitivity",
    "required_complexity",
    "required_experience",
    "nearest_reference",
    "value_band",
    "value_logarithmic",
    "value_exponential",
    "assess_position",
    "REFERENCE_POINTS",
]
