# Price Comparison Tool

A FastAPI-based web application that searches for product prices across multiple sources using AI-powered filtering and web scraping. The application is deployed on Render and provides both REST API endpoints and a modular backend architecture.

## 🚀 Live API

**Base URL**: `https://price-fetching-tool.onrender.com`

## Features

- 🔍 **Multi-source Search**: Uses SERP API to search across multiple e-commerce platforms
- 🤖 **AI-powered Filtering**: Gemini AI identifies results with actual price information
- 🌐 **Web Scraping**: Firecrawl extracts prices from product pages
- 🌍 **Multi-country Support**: Search in different countries with localized results
- 📊 **Currency Detection**: Automatically detects and returns currency for each country
- 🚀 **FastAPI REST API**: High-performance web API with automatic documentation
- ☁️ **Cloud Deployed**: Hosted on Render for 24/7 availability
- 🏗️ **Modular Architecture**: Clean, maintainable code structure

## Project Structure

```
BharatX/
├── app.py                    # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment configuration
├── .env                     # Environment variables (not in repo)
├── .gitignore              # Git ignore rules
├── services/               # Core business logic
│   ├── __init__.py
│   ├── price_fetch.py      # Main price fetching logic
│   ├── model.py           # AI model configuration
│   └── prompt.py          # AI prompt templates
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── country_utils.py   # Country and currency utilities
└── data/                  # Data storage
    └── results.json       # Sample results
```

## API Documentation

### Get Product Prices

**Endpoint**: `GET /price`

**Parameters**:
- `country` (required): Two-letter country code (e.g., "US", "IN", "UK", "CA")
- `query` (required): Product search query (e.g., "iPhone 16 Pro 128GB")

**Response**:
```json
{
  "currency": "USD",
  "product": "iPhone 16 Pro 128GB",
  "price_list": [
    {
      "link": "https://example.com/product",
      "price": "999.99",
      "source": "gemini"
    },
    {
      "link": "https://another-store.com/item",
      "price": "1049.00",
      "source": "firecrawl"
    }
  ]
}
```

## Usage Examples

### 1. Using cURL

**Basic request**:
```bash
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=US" \
  --data-urlencode "query=iPhone 16 Pro, 128GB" \
  | jq
```

**iPhone pricing in different countries**:
```bash
# United States
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=US" \
  --data-urlencode "query=iPhone 16 Pro, 128GB" \
  | jq

# India
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=IN" \
  --data-urlencode "query=iPhone 16 Pro, 128GB" \
  | jq

# United Kingdom
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=UK" \
  --data-urlencode "query=iPhone 16 Pro, 128GB" \
  | jq
```

**Other products**:
```bash
# Samsung Galaxy S24
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=US" \
  --data-urlencode "query=Samsung Galaxy S24 Ultra" \
  | jq

# MacBook Pro
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=CA" \
  --data-urlencode "query=MacBook Pro M3 14 inch" \
  | jq

# PlayStation 5
curl -G "https://price-fetching-tool.onrender.com/price" \
  --data-urlencode "country=US" \
  --data-urlencode "query=PlayStation 5 console" \
  | jq
```

### 2. Using Python Requests

```python
import requests
import json

# Basic request
url = "https://price-fetching-tool.onrender.com/price"
params = {
    "country": "US",
    "query": "iPhone 16 Pro, 128GB"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Currency: {data['currency']}")
print(f"Product: {data['product']}")
print(f"Found {len(data['price_list'])} price results")

for i, result in enumerate(data['price_list'], 1):
    print(f"{i}. Price: {result['price']} - {result['link']}")
```

### 3. Using JavaScript/Fetch

```javascript
async function fetchPrices(country, query) {
    const url = new URL('https://price-fetching-tool.onrender.com/price');
    url.searchParams.append('country', country);
    url.searchParams.append('query', query);
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        console.log(`Currency: ${data.currency}`);
        console.log(`Product: ${data.product}`);
        console.log(`Found ${data.price_list.length} results`);
        
        data.price_list.forEach((result, index) => {
            console.log(`${index + 1}. Price: ${result.price} - ${result.source}`);
        });
        
        return data;
    } catch (error) {
        console.error('Error fetching prices:', error);
    }
}

// Usage
fetchPrices('US', 'iPhone 16 Pro, 128GB');
```

