def get_filter_prompt(results_json):
    return f"""
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


def get_price_extraction_prompt(results_json):
    return f"""
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


def get_detailed_analysis_prompt(content: str):
    return f"""
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
