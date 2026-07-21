"""Bulk composition of a custom atmosphere."""
from astropy import units as u
from astropy.constants import R as R_universal

from omniastro.atmosphere.species import get_species

__all__ = ["AtmosphereComposition"]


class AtmosphereComposition:
    """The mole-fraction composition of an atmosphere's well-mixed layer.

    Parameters
    ----------
    fractions : dict
        Mapping of species to mole fraction. Keys may be built-in species
        formulas (e.g. ``"N2"``, case-insensitive) or :class:`~omniastro.
        atmosphere.species.Species` instances for anything not in the
        built-in table. Values must be non-negative and sum to 1 (within
        0.1%).

    Examples
    --------
    >>> from omniastro.atmosphere import AtmosphereComposition
    >>> air = AtmosphereComposition(
    ...     {"N2": 0.78084, "O2": 0.209476, "Ar": 0.00934, "CO2": 0.000314}
    ... )
    >>> air.mean_molecular_weight  # doctest: +SKIP
    <Quantity 0.02896... kg / mol>
    """

    def __init__(self, fractions):
        if not fractions:
            raise ValueError("composition must contain at least one species")

        resolved: dict = {}
        total = 0.0
        for key, fraction in fractions.items():
            if fraction < 0:
                raise ValueError(
                    f"mole fraction of {key!r} must be non-negative, "
                    f"got {fraction}"
                )
            species = get_species(key)
            _, previous_fraction = resolved.get(species.name, (None, 0.0))
            resolved[species.name] = (species, previous_fraction + fraction)
            total += fraction

        if not (0.999 <= total <= 1.001):
            raise ValueError(
                f"mole fractions must sum to 1, got {total}"
            )

        self._fractions = {
            name: (species, frac / total)
            for name, (species, frac) in resolved.items()
        }

    @property
    def fractions(self):
        """dict[str, float] : Mole fraction of each species, by name."""
        return {name: frac for name, (_, frac) in self._fractions.items()}

    @property
    def species(self):
        """list[Species] : The species present in this composition."""
        return [species for species, _ in self._fractions.values()]

    @property
    def mean_molecular_weight(self):
        """~astropy.units.Quantity : Mole-fraction-weighted mean molar mass."""
        M = sum(
            frac * species.molar_mass
            for species, frac in self._fractions.values()
        )
        return M.to(u.kg / u.mol)

    @property
    def specific_gas_constant(self):
        """~astropy.units.Quantity : R_universal / mean molecular weight."""
        return (R_universal / self.mean_molecular_weight).to(
            u.J / (u.kg * u.K)
        )

    @property
    def heat_capacity_ratio(self):
        """float : Mole-fraction-weighted approximation of the mixture's
        adiabatic index (Cp/Cv), used for the speed of sound.
        """
        return sum(
            frac * species.heat_capacity_ratio
            for species, frac in self._fractions.values()
        )

    def __repr__(self):
        parts = ", ".join(
            f"{name}={frac:.4g}" for name, frac in self.fractions.items()
        )
        return f"AtmosphereComposition({parts})"
