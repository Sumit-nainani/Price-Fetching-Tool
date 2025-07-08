import os
import json
import re
import requests
import time
from firecrawl import FirecrawlApp
import google.generativeai as genai
from typing import List, Dict, Optional
from forex_python.converter import CurrencyRates
from dotenv import load_dotenv
import pycountry
import logging

# Configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

price_list = []


class PriceComparisonTool:
    def __init__(self):
        # Initialize API clients
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

    def get_country_name(self, country_code: str) -> str:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        return country.name

    def search_products(self, query: str, country: str) -> List[Dict]:
        search_query = f"{query} price in {self.get_country_name(country)} all stores"
        params = {
            "api_key": self.serp_api_key,
            "engine": "google",
            "q": search_query,
            "gl": country.lower(),
            "hl": "en",
            "num": 20,
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            return response.json().get("organic_results", [])
        except Exception as e:
            logger.error(f"SERP API error: {e}")
            return []

    def extract_price_from_snippet(self, snippet: str, title: str) -> Optional[Dict]:
        """Extract price information from search snippet"""
        # Common price patterns
        price_patterns = [
            r"[$£€¥₹]\s*[\d,]+\.?\d*",
            r"[\d,]+\.?\d*\s*[$£€¥₹]",
            r"Price:\s*[$£€¥₹]?\s*[\d,]+\.?\d*",
            r"₹\s*[\d,]+",
            r"\$\s*[\d,]+",
            r"£\s*[\d,]+",
            r"€\s*[\d,]+",
        ]

        text = f"{title} {snippet}".lower()

        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                price_str = matches[0]
                # Extract currency and amount
                currency_match = re.search(r"[$£€¥₹]", price_str)
                currency = currency_match.group() if currency_match else "USD"

                # Extract numeric value
                amount_match = re.search(r"[\d,]+\.?\d*", price_str)
                if amount_match:
                    return {
                        "price": amount_match.group().replace(",", ""),
                        "currency": currency,
                        "has_price": True,
                    }

        return {"has_price": False}

    def filter_results_for_scraping(self, search_results: List[Dict]) -> tuple:
        """Filter results that need scraping vs those with price in snippet"""
        results_with_price = []
        results_need_scraping = []

        for result in search_results:
            snippet = result.get("snippet", "")
            title = result.get("title", "")
            link = result.get("link", "")

            if not link:
                continue

            price_info = self.extract_price_from_snippet(snippet, title)

            if price_info.get("has_price"):
                results_with_price.append(
                    {
                        "link": link,
                        "title": title,
                        "snippet": snippet,
                        "price_info": price_info,
                    }
                )
            else:
                results_need_scraping.append(
                    {"link": link, "title": title, "snippet": snippet}
                )

        return results_with_price, results_need_scraping

    def _validate_product_data(self, item: Dict) -> bool:
        """Validate product data structure"""
        required_fields = ["link", "price", "currency", "productName"]
        return all(field in item and item[field] for field in required_fields)

    def scrape_websites(self, urls: List[str]) -> List[Dict]:
        """Scrape websites using Firecrawl"""
        scraped_data = []

        for url in urls[:10]:  # Limit to avoid rate limits
            try:
                result = self.firecrawl.scrape_url(
                    url, params={"formats": ["markdown"]}
                )
                if result.get("success"):
                    scraped_data.append(
                        {
                            "url": url,
                            "content": result.get("markdown", "")[
                                :5000
                            ],  # Limit content length
                        }
                    )
                    logger.info(f"Successfully scraped: {url}")
            except Exception as e:
                logger.error(f"Scraping error for {url}: {e}")
                continue

        return scraped_data

    def scrape_prices_with_firecrawl(self, results_without_price):
        try:
            # Initialize Firecrawl
            app = FirecrawlApp(api_key=self.firecrawl_api_key)

            for i, result in enumerate(results_without_price):
                link = result.get("link", "")

                if not link:
                    print(f"Skipping result {i}: No link found")
                    continue

                try:
                    # Scrape the webpage
                    scrape_result = app.scrape_url(
                        link,
                        formats=["markdown", "html"],
                        includeTags=[
                            "title",
                            "meta",
                            "h1",
                            "h2",
                            "h3",
                            "p",
                            "span",
                            "div",
                        ],
                        excludeTags=[
                            "script",
                            "style",
                            "nav",
                            "footer",
                            "header",
                        ],
                        waitFor=2000,  # Wait 2 seconds for dynamic content
                    )

                    content = ""
                    success = False

                    if hasattr(scrape_result, "__dict__"):
                        # Convert object to dict
                        result_dict = scrape_result.__dict__
                        success = result_dict.get("success", False)
                        content = result_dict.get("markdown", "") or result_dict.get(
                            "content", ""
                        )

                    elif hasattr(scrape_result, "success"):
                        success = scrape_result.success
                        content = getattr(scrape_result, "markdown", "") or getattr(
                            scrape_result, "content", ""
                        )

                    # Method 3: Try to access as dict
                    elif isinstance(scrape_result, dict):
                        success = scrape_result.get("success", False)
                        content = scrape_result.get(
                            "markdown", ""
                        ) or scrape_result.get("content", "")

                    elif hasattr(scrape_result, "data"):
                        data = scrape_result.data
                        if isinstance(data, dict):
                            success = data.get("success", False)
                            content = data.get("markdown", "") or data.get(
                                "content", ""
                            )

                    if success and content:
                        price_list.append(
                            {
                                "link": link,
                                "price": self.extract_price_from_content(content),
                            }
                        )

                    time.sleep(1)

                except Exception as e:
                    print(f"❌ Error scraping {link}: {str(e)}")

        except ImportError:
            print(
                "Firecrawl library not installed. Install with: pip install firecrawl-py"
            )

        except Exception as e:
            print(f"Error with Firecrawl: {e}")

    def extract_price_from_content(self, content: str) -> str:
        try:
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            prompt = f"""
            Extract the main product price from this webpage content.
            Look for the primary selling price, not shipping, tax, or promotional prices.
            CONTENT:
            {content} 
            INSTRUCTIONS:
            1. Find the main product price (iPhone, smartphone, etc.)
            2. Return the numeric value with currency symbols
            3. If multiple prices, choose the base/starting price
            4. Remove commas: "1,299" becomes "1299"
            5. Keep decimals: "999.99"
            6. If no price found, return "0"
            RESPONSE: Return only the numeric price value with currency symbols, nothing else.
            """
            response = model.generate_content(prompt)
            price = response.text.strip()
            price = re.sub(r"[^\d.]", "", price)
            return price if price else "0"

        except Exception as e:
            print(f"Gemini extraction failed: {e}, using regex fallback")

    def extract_prices_with_gemini(self, results_with_price):
        try:
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # Convert results to JSON string
            results_json = json.dumps(results_with_price, indent=2)

            prompt = f"""
            Extract price and link information from the following search results.
            
            INSTRUCTIONS:
            1. For each result, find the main price (ignore financing/monthly payments unless it's the only price)
            2. Extract the numeric price value WITH currency symbols (e.g. $, ₹, €, £, ¥, Rs, etc.)
            3. If multiple prices exist, choose the main product price (not shipping, tax, or monthly payments)
            4. Extract the main link/URL for each result
            5. Return ONLY a valid JSON array of objects
            
            SEARCH RESULTS:
            {results_json}
            
            REQUIRED OUTPUT FORMAT (JSON array only):
            [
              {{"link": "https://example.com/product", "price": " $999"}},
              {{"link": "https://another-site.com/item", "price": "1299 Rs"}}
            ]
            
            RULES:
            - Price should be numeric string with currency symbols
            - If price has decimals, keep them: "999.99"
            - If price has commas, remove them: "1,299" becomes "1299"
            - If no clear price found, use "0"
            - If no link found, use empty string ""
            - Return ONLY the JSON array, no other text
            
            JSON Array:
            """

            response = model.generate_content(prompt)
            response_text = response.text.strip()

            try:
                # Clean the response to extract JSON
                # Remove any markdown formatting
                response_text = re.sub(r"```json\s*", "", response_text)
                response_text = re.sub(r"```\s*", "", response_text)

                # Find JSON array in response
                json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    extracted_data = json.loads(json_str)

                    # Validate and clean the extracted data
                    cleaned_data = []
                    for item in extracted_data:
                        if (
                            isinstance(item, dict)
                            and "link" in item
                            and "price" in item
                        ):
                            # Clean price - remove any remaining currency symbols
                            price = str(item["price"]).strip()
                            price = re.sub(
                                r"[^\d.]", "", price
                            )  # Keep only digits and dots

                            cleaned_item = {
                                "link": str(item["link"]).strip(),
                                "price": price if price else "0",
                            }
                            cleaned_data.append(cleaned_item)

                    return cleaned_data
                else:
                    print("No valid JSON found in response")
                    return []

            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response was: {response_text}")
                return []

        except ImportError:
            print(
                "Google Generative AI library not installed. Install with: pip install google-generativeai"
            )
            return []
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return []

    def get_product_prices(self, country: str, query: str) -> List[Dict]:
        """Main function to get product prices"""
        logger.info(f"Searching for '{query}' in {country}")

        # Step 1: Search using SERP API
        results = self.search_products(query, country)
        if not results:
            logger.warning("No search results found")
            return []
        return results

    def filter_results_with_gemini_flexible(self, results):
        try:
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            results_json = json.dumps(results, indent=2)

            # Improved strict prompt
            prompt = f"""
            TASK: Identify search results that contain ACTUAL NUMERIC PRICE VALUES (not just price-related words).
    
            STRICT CRITERIA - Only include results that have:
            ✅ ACTUAL numeric prices with currency symbols: $999, ₹1,299, €500, £400, ¥1000
            ✅ ACTUAL numeric prices with currency words: Rs.999, USD 500, INR 25000
            ✅ ACTUAL pricing terms with numbers: MRP 999, Price: $500, Cost $299
            ✅ ACTUAL monthly/financing with numbers: $41.62/mo, Finance $33.34/month
    
            ❌ EXCLUDE results that only have:
            ❌ Generic price words without numbers: "prices", "pricing", "cost", "affordable"
            ❌ Vague mentions: "learn about prices", "check pricing", "best price"
            ❌ Just currency symbols without numbers: "$", "₹", "€"
            ❌ Zero values: "0.00", "$0", "Free"
    
            EXAMPLES:
            
            INCLUDE (Has actual prices):
            - "Buy iPhone for $999.00 with free shipping"
            - "Price was $33.34 per month, now $5.56 per month"
            - "Best price ₹1,19,900 with discount"
            - "MRP Rs.25,000 Special offer"
            
            EXCLUDE (No actual prices):
            - "Learn about prices and features"
            - "Check latest pricing and reviews"
            - "Colors, Price, Size, Reviews" (just mentions word "Price")
            - "Best price available" (no actual number)
    
            SEARCH RESULTS:
            {results_json}
    
            INSTRUCTIONS:
            1. Examine each result carefully
            2. Look for ACTUAL NUMERIC VALUES with currency indicators
            3. Ignore generic price-related words without numbers
            4. Return ONLY indices of results with real price numbers
    
            RESPONSE FORMAT: Return only a JSON array of indices (0-based)
            Example: [1, 3, 7] (if results at positions 1, 3, and 7 have actual prices)
    
            JSON Array:
            """

            response = model.generate_content(prompt)

            # Improved parsing logic
            try:
                response_text = response.text.strip()

                # Remove any markdown formatting
                response_text = re.sub(r"```json\s*", "", response_text)
                response_text = re.sub(r"```\s*", "", response_text)
                response_text = re.sub(r"JSON Array:\s*", "", response_text)

                # Multiple patterns to extract JSON array
                patterns = [
                    r"\[[\d,\s]*\]",  # Standard array format
                    r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]",  # Array with numbers
                    r"(\d+(?:\s*,\s*\d+)*)",  # Just comma-separated numbers
                ]

                indices_with_price = []

                for pattern in patterns:
                    json_match = re.search(pattern, response_text)
                    if json_match:
                        try:
                            if pattern == patterns[0]:  # Full array format
                                indices_with_price = json.loads(json_match.group())
                            else:  # Extract numbers and create array
                                numbers_str = (
                                    json_match.group(1)
                                    if len(json_match.groups()) > 0
                                    else json_match.group()
                                )
                                if numbers_str.strip():
                                    numbers = re.findall(r"\d+", numbers_str)
                                    indices_with_price = [
                                        int(n) for n in numbers if int(n) < len(results)
                                    ]
                                else:
                                    indices_with_price = []
                            break
                        except (json.JSONDecodeError, ValueError):
                            continue

                # Validate indices
                indices_with_price = [
                    i for i in indices_with_price if 0 <= i < len(results)
                ]

                print(f"Extracted indices: {indices_with_price}")  # Debug output

            except Exception as e:
                print(f"Error parsing Gemini response: {e}")
                print(f"Response was: {response_text}")
                indices_with_price = []

            # Split results based on indices
            results_with_price = []
            results_without_price = []

            for i, result in enumerate(results):
                if i in indices_with_price:
                    results_with_price.append(result)
                else:
                    results_without_price.append(result)

            global price_list
            price_list = self.extract_prices_with_gemini(results_with_price)

            self.scrape_prices_with_firecrawl(results_without_price)

        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return []


