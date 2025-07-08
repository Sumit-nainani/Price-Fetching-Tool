"""Country-related utility functions."""

import pycountry
from typing import Optional
from forex_python.converter import CurrencyRates


def get_country_name(country_code: str) -> str:
    """
    Get country name from country code.

    Args:
        country_code: Two-letter country code (e.g., 'IN', 'US')

    Returns:
        Country name or the original code if not found
    """
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        return country.name if country else country_code
    except Exception:
        return country_code


def get_currency_from_country_code(country_code: str) -> Optional[str]:
    """
    Get currency code from country code.

    Args:
        country_code: Two-letter country code

    Returns:
        Currency code or None if not found
    """
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if not country:
            return None

        # Try to get currency from pycountry
        currency = pycountry.currencies.get(numeric=country.numeric)
        if currency:
            return currency.alpha_3

        # Fallback using forex-python
        c = CurrencyRates()
        return c.get_currency_code(country.name)

    except Exception:
        return None
