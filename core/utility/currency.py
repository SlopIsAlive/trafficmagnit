from iso4217 import Currency


def currency_by_code(iso_code: int) -> Currency:
    try:
        return next(c for c in Currency if c.number == iso_code)
    except StopIteration:
        raise ValueError(f"{iso_code} is not a valid ISO 4217 currency code")