def get_currency_from_country_code(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())

        currency = pycountry.currencies.get(numeric=country.numeric)
        if currency:
            return currency.alpha_3

        # Fallback using forex-python
        c = CurrencyRates()
        return c.get_currency_code(country.name)

    except Exception as e:
        return f"Error: {str(e)}"


def price_tool(country, query):
    tool = PriceComparisonTool()

    # Test cases
    # test_cases = [
    #     {"country": "IN", "query": "iPhone 16 Pro, 128GB"},
    #     # {"country": "IN", "query": "boAt Airdopes 311 Pro"},
    # ]
    print("api called")
    results = tool.get_product_prices(country, query)

    tool.filter_results_with_gemini_flexible(results)

    with open(
        "/home/abhishek/Desktop/BharatX/results1.json", "w", encoding="utf-8"
    ) as f:
        json.dump(price_list, f, indent=2, ensure_ascii=False)

    # with open(
    #     "/home/abhishek/Desktop/BharatX/results2.json", "w", encoding="utf-8"
    # ) as f:
    #     json.dump(b, f, indent=2, ensure_ascii=False)

    return price_list

    # with open(
    #     "/home/abhishek/Desktop/BharatX/results2.json", "w", encoding="utf-8"
    # ) as f:
    #     json.dump(x, f, indent=2, ensure_ascii=False)


price_tool("IN", "iPhone 16 Pro, 128GB")
