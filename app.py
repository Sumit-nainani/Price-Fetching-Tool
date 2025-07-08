# app.py

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from price_fetch import get_currency_from_country_code, price_tool

app = FastAPI()


class ProductResponse(BaseModel):
    currency: str
    product: str
    websites: List


@app.get("/price", response_model=ProductResponse)
def get_product(currency: str = Query(...), query: str = Query(...)):
    currency = get_currency_from_country_code(currency)
    website_list = price_tool(query, currency)

    return {"currency": currency, "product": query, "price_list": website_list}
