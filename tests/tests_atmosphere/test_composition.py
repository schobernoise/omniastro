from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
import pytest

from omniastro.atmosphere import AtmosphereComposition, Species

AIR_FRACTIONS = {
    "N2": 0.780840,
    "O2": 0.209476,
    "Ar": 0.009340,
    "CO2": 0.000314,
}


def test_mean_molecular_weight_matches_coesa76_M0():
    air = AtmosphereComposition(AIR_FRACTIONS)
    # COESA76's M0 = 28.9644 kg/kmol
    assert_quantity_allclose(
        air.mean_molecular_weight, 28.9644e-3 * u.kg / u.mol, rtol=1e-3
    )


def test_specific_gas_constant_matches_coesa76_R_air():
    air = AtmosphereComposition(AIR_FRACTIONS)
    # COESA76's R_air = 287.053 J / kg / K
    assert_quantity_allclose(
        air.specific_gas_constant, 287.053 * u.J / u.kg / u.K, rtol=1e-3
    )


def test_fractions_are_normalized():
    # Slightly off from 1.0 but within tolerance.
    comp = AtmosphereComposition({"N2": 0.79, "O2": 0.21001})
    total = sum(comp.fractions.values())
    assert total == pytest.approx(1.0)


def test_rejects_fractions_far_from_one():
    with pytest.raises(ValueError, match="sum to 1"):
        AtmosphereComposition({"N2": 0.5, "O2": 0.3})


def test_rejects_negative_fraction():
    with pytest.raises(ValueError, match="non-negative"):
        AtmosphereComposition({"N2": -0.1, "O2": 1.1})


def test_rejects_unknown_species_name():
    with pytest.raises(KeyError):
        AtmosphereComposition({"UNOBTANIUM": 1.0})


def test_accepts_custom_species():
    unobtanium = Species("Unobtanium", 999 * u.g / u.mol, 1.5)
    comp = AtmosphereComposition({unobtanium: 1.0})
    assert_quantity_allclose(
        comp.mean_molecular_weight, 999e-3 * u.kg / u.mol
    )
    assert comp.heat_capacity_ratio == pytest.approx(1.5)


def test_pure_monatomic_heat_capacity_ratio():
    argon = AtmosphereComposition({"Ar": 1.0})
    assert argon.heat_capacity_ratio == pytest.approx(5 / 3)


def test_empty_composition_rejected():
    with pytest.raises(ValueError):
        AtmosphereComposition({})
