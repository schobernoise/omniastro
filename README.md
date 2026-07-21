[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?logo=open%20source%20initiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue.svg?logo=python&logoColor=white)](pyproject.toml)
[![Code style](https://img.shields.io/badge/code%20style-black%20isort%20ruff-black)]()

# omniastro

> **Disclaimer:** This is a solo, spare-time fork maintained with the heavy
> assistance of [Claude Code](https://claude.com/claude-code). I don't have
> the time to maintain this manually the way a project like this deserves,
> so expect AI-assisted changes, and review/test anything before relying on
> it in production. The long-term aim is to grow this into a toolkit for
> physically accurate worldbuilding (custom planets, atmospheres, orbits,
> etc.), beyond poliastro's original Solar System scope.

`omniastro` is an active fork of [poliastro](https://github.com/poliastro/poliastro), a pure
Python library for interactive Astrodynamics and Orbital Mechanics. poliastro was
[archived by its original maintainers in 2023](https://github.com/poliastro/poliastro/issues/1640);
this fork reanimates the codebase, keeps its dependencies current, and will carry
the project forward for use in other applications.

All credit for the original design, algorithms, and years of work goes to the
poliastro authors and community — see [Attribution](#attribution) below.

poliastro/omniastro provides a simple and intuitive API for orbit propagation,
solving Lambert's problem, converting between position/velocity vectors and
classical orbital elements, and orbit plotting, among others. It focuses on
interplanetary applications, but can also be used to analyze artificial
satellites in Low-Earth Orbit (LEO).


## Requirements

omniastro requires the following Python packages:

- [numpy](https://numpy.org/) for basic numerical routines
- [astropy](https://www.astropy.org/) for physical units and time handling
- [numba](https://numba.pydata.org/) for accelerating the code
- [jplephem](https://github.com/brandon-rhodes/python-jplephem) for the planetary ephemerides using SPICE kernels
- [matplotlib](https://matplotlib.org/) for orbit plotting
- [plotly](https://plotly.com/) for 2D and 3D interactive orbit plotting
- [scipy](https://scipy.org/) for root finding and numerical propagation

omniastro targets Python 3.12+ on Linux, macOS and Windows. See
[`pyproject.toml`](pyproject.toml) for exact version constraints.


## Installation

This fork is not (yet) published on PyPI or conda-forge. Install it directly
from source:

```bash
git clone https://github.com/schobernoise/omniastro.git
cd omniastro
python -m pip install -e .
```

For development, install the `test` and `doc` extras as needed:

```bash
python -m pip install -e ".[test]"
```


## Usage

The Python package itself has been renamed from `poliastro` to `omniastro`:

```python
from omniastro.bodies import Earth
from omniastro.twobody import Orbit
```

### Custom atmospheres

Besides the built-in Earth atmosphere models (`omniastro.earth.atmosphere`),
`omniastro.atmosphere` lets you build a physically consistent atmosphere for
any world from its gas composition, surface conditions, and a temperature
lapse-rate profile — useful for worldbuilding:

```python
from astropy import units as u
from omniastro.atmosphere import AtmosphereComposition, CustomAtmosphere

co2_atmo = AtmosphereComposition({"CO2": 0.965, "N2": 0.035})
venus_like = CustomAtmosphere(
    composition=co2_atmo,
    layers=[(0 * u.km, -8.0 * u.K / u.km)],
    surface_temperature=737 * u.K,
    surface_pressure=9.2e6 * u.Pa,
    radius=6051.8 * u.km,
    surface_gravity=8.87 * u.m / u.s**2,
)
venus_like.density(0 * u.km)  # <Quantity 65.23... kg / m3>
```

`temperature`, `pressure`, `density`, `sound_speed` and `properties` work at
any altitude within the defined layers, and an `attractor=` (a
`~omniastro.bodies.Body`) can be passed instead of explicit `radius`/
`surface_gravity`.

## Documentation

The original poliastro documentation (quickstart guide, API reference,
examples gallery) is still a good starting point for understanding the
library's API — everywhere it writes `poliastro.foo`, read `omniastro.foo`,
since the core has not otherwise diverged yet:

* [poliastro stable documentation](https://docs.poliastro.space/en/stable/)
* [poliastro examples gallery](https://docs.poliastro.space/en/latest/gallery.html)

Docs specific to this fork will be published as the project evolves.


## License

omniastro, like poliastro, is released under the MIT license, allowing
commercial use of the library. Please refer to the [COPYING](COPYING) file.

    The MIT License (MIT)

    Copyright (c) 2012-2023 Juan Luis Cano Rodríguez, Jorge Martínez Garrido, and the poliastro development team
    Copyright (c) 2026 Fabian Schober and omniastro contributors

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.


## Attribution

This project is a fork of [poliastro](https://github.com/poliastro/poliastro),
originally created by Juan Luis Cano Rodríguez and Jorge Martínez Garrido, and
built by the poliastro development team and community over more than a
decade. poliastro was archived in 2023; per the archival notice, forks are
welcome provided attribution is retained. If you use the underlying
astrodynamics algorithms in published work, please cite the original project:

    Juan Luis Cano Rodríguez, Jorge Martinez, et al.. (2023). poliastro: poliastro 0.17.0. Zenodo. 10.5281/zenodo.6817189


## Problems and suggestions

This is a personal fork under active development for a downstream application.
If you run into a bug or have a suggestion, please open an issue in this
repository's [issue tracker](https://github.com/schobernoise/omniastro/issues).
