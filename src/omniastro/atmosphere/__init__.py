"""Physically-based atmosphere models for arbitrary attractors.

Unlike `omniastro.earth.atmosphere`, which offers specific empirical
models of Earth's atmosphere (COESA62, COESA76, Jacchia77), this package
lets you build a custom atmosphere for any body from its gas composition,
surface conditions, and a temperature-lapse-rate profile.
"""
from omniastro.atmosphere.composition import AtmosphereComposition
from omniastro.atmosphere.custom import CustomAtmosphere
from omniastro.atmosphere.species import Species, get_species

__all__ = [
    "AtmosphereComposition",
    "CustomAtmosphere",
    "Species",
    "get_species",
]
