import pytest

from omniastro.bodies import Sun
from omniastro.twobody.mean_elements import get_mean_elements


def test_get_mean_elements_raises_error_if_invalid_body():
    body = Sun

    with pytest.raises(ValueError) as excinfo:
        get_mean_elements(body)
    assert (
        f"No available mean elements for {body}. It must be an instance of `omniastro.bodies.SolarSystemPlanet`"
        in excinfo.exconly()
    )
