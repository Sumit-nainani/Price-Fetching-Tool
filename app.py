# app.py

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from price_fetch import get_currency_from_country_code, price_tool  # noqa
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()


class ProductResponse(BaseModel):
    currency: str
    product: str
    websites: List[dict]


@app.get("/price", response_model=ProductResponse)
def get_product(country: str = Query(...), query: str = Query(...)):
    # currency = get_currency_from_country_code(country)
    # logging.info(
    #     f"Fetching price for product: {query} in country: {country} with currency: {currency}"
    # )
    logging.info(f"Fetching price for product: {query} in country: {country}")
    website_list = price_tool(country, query)

    return {"currency": "INR", "product": query, "price_list": website_list}
