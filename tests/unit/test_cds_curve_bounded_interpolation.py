import pytest

from financepy.market.curves.cds_curve import CDSCurve
from financepy.market.curves.flat_discount_curve import FlatDiscountCurve
from financepy.market.curves.interpolator import InterpTypes
from financepy.products.credit.cds import CDS
from financepy.utils.date import Date
from financepy.utils.error import FinError


def test_cds_curve_rejects_calibration_without_valid_survival_root():
    value_dt = Date(20, 12, 2018)
    discount_curve = FlatDiscountCurve(value_dt, 0.03)
    cds = CDS(value_dt, "5Y", -0.001)

    with pytest.raises(FinError, match="no survival-probability root"):
        CDSCurve(value_dt, [cds], discount_curve, 0.40)


def test_cds_curve_calibrates_using_configured_survival_interpolation():
    value_dt = Date(20, 12, 2018)
    discount_curve = FlatDiscountCurve(value_dt, 0.03)
    contracts = [
        CDS(value_dt, "5Y", 0.01),
        CDS(value_dt, "10Y", 0.015),
    ]
    issuer_curve = CDSCurve(
        value_dt,
        contracts,
        discount_curve,
        0.40,
        interp_method=InterpTypes.LINEAR_DISCOUNT,
    )

    assert all(0.0 < q <= 1.0 for q in issuer_curve._qs)
    for cds in contracts:
        _, clean_pv = cds.value(value_dt, issuer_curve, 0.40)
        assert abs(clean_pv) < 1e-5
