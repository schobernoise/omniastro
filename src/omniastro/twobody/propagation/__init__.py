"""The following script holds the different high level functions for the
different propagators available at omniastro:

+-------------+------------+-----------------+-----------------+
|  Propagator | Elliptical |    Parabolic    |    Hyperbolic   |
+-------------+------------+-----------------+-----------------+
|  farnocchia |      ✓     |        ✓        |        ✓        |
+-------------+------------+-----------------+-----------------+
|   vallado   |      ✓     |        ✓        |        ✓        |
+-------------+------------+-----------------+-----------------+
|   mikkola   |      ✓     |        ✓        |        ✓        |
+-------------+------------+-----------------+-----------------+
|   markley   |      ✓     |        x        |        x        |
+-------------+------------+-----------------+-----------------+
|   pimienta  |      ✓     |        ✓        |        x        |
+-------------+------------+-----------------+-----------------+
|   gooding   |      ✓     |        x        |        x        |
+-------------+------------+-----------------+-----------------+
|    danby    |      ✓     |        ✓        |        ✓        |
+-------------+------------+-----------------+-----------------+
|    cowell   |      ✓     |        ✓        |        ✓        |
+-------------+------------+-----------------+-----------------+
|  recseries  |      ✓     |        x        |        x        |
+-------------+------------+-----------------+-----------------+

"""
from omniastro.twobody.propagation.cowell import CowellPropagator
from omniastro.twobody.propagation.danby import DanbyPropagator
from omniastro.twobody.propagation.enums import PropagatorKind
from omniastro.twobody.propagation.farnocchia import FarnocchiaPropagator
from omniastro.twobody.propagation.gooding import GoodingPropagator
from omniastro.twobody.propagation.markley import MarkleyPropagator
from omniastro.twobody.propagation.mikkola import MikkolaPropagator
from omniastro.twobody.propagation.pimienta import PimientaPropagator
from omniastro.twobody.propagation.recseries import RecseriesPropagator
from omniastro.twobody.propagation.vallado import ValladoPropagator

from ._compat import propagate

ALL_PROPAGATORS = [
    CowellPropagator,
    DanbyPropagator,
    FarnocchiaPropagator,
    GoodingPropagator,
    MarkleyPropagator,
    MikkolaPropagator,
    PimientaPropagator,
    RecseriesPropagator,
    ValladoPropagator,
]
ELLIPTIC_PROPAGATORS = [
    propagator
    for propagator in ALL_PROPAGATORS
    if propagator.kind & PropagatorKind.ELLIPTIC
]
PARABOLIC_PROPAGATORS = [
    propagator
    for propagator in ALL_PROPAGATORS
    if propagator.kind & PropagatorKind.PARABOLIC
]
HYPERBOLIC_PROPAGATORS = [
    propagator
    for propagator in ALL_PROPAGATORS
    if propagator.kind & PropagatorKind.HYPERBOLIC
]


__all__ = [item.__name__ for item in ALL_PROPAGATORS] + ["propagate"]
