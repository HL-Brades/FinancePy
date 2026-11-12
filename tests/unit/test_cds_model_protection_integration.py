import math

import numpy as np
import pytest

from financepy.market.curves.cds_curve import CDSCurve
from financepy.market.curves.flat_discount_curve import FlatDiscountCurve
from financepy.market.curves.interpolator import InterpTypes
from financepy.models.cds_model import (
    build_protection_integration_times,
    prot_leg_pv_numba,
)
from financepy.products.credit.cds import CDS
from financepy.utils.date import Date


def test_protection_grid_includes_curve_knots_and_contract_dates():
    grid = build_protection_integration_times(
        0.1,
        1.1,
        np.array([0.0, 0.6, 2.0]),
        np.array([0.0, 0.8, 2.0]),
        np.array([0.4, 1.0]),
        2,
    )

    assert grid[0] == 0.1
    assert grid[-1] == 1.1
    assert 0.4 in grid
    assert 0.6 in grid
    assert 0.8 in grid
    assert 1.0 in grid


def test_protection_integral_is_exact_across_piecewise_flat_forward_knots():
    hazard_rates = (0.04, 0.07)
    discount_rates = (0.02, 0.03)
    node_time = 1.0
    discount_times = np.array([0.0, node_time, 2.0])
    survival_times = np.array([0.0, node_time, 2.0])
    discount_values = np.array(
        [1.0, math.exp(-discount_rates[0]), math.exp(-sum(discount_rates))]
    )
    survival_values = np.array(
        [1.0, math.exp(-hazard_rates[0]), math.exp(-sum(hazard_rates))]
    )
    integration_times = build_protection_integration_times(
        0.25,
        1.75,
        discount_times,
        survival_times,
        np.array([0.5, 1.5]),
        1,
    )
    recovery_rate = 0.4

    actual = prot_leg_pv_numba(
        integration_times,
        discount_times,
        discount_values,
        survival_times,
        survival_values,
        recovery_rate,
        0,
        InterpTypes.FLAT_FWD_RATES.value,
    )

    expected = 0.0
    for start, end, hazard_rate, discount_rate in (
        (0.25, 1.0, hazard_rates[0], discount_rates[0]),
        (1.0, 1.75, hazard_rates[1], discount_rates[1]),
    ):
        q_start = math.exp(
            -hazard_rates[0] * min(start, node_time)
            - hazard_rates[1] * max(start - node_time, 0.0)
        )
        z_start = math.exp(
            -discount_rates[0] * min(start, node_time)
            - discount_rates[1] * max(start - node_time, 0.0)
        )
        total_rate = hazard_rate + discount_rate
        expected += (
            (1.0 - recovery_rate)
            * hazard_rate
            * q_start
            * z_start
            * (-math.expm1(-total_rate * (end - start)))
            / total_rate
        )

    assert actual == pytest.approx(expected, abs=1e-13)


def test_protection_at_start_of_day_shifts_effective_and_maturity_dates():
    anchor_dt = Date(1, 1, 2024)
    step_in_dt = anchor_dt.add_days(1)
    maturity_dt = Date(1, 1, 2025)
    discount_curve = FlatDiscountCurve(anchor_dt, 0.03)
    issuer_curve = CDSCurve(
        anchor_dt,
        [],
        discount_curve,
        0.4,
        interp_method=InterpTypes.FLAT_FWD_RATES,
    )
    hazard_rate = 0.05
    issuer_curve.set_times(np.array([0.0, 2.0]))
    issuer_curve.set_qs(np.array([1.0, math.exp(-2.0 * hazard_rate)]))

    cds = CDS(
        step_in_dt,
        maturity_dt,
        0.01,
        notional=1.0,
        protection_at_start_of_day=True,
    )
    cds_without_shift = CDS(
        step_in_dt,
        maturity_dt,
        0.01,
        notional=1.0,
    )
    actual = cds.prot_leg_pv(anchor_dt, issuer_curve, 0.4)
    assert cds.rpv01(anchor_dt, issuer_curve) != cds_without_shift.rpv01(
        anchor_dt, issuer_curve
    )

    t_start = 0.0
    t_end = (maturity_dt.add_days(-1) - anchor_dt) / 365.0
    total_rate = hazard_rate + 0.03
    expected = (
        (1.0 - 0.4)
        * hazard_rate
        * (-math.expm1(-total_rate * (t_end - t_start)))
        / total_rate
    )

    assert actual == pytest.approx(expected, abs=1e-12)
