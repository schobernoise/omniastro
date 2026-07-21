"""A hydrostatic, layered atmosphere model for arbitrary attractors.

This generalizes the piecewise linear temperature-lapse-rate approach used
by the troposphere/stratosphere of `omniastro.earth.atmosphere.COESA76`
(itself modeling the well-mixed, ideal-gas homosphere of Earth) to any
attractor, surface conditions and gas composition. It does not attempt to
model the upper-atmosphere phenomena (diffusive separation, ionization,
escape) that make COESA76's thermosphere branch Earth-specific.
"""
from astropy import units as u
from astropy.constants import R as R_universal
import numpy as np

from omniastro.core.earth_atmosphere.util import (
    _check_altitude as _check_altitude_fast,
    _get_index as _get_index_fast,
)

__all__ = ["CustomAtmosphere"]


class CustomAtmosphere:
    """A custom, layered hydrostatic-equilibrium atmosphere model.

    The atmosphere is defined by a well-mixed gas composition and a series
    of layers, each with a constant temperature lapse rate, in the same
    spirit as the U.S. Standard Atmosphere's troposphere/stratosphere.
    Temperature, pressure and density at any altitude are then derived from
    hydrostatic equilibrium and the ideal gas law.

    Parameters
    ----------
    composition : ~omniastro.atmosphere.composition.AtmosphereComposition
        Bulk gas composition of the atmosphere.
    layers : list[tuple[~astropy.units.Quantity, ~astropy.units.Quantity]]
        Layer boundaries as ``(base_altitude, lapse_rate)`` pairs, sorted by
        increasing altitude and starting at ``0 * u.km``. ``lapse_rate`` is
        the (possibly negative) rate of temperature change with geopotential
        altitude that applies from that boundary up to the next one.
    surface_temperature : ~astropy.units.Quantity
        Temperature at zero altitude.
    surface_pressure : ~astropy.units.Quantity
        Pressure at zero altitude.
    attractor : ~omniastro.bodies.Body, optional
        Body this atmosphere surrounds; used to derive ``radius`` and
        ``surface_gravity`` if not given explicitly.
    radius : ~astropy.units.Quantity, optional
        Attractor radius, required if `attractor` is not given.
    surface_gravity : ~astropy.units.Quantity, optional
        Gravitational acceleration at zero altitude, required if
        `attractor` is not given.

    Examples
    --------
    >>> from astropy import units as u
    >>> from omniastro.atmosphere import AtmosphereComposition, CustomAtmosphere
    >>> co2_atmo = AtmosphereComposition({"CO2": 0.965, "N2": 0.035})
    >>> venus = CustomAtmosphere(
    ...     composition=co2_atmo,
    ...     layers=[(0 * u.km, -8.0 * u.K / u.km)],
    ...     surface_temperature=737 * u.K,
    ...     surface_pressure=9.2e6 * u.Pa,
    ...     radius=6051.8 * u.km,
    ...     surface_gravity=8.87 * u.m / u.s**2,
    ... )
    >>> venus.density(0 * u.km)  # doctest: +SKIP
    <Quantity 65... kg / m3>
    """

    def __init__(
        self,
        composition,
        layers,
        surface_temperature,
        surface_pressure,
        attractor=None,
        radius=None,
        surface_gravity=None,
    ):
        if attractor is not None:
            if radius is not None or surface_gravity is not None:
                raise ValueError(
                    "pass either `attractor`, or `radius` and "
                    "`surface_gravity`, not both"
                )
            radius = attractor.R
            surface_gravity = (attractor.k / attractor.R**2).decompose()
        elif radius is None or surface_gravity is None:
            raise ValueError(
                "either `attractor`, or both `radius` and "
                "`surface_gravity`, must be given"
            )

        if len(layers) == 0:
            raise ValueError("at least one layer is required")
        if not u.isclose(layers[0][0], 0 * u.km):
            raise ValueError("the first layer must start at zero altitude")

        self.composition = composition
        self.r0 = radius.to(u.km)
        self.g0 = surface_gravity.to(u.m / u.s**2)
        self.M = composition.mean_molecular_weight
        self.R_specific = composition.specific_gas_constant
        self.gamma = composition.heat_capacity_ratio

        # g0 * M / R_universal, the combined constant used by the
        # barometric formula below; see COESA76's `alpha`.
        self.alpha = (self.g0 * self.M / R_universal).to(u.K / u.km)

        zb_levels = [z.to(u.km) for z, _ in layers]
        Lb_levels = [L.to(u.K / u.km) for _, L in layers]
        hb_levels = [
            _check_altitude_fast(z.to_value(u.km), self.r0.value, True)[1]
            * u.km
            for z in zb_levels
        ]

        Tb_levels = [surface_temperature.to(u.K)]
        pb_levels = [surface_pressure.to(u.Pa)]
        for i in range(1, len(zb_levels)):
            dh = hb_levels[i] - hb_levels[i - 1]
            Lb = Lb_levels[i - 1]
            Tb = Tb_levels[i - 1]
            pb = pb_levels[i - 1]

            T_next = Tb + Lb * dh
            if Lb == 0 * u.K / u.km:
                p_next = pb * np.exp(-self.alpha * dh / Tb)
            else:
                p_next = pb * (Tb / T_next) ** (self.alpha / Lb)

            Tb_levels.append(T_next.to(u.K))
            pb_levels.append(p_next.to(u.Pa))

        self.zb_levels = u.Quantity(zb_levels)
        self.hb_levels = u.Quantity(hb_levels)
        self.Tb_levels = u.Quantity(Tb_levels)
        self.Lb_levels = u.Quantity(Lb_levels)
        self.pb_levels = u.Quantity(pb_levels)

    def _check_altitude(self, alt, geometric=True):
        alt = alt.to_value(u.km)
        z, h = _check_altitude_fast(alt, self.r0.value, geometric)
        z, h = z * u.km, h * u.km

        if not self.zb_levels[0] <= z <= self.zb_levels[-1]:
            raise ValueError(
                f"Geometric altitude must be in range "
                f"[{self.zb_levels[0]}, {self.zb_levels[-1]}]"
            )
        return z, h

    def _get_index(self, x, x_levels):
        x = x.to_value(u.km)
        x_levels = (x_levels << u.km).value
        return _get_index_fast(x, x_levels)

    def temperature(self, alt, geometric=True):
        """Temperature at a given altitude.

        Parameters
        ----------
        alt : ~astropy.units.Quantity
            Geometric/geopotential altitude.
        geometric : bool
            If `True`, `alt` is interpreted as geometric altitude.

        Returns
        -------
        T : ~astropy.units.Quantity
        """
        z, h = self._check_altitude(alt, geometric=geometric)
        i = self._get_index(z, self.zb_levels)
        Tb, Lb, hb = self.Tb_levels[i], self.Lb_levels[i], self.hb_levels[i]
        T = Tb + Lb * (h - hb)
        return T.to(u.K)

    def pressure(self, alt, geometric=True):
        """Pressure at a given altitude.

        Parameters
        ----------
        alt : ~astropy.units.Quantity
            Geometric/geopotential altitude.
        geometric : bool
            If `True`, `alt` is interpreted as geometric altitude.

        Returns
        -------
        p : ~astropy.units.Quantity
        """
        z, h = self._check_altitude(alt, geometric=geometric)
        i = self._get_index(z, self.zb_levels)
        Tb, Lb, hb, pb = (
            self.Tb_levels[i],
            self.Lb_levels[i],
            self.hb_levels[i],
            self.pb_levels[i],
        )

        if Lb == 0 * u.K / u.km:
            p = pb * np.exp(-self.alpha * (h - hb) / Tb)
        else:
            T = self.temperature(alt, geometric=geometric)
            p = pb * (Tb / T) ** (self.alpha / Lb)

        return p.to(u.Pa)

    def density(self, alt, geometric=True):
        """Density at a given altitude, from the ideal gas law.

        Parameters
        ----------
        alt : ~astropy.units.Quantity
            Geometric/geopotential altitude.
        geometric : bool
            If `True`, `alt` is interpreted as geometric altitude.

        Returns
        -------
        rho : ~astropy.units.Quantity
        """
        T = self.temperature(alt, geometric=geometric)
        p = self.pressure(alt, geometric=geometric)
        rho = p / (self.R_specific * T)
        return rho.to(u.kg / u.m**3)

    def properties(self, alt, geometric=True):
        """Temperature, pressure and density at a given altitude.

        Parameters
        ----------
        alt : ~astropy.units.Quantity
            Geometric/geopotential altitude.
        geometric : bool
            If `True`, `alt` is interpreted as geometric altitude.

        Returns
        -------
        T, p, rho : ~astropy.units.Quantity
        """
        T = self.temperature(alt, geometric=geometric)
        p = self.pressure(alt, geometric=geometric)
        rho = p / (self.R_specific * T)
        return T, p, rho.to(u.kg / u.m**3)

    def sound_speed(self, alt, geometric=True):
        """Speed of sound at a given altitude, from the ideal gas law.

        Uses the composition's mole-fraction-weighted heat capacity ratio,
        see :attr:`~omniastro.atmosphere.composition.AtmosphereComposition.
        heat_capacity_ratio`.

        Parameters
        ----------
        alt : ~astropy.units.Quantity
            Geometric/geopotential altitude.
        geometric : bool
            If `True`, `alt` is interpreted as geometric altitude.

        Returns
        -------
        Cs : ~astropy.units.Quantity
        """
        T = self.temperature(alt, geometric=geometric)
        Cs = np.sqrt(self.gamma * self.R_specific * T)
        return Cs.to(u.m / u.s)