## Supported Countries

The API supports price searches in the following countries:

| Country Code | Country Name | Currency |
|--------------|--------------|----------|
| US | United States | USD |
| IN | India | INR |
| UK | United Kingdom | GBP |
| CA | Canada | CAD |
| AU | Australia | AUD |
| DE | Germany | EUR |
| FR | France | EUR |
| JP | Japan | JPY |
| SG | Singapore | SGD |
| BR | Brazil | BRL |

*Note: More countries can be added based on SERP API support*

## Local Development

### Prerequisites
- Python 3.8+
- API Keys for:
  - [SerpApi](https://serpapi.com/) - For search results
  - [Google Gemini AI](https://aistudio.google.com/) - For AI filtering
  - [Firecrawl](https://firecrawl.dev/) - For web scraping

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd BharatX
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   SERP_API_KEY=your_serp_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

5. **Run the application**:
   ```bash
   uvicorn app:app --reload
   ```

6. **Access the API**:
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

## API Keys Setup

### SERP API
1. Visit [SerpApi](https://serpapi.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Free tier: 100 searches/month

### Gemini AI
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the API key
4. Free tier: Generous usage limits

### Firecrawl
1. Visit [Firecrawl](https://firecrawl.dev/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Free tier: 500 pages/month

## Architecture

### Core Components

1. **FastAPI Application** (`app.py`)
   - REST API endpoints
   - Request/response models
   - Automatic documentation

2. **Price Fetching Service** (`services/price_fetch.py`)
   - SERP API integration
   - AI-powered result filtering
   - Web scraping coordination

3. **AI Model Management** (`services/model.py`)
   - Gemini AI model configuration
   - Model initialization and management

4. **Prompt Engineering** (`services/prompt.py`)
   - AI prompt templates
   - Structured prompts for filtering and extraction

5. **Utility Functions** (`utils/country_utils.py`)
   - Country code validation
   - Currency detection
   - Country name resolution

### Data Flow

1. **API Request** → FastAPI receives country and query parameters
2. **Search** → SERP API searches for products in specified country
3. **AI Filtering** → Gemini AI identifies results with actual prices
4. **Price Extraction** → AI extracts prices from search snippets
5. **Web Scraping** → Firecrawl scrapes additional prices from product pages
6. **Response** → Formatted JSON response with prices and metadata

## Error Handling

The API includes comprehensive error handling:

- **Invalid country codes**: Returns appropriate error messages
- **API key failures**: Graceful degradation when services are unavailable
- **Network timeouts**: Retry logic and fallback mechanisms
- **No results found**: Empty price list with appropriate status

## Performance

- **Response Time**: Typically 10-30 seconds depending on search complexity
- **Concurrent Requests**: Supports multiple concurrent requests
- **Rate Limiting**: Respects API provider rate limits
- **Caching**: Results can be cached for improved performance

## Deployment

The application is deployed on [Render](https://render.com/) using the included `render.yaml` configuration:

```yaml
services:
  - type: web
    name: fastapi-ai-app
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app:app --host 0.0.0.0 --port 8000"
    plan: free
```

### Deploy to Render

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service
4. Connect your forked repository
5. Add environment variables in Render dashboard
6. Deploy!

## Monitoring and Logs

- **Health Check**: `GET /` returns basic API information
- **Logs**: Available in Render dashboard
- **Metrics**: Request count, response times, error rates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

1. **API Issues**: Check the `/docs` endpoint for API documentation
2. **Rate Limits**: Monitor your API key usage on provider dashboards
3. **Performance**: Consider caching responses for repeated queries
4. **Bug Reports**: Create an issue in the GitHub repository

## Roadmap

- [ ] Response caching for improved performance
- [ ] Webhook support for price monitoring
- [ ] Additional search engines integration
- [ ] Price history tracking
- [ ] Email/SMS notifications for price drops
- [ ] GraphQL API support
- [ ] Advanced filtering and sorting options