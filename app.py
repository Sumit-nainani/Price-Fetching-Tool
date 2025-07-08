from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from services.price_fetch import price_fetch
import logging
from utils.country_utils import get_currency_from_country_code

logging.basicConfig(level=logging.INFO)

app = FastAPI()


class ProductResponse(BaseModel):
    currency: str
    product: str
    price_list: List[dict]


@app.get("/price", response_model=ProductResponse)
def get_product(country: str = Query(...), query: str = Query(...)):
    currency = get_currency_from_country_code(country)
    logging.info(f"Fetching price for product: {query} in country: {country}")
    website_list = price_fetch(country, query)
    return {"currency": currency, "product": query, "price_list": website_list}
