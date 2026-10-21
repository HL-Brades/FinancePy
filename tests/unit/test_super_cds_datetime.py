import datetime as dt

from financepy.super_cds import _ensure_utc_datetime


def test_ensure_utc_datetime_assigns_utc_to_naive_excel_timestamp():
    value = dt.datetime(2026, 10, 21, 12, 0)

    assert _ensure_utc_datetime(value) == value.replace(tzinfo=dt.timezone.utc)


def test_ensure_utc_datetime_converts_aware_timestamp_to_utc():
    value = dt.datetime(
        2026, 10, 21, 15, 0, tzinfo=dt.timezone(dt.timedelta(hours=3))
    )

    assert _ensure_utc_datetime(value) == dt.datetime(
        2026, 10, 21, 12, 0, tzinfo=dt.timezone.utc
    )
