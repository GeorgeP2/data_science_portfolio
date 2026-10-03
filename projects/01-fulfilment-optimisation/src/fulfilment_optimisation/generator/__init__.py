"""Synthetic warehouse instances with parameter ranges calibrated on the KIT suite (T17)."""

from fulfilment_optimisation.generator.layout import LayoutRanges, sample_layout
from fulfilment_optimisation.generator.scenarios import describe, generate_instance, is_held_out

__all__ = ["LayoutRanges", "describe", "generate_instance", "is_held_out", "sample_layout"]
