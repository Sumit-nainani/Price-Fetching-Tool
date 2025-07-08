import os
import json
import re
import requests
import time
from firecrawl import FirecrawlApp
from typing import List, Dict
from dotenv import load_dotenv
import logging
from utils.country_utils import get_country_name
from .prompt import (
    get_filter_prompt,
    get_price_extraction_prompt,
    get_detailed_analysis_prompt,
)
from .model import get_model

# Configure logging
load_dotenv(".env")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

price_list = []


class PriceComparisonTool:
    def __init__(self):
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

    def search_products(self, query: str, country: str) -> List[Dict]:
        params = {
            "api_key": self.serp_api_key,
            "engine": "google",
            "q": f"{query} price in {get_country_name(country)} all stores",
            "gl": country.lower(),
            "hl": "en",
            "num": 30,
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            return response.json().get("organic_results", [])
        except Exception as e:
            logger.error(f"SERP API error: {e}")
            return []

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
                        waitFor=2000,
                    )

                    content = ""
                    success = False

                    if hasattr(scrape_result, "__dict__"):
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
                        price = self.extract_price_from_content(content)
                        if price != "0":
                            price_list.append(
                                {
                                    "link": link,
                                    "price": price,
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
            model = get_model(self.gemini_api_key)
            prompt = get_detailed_analysis_prompt(content)
            response = model.generate_content(prompt)
            price = response.text.strip()
            price = re.sub(r"[^\d.]", "", price)
            return price if price else "0"

        except Exception as e:
            print(f"Gemini extraction failed: {e}, using regex fallback")

    def extract_prices_with_gemini(self, results_with_price):
        try:
            model = get_model(self.gemini_api_key)
            results_json = json.dumps(results_with_price, indent=2)
            prompt = get_price_extraction_prompt(results_json)

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

        results = self.search_products(query, country)
        if not results:
            logger.warning("No search results found")
            return []

        return results

    def filter_results_with_gemini(self, results):
        try:
            model = get_model(self.gemini_api_key)
            results_json = json.dumps(results, indent=2)
            prompt = get_filter_prompt(results_json)

            response = model.generate_content(prompt)

            try:
                response_text = response.text.strip()
                response_text = re.sub(r"```json\s*", "", response_text)
                response_text = re.sub(r"```\s*", "", response_text)
                response_text = re.sub(r"JSON Array:\s*", "", response_text)

                # Multiple patterns to extract JSON array
                patterns = [
                    r"\[[\d,\s]*\]",
                    r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]",
                    r"(\d+(?:\s*,\s*\d+)*)",
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


def price_fetch(country, query):
    tool = PriceComparisonTool()

    results = tool.get_product_prices(country, query)

    print("api called")
    if len(results):
        tool.filter_results_with_gemini(results)
    else:
        print("No results found")

    return price_list
