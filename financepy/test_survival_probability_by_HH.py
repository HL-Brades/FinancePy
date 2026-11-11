# noqa: N999  # Local test script name is intentionally not snake_case.
"""import the packages that we'll use"""

# time
# import datetime as dt

# uteis
# from . import utils_by_HH as ut

# financial functions
from financepy.market.curves.interpolator import InterpTypes

# CDS functions
from financepy.products.credit.cds import CDS
from financepy.market.curves.cds_curve import CDSCurve

# dates functions
from financepy.utils.date import Date
from financepy.utils.day_count import DayCountTypes
from financepy.utils.frequency import FrequencyTypes

# from .utils.date import from_datetime
from financepy.utils.calendar import CalendarTypes

# swap functions
from financepy.products.rates.ibor_swap import SwapTypes
from financepy.products.rates.ois import OIS
from financepy.market.curves.ois_curve import OISCurve
from financepy.products.rates.ibor_deposit import IborDeposit

# variáveis gerais
# deposits
OISdeposits = []  # lista de todos os vertices da curva de deposits
depoDCCType = DayCountTypes.ACT_360
calendario = CalendarTypes.UNITED_STATES
trade_date = Date(9, 11, 2026)
data_deposito = Date(12, 11, 2026)
taxa_deposito = 0.0389
# adiciona o unico deposit
deposit = IborDeposit(
    trade_date,
    data_deposito,
    taxa_deposito,
    depoDCCType,
    cal_type=calendario,
)
OISdeposits.append(deposit)
# OIS swaps
OIS_swaps = []  # lista de todos os vertices da curva de swaps
swapType = SwapTypes.PAY
dcType = DayCountTypes.ACT_360  # THIRTY_E_360_ISDA
fixedFreq = FrequencyTypes.ANNUAL  # SEMI_ANNUAL
calendario = CalendarTypes.UNITED_STATES
settlement_date = Date(12, 11, 2026)
# vertices da curva de swap
range_data = [
    Date(12, 12, 2026),
    Date(12, 1, 2027),
    Date(12, 2, 2027),
    Date(12, 5, 2027),
    Date(12, 11, 2027),
    Date(12, 11, 2028),
    Date(12, 11, 2029),
    Date(12, 11, 2030),
    Date(12, 11, 2031),
    Date(12, 11, 2032),
    Date(12, 11, 2033),
    Date(12, 11, 2034),
    Date(12, 11, 2035),
    Date(12, 11, 2036),
    Date(12, 11, 2038),
    Date(12, 11, 2041),
    Date(12, 11, 2046),
    Date(12, 11, 2051),
    Date(12, 11, 2056),
]
range_taxa = [
    0.038900,
    0.040100,
    0.040555,
    0.041555,
    0.043145,
    0.043740,
    0.043760,
    0.043660,
    0.043645,
    0.043740,
    0.043900,
    0.044100,
    0.044355,
    0.044640,
    0.045225,
    0.045985,
    0.046580,
    0.046460,
    0.046015,
]
# adiciona todos os dados dos swaps
for i in range(len(range_taxa)):
    if range_data[i] is None or range_taxa[i] is None:
        # pula se nao tem data ou taxa
        continue
    else:
        # adiciona o vertice de swap
        swap = OIS(
            settlement_date,
            range_data[i],
            swapType,
            range_taxa[i],
            fixedFreq,
            dcType,
            1e6,
            2,
            0.0,
            fixedFreq,
            dcType,
            calendario,
        )
        # adiciona o swap a lista de swaps
        OIS_swaps.append(swap)
# cria a curva de juros OIS so com a SOFR e os swaps
Interest_types = InterpTypes.FLAT_FWD_RATES
curva_OIS = OISCurve(trade_date, OISdeposits, [], OIS_swaps, Interest_types)


""" Dados de CDS para teste da curva de sobrevivência """
accrual_start_date = Date(21, 9, 2026)
trade_date = Date(9, 11, 2026)
step_in_date = Date(10, 11, 2026)
settlement_date = Date(12, 11, 2026)
maturity_date = Date(20, 12, 2031)
recovery_rate = 0.25
cds_flat_spread = 0.0150
freq_type = FrequencyTypes(4)  # quarterly
# cria o vertice de CDS
cds_unique = CDS(
    step_in_date,
    maturity_date,
    cds_flat_spread,
    freq_type=freq_type,
    accrual_dc_type=DayCountTypes.ACT_360,
    prev_coupon_dt=accrual_start_date,
)
# cria a curva de sobrevivencia com o vertice de CDS
issuer_curve = CDSCurve(
    trade_date,
    [cds_unique],
    curva_OIS,
    recovery_rate,
    DayCountTypes.ACT_360,
    InterpTypes.FLAT_FWD_RATES,
)

# verifica a probabilidade de sobrevivencia para o primeiro e ultimo fluxo do CDS
survival_prob_first = issuer_curve.survival_prob(Date(21, 12, 2026))
survival_prob_last = issuer_curve.survival_prob(Date(20, 12, 2031))

delta_prob_first = 0.997737 - survival_prob_first
delta_prob_last = 0.901996 - survival_prob_last

print(
    f"prob. de sobrevivência do primeiro fluxo: {survival_prob_first:.8f} ->{delta_prob_first:.8f}"
)
print(
    f"prob. de sobrevivência do último fluxo: {survival_prob_last:.8f} -> {delta_prob_last:.8f}"
)
