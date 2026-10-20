"""Reproduce a CDS survival-curve calibration for a single contract."""

from financepy.market.curves.cds_curve import CDSCurve

# from financepy.market.curves.flat_discount_curve import FlatDiscountCurve
from financepy.products.credit.cds import CDS
from financepy.utils.date import Date
from financepy.utils.frequency import FrequencyTypes
from financepy.utils.day_count import DayCountTypes
from financepy.market.curves.interpolator import InterpTypes
from financepy.market.curves.ois_curve import OISCurve
from financepy.utils.calendar import CalendarTypes
from financepy.products.rates.ois import OIS
from financepy.products.rates.ibor_deposit import IborDeposit
from financepy.products.rates.ibor_swap import SwapTypes

# dados gerais
trade_date = Date(21, 10, 2026)
step_in_dt = Date(21, 10, 2026)
previous_coupon_dt = Date(21, 10, 2026)
maturity_dt = Date(20, 12, 2036)
running_coupon = 266 / 10_000
spread = 266 / 10_000
notional = 1_000_000
recovery_rate = 0.0
flat_discount_rate = 0.0387

## Curve
# old by HH: discount_curve = FlatDiscountCurve(step_in_dt, flat_discount_rate)
# adiciona o vertice de deposit
deposit = IborDeposit(
    trade_date,
    Date(22, 10, 2026),
    flat_discount_rate,
    DayCountTypes.ACT_360,
    cal_type=CalendarTypes.UNITED_STATES,
)
# adiciona o vertice de swap
OIS_swaps = []
for maturities in [1, 2, 3, 5, 7, 10, 12, 15, 20]:
    swap = OIS(
        Date(22, 10, 2026),
        Date(22, 10, 2026).add_years(maturities),
        SwapTypes.PAY,
        flat_discount_rate,
        FrequencyTypes.ANNUAL,
        DayCountTypes.ACT_360,
        1e6,
        2,
        0.0,
        FrequencyTypes.ANNUAL,
        DayCountTypes.ACT_360,
        CalendarTypes.UNITED_STATES,
    )
    OIS_swaps.append(swap)
# monta a curva de desconto com os dois vertices
discount_curve = OISCurve(
    trade_date, [deposit], [], OIS_swaps, InterpTypes.FLAT_FWD_RATES
)

# monta o CDS com os dados do contrato
cds = CDS(
    step_in_dt,
    "10y",  # maturity_dt,
    spread,
    # notional=notional,
    freq_type=FrequencyTypes.SEMI_ANNUAL,
    prev_coupon_dt=previous_coupon_dt,
)

issuer_curve = CDSCurve(
    step_in_dt,
    [cds],
    discount_curve,
    recovery_rate,
    DayCountTypes.ACT_360,
    InterpTypes.FLAT_FWD_RATES,
)

dirty_pv, clean_pv = cds.value(step_in_dt, issuer_curve, recovery_rate)
q_star = issuer_curve._qs[-1]

print(f"Step-in date: {step_in_dt}")
print(f"Previous coupon date: {previous_coupon_dt}")
print(f"Maturity date: {cds.maturity_dt}")
print(f"Frequency: {cds.freq_type.name}")
print(f"Running coupon / spread: {running_coupon * 10_000:.2f} bps")
print(f"Notional: {notional:,.2f}")
print(f"Recovery rate: {recovery_rate:.2%}")
# print(f"Flat discount rate: {flat_discount_rate:.2%} (continuous)")
print(f"Flat discount rate: {flat_discount_rate:.2%} (Act/360)")
print(f"Calibrated maturity survival probability (q_star): {q_star:.10f}")
print(f"Dirty PV: {dirty_pv:.10f}")
print(f"Clean PV: {clean_pv:.10f}")

assert 0.0 < q_star <= 1.0
assert abs(clean_pv) < 1e-5

# mostra todos os dados da curva de CDS caso o debug seja verbal
for dados in cds.print_payments_by_HH(step_in_dt, issuer_curve, full_flow=True):
    print(dados)
