"""Chemical species usable when building custom atmosphere compositions."""
from dataclasses import dataclass

from astropy import units as u


@dataclass(frozen=True)
class Species:
    """A chemical species contributing to an atmosphere's bulk composition.

    Parameters
    ----------
    name : str
        Short identifier, e.g. ``"CO2"``.
    molar_mass : ~astropy.units.Quantity
        Molar mass of the species.
    heat_capacity_ratio : float
        Adiabatic index (Cp/Cv) of the species, used to approximate the
        mixture's heat capacity ratio for the speed of sound. This is a
        classical ideal-gas approximation (5/3 monatomic, 7/5 diatomic,
        ~4/3 polyatomic) and does not account for temperature-dependent
        vibrational modes.
    """

    name: str
    molar_mass: u.Quantity
    heat_capacity_ratio: float

    def __post_init__(self):
        if not self.molar_mass.unit.is_equivalent(u.kg / u.mol):
            raise ValueError(
                f"molar_mass must have units equivalent to kg / mol, "
                f"got {self.molar_mass.unit}"
            )


_MONATOMIC = 5 / 3
_DIATOMIC = 7 / 5
_POLYATOMIC = 4 / 3

# Common atmospheric species, keyed by uppercase formula.
# Molar masses in g/mol from IUPAC standard atomic weights.
SPECIES = {
    "H": Species("H", 1.008 * u.g / u.mol, _MONATOMIC),
    "H2": Species("H2", 2.016 * u.g / u.mol, _DIATOMIC),
    "HE": Species("He", 4.002602 * u.g / u.mol, _MONATOMIC),
    "H2O": Species("H2O", 18.01528 * u.g / u.mol, _POLYATOMIC),
    "CH4": Species("CH4", 16.0425 * u.g / u.mol, _POLYATOMIC),
    "NH3": Species("NH3", 17.0305 * u.g / u.mol, _POLYATOMIC),
    "NE": Species("Ne", 20.1797 * u.g / u.mol, _MONATOMIC),
    "N2": Species("N2", 28.0134 * u.g / u.mol, _DIATOMIC),
    "CO": Species("CO", 28.0101 * u.g / u.mol, _DIATOMIC),
    "NO": Species("NO", 30.0061 * u.g / u.mol, _DIATOMIC),
    "O2": Species("O2", 31.9988 * u.g / u.mol, _DIATOMIC),
    "H2S": Species("H2S", 34.0809 * u.g / u.mol, _POLYATOMIC),
    "AR": Species("Ar", 39.948 * u.g / u.mol, _MONATOMIC),
    "N2O": Species("N2O", 44.0128 * u.g / u.mol, _POLYATOMIC),
    "CO2": Species("CO2", 44.0095 * u.g / u.mol, _POLYATOMIC),
    "O3": Species("O3", 47.998 * u.g / u.mol, _POLYATOMIC),
    "SO2": Species("SO2", 64.066 * u.g / u.mol, _POLYATOMIC),
    "KR": Species("Kr", 83.798 * u.g / u.mol, _MONATOMIC),
    "XE": Species("Xe", 131.293 * u.g / u.mol, _MONATOMIC),
}


def get_species(name):
    """Looks up a built-in :class:`Species` by (case-insensitive) formula.

    Parameters
    ----------
    name : str or Species
        Formula such as ``"CO2"``, or an already-built :class:`Species`
        instance, which is returned unchanged.

    Returns
    -------
    Species
    """
    if isinstance(name, Species):
        return name

    try:
        return SPECIES[name.upper()]
    except KeyError:
        raise KeyError(
            f"Unknown species {name!r}. Built-in species are "
            f"{sorted(s.name for s in SPECIES.values())}; for anything "
            "else, pass a `Species` instance directly."
        ) from None
