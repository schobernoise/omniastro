from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
import pytest

from omniastro.atmosphere import AtmosphereComposition, CustomAtmosphere
from omniastro.bodies import Earth

AIR = AtmosphereComposition(
    {"N2": 0.780840, "O2": 0.209476, "Ar": 0.009340, "CO2": 0.000314}
)

# Same layer boundaries as omniastro.earth.atmosphere.coesa76's data table,
# up to the top of the homosphere (86 km), where COESA76 itself switches to
# an Earth-specific empirical thermosphere model that this generic engine
# does not attempt to reproduce.
EARTH_TROPO_STRATO_LAYERS = [
    (0.0 * u.km, -6.5 * u.K / u.km),
    (11.019 * u.km, 0.0 * u.K / u.km),
    (20.063 * u.km, 1.0 * u.K / u.km),
    (32.162 * u.km, 2.8 * u.K / u.km),
    (47.350 * u.km, 0.0 * u.K / u.km),
    (51.413 * u.km, -2.8 * u.K / u.km),
    (71.802 * u.km, -2.0 * u.K / u.km),
    (86.0 * u.km, 0.0 * u.K / u.km),
]


@pytest.fixture
def earth_like():
    return CustomAtmosphere(
        composition=AIR,
        layers=EARTH_TROPO_STRATO_LAYERS,
        surface_temperature=288.15 * u.K,
        surface_pressure=1013.25 * u.mbar,
        attractor=Earth,
    )


# Below-86km values taken from the COESA76 report, same as
# tests_earth/tests_atmosphere/test_coesa76.py.
coesa76_solutions = {
    0.5 * u.km: [284.90 * u.K, 9.5461e2 * u.mbar, 1.1673 * u.kg / u.m**3],
    1.0 * u.km: [281.651 * u.K, 8.9876e2 * u.mbar, 1.1117 * u.kg / u.m**3],
    10 * u.km: [223.252 * u.K, 2.6499e2 * u.mbar, 4.1351e-1 * u.kg / u.m**3],
    77 * u.km: [204.493 * u.K, 1.7286e-2 * u.mbar, 2.9448e-5 * u.kg / u.m**3],
}


@pytest.mark.parametrize("z", coesa76_solutions.keys())
def test_reproduces_coesa76_below_86km(earth_like, z):
    expected_T, expected_p, expected_rho = coesa76_solutions[z]

    T, p, rho = earth_like.properties(z)

    # Loose tolerances: our composition-derived constants (mean molecular
    # weight, alpha) are physically equivalent to but not bit-identical
    # with COESA76's exact tabulated values, so small differences compound
    # across layers.
    assert_quantity_allclose(T, expected_T, rtol=1e-3)
    assert_quantity_allclose(p, expected_p, rtol=1.5e-2)
    assert_quantity_allclose(rho, expected_rho, rtol=1.5e-2)


def test_surface_conditions(earth_like):
    T, p, _rho = earth_like.properties(0 * u.km)
    assert_quantity_allclose(T, 288.15 * u.K)
    assert_quantity_allclose(p, 1013.25 * u.mbar, rtol=1e-6)


def test_outside_altitude_range(earth_like):
    with pytest.raises(ValueError, match="range"):
        earth_like.temperature(200 * u.km)


def test_first_layer_must_start_at_zero():
    with pytest.raises(ValueError, match="zero altitude"):
        CustomAtmosphere(
            composition=AIR,
            layers=[(1 * u.km, -6.5 * u.K / u.km)],
            surface_temperature=288.15 * u.K,
            surface_pressure=1013.25 * u.mbar,
            attractor=Earth,
        )


def test_requires_attractor_or_explicit_gravity():
    with pytest.raises(ValueError, match="attractor"):
        CustomAtmosphere(
            composition=AIR,
            layers=[(0 * u.km, -6.5 * u.K / u.km)],
            surface_temperature=288.15 * u.K,
            surface_pressure=1013.25 * u.mbar,
        )


def test_rejects_both_attractor_and_explicit_gravity():
    with pytest.raises(ValueError, match="not both"):
        CustomAtmosphere(
            composition=AIR,
            layers=[(0 * u.km, -6.5 * u.K / u.km)],
            surface_temperature=288.15 * u.K,
            surface_pressure=1013.25 * u.mbar,
            attractor=Earth,
            radius=6371 * u.km,
            surface_gravity=9.81 * u.m / u.s**2,
        )


def test_custom_venus_like_atmosphere_is_self_consistent():
    co2_atmo = AtmosphereComposition({"CO2": 0.965, "N2": 0.035})
    venus = CustomAtmosphere(
        composition=co2_atmo,
        layers=[(0 * u.km, -8.0 * u.K / u.km)],
        surface_temperature=737 * u.K,
        surface_pressure=9.2e6 * u.Pa,
        radius=6051.8 * u.km,
        surface_gravity=8.87 * u.m / u.s**2,
    )

    T, p, rho = venus.properties(0 * u.km)
    assert_quantity_allclose(T, 737 * u.K)
    assert_quantity_allclose(p, 9.2e6 * u.Pa, rtol=1e-6)
    # Sanity check via the ideal gas law rather than a hardcoded value.
    assert_quantity_allclose(
        rho, p / (co2_atmo.specific_gas_constant * T), rtol=1e-6
    )

    Cs = venus.sound_speed(0 * u.km)
    assert_quantity_allclose(Cs, 434.0 * u.m / u.s, rtol=1e-3)
