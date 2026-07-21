---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Visualizing the SpaceX Tesla Roadster trip to Mars

```{code-cell}
from astropy.time import Time
from astropy import units as u

from omniastro.bodies import Earth, Mars, Sun
from omniastro.ephem import Ephem
from omniastro.frames import Planes
from omniastro.plotting import OrbitPlotter
from omniastro.plotting.orbit.backends import Plotly3D
from omniastro.util import time_range

EPOCH = Time("2018-02-18 12:00:00", scale="tdb")
```

```{code-cell}
roadster = Ephem.from_horizons(
    "SpaceX Roadster",
    epochs=time_range(EPOCH, end=EPOCH + 360 * u.day),
    attractor=Sun,
    plane=Planes.EARTH_ECLIPTIC,
    id_type="majorbody",
)
roadster
```

```{code-cell}
from omniastro.plotting.misc import plot_solar_system
```

```{code-cell}
:tags: [nbsphinx-thumbnail]

frame = plot_solar_system(outer=False, epoch=EPOCH)
frame.plot_ephem(roadster, EPOCH, label="SpaceX Roadster", color="black")
```

```{code-cell}
frame = OrbitPlotter(backend=Plotly3D(), plane=Planes.EARTH_ECLIPTIC)

frame.plot_body_orbit(Earth, EPOCH)
frame.plot_body_orbit(Mars, EPOCH)

frame.plot_ephem(roadster, EPOCH, label="SpaceX Roadster", color="black")

frame.set_view(45 * u.deg, -120 * u.deg, 4 * u.km)
```
