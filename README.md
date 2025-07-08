# Price Comparison Tool

A FastAPI-based web application that searches for product prices across multiple sources using AI-powered filtering and web scraping. The application is deployed on Render and provides both REST API endpoints and a modular backend architecture.

## 🚀 Live API

**Base URL**: `https://price-fetching-tool.onrender.com`

## Features

- 🔍 **Multi-source Search**: Uses SERP API to search across multiple e-commerce platforms
- 🤖 **AI-powered Filtering**: Gemini AI identifies results with actual price information
- 🌐 **Web Scraping**: Firecrawl extracts prices from product pages
- 🚀 **FastAPI REST API**: High-performance web API with automatic documentation
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

![Screenshot](https://raw.githubusercontent.com/Sumit-nainani/Price-Fetching-Tool/main/images/result1.png)

![Screenshot](https://raw.githubusercontent.com/Sumit-nainani/Price-Fetching-Tool/main/images/result2.png)

![Screenshot](https://raw.githubusercontent.com/Sumit-nainani/Price-Fetching-Tool/main/images/result3.png)

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
    },
    {
      "link": "https://another-store.com/item",
      "price": "1049.00",
    }
  ]
}
```

## Usage Examples

### Using cURL

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
```

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
   cd repo_dir
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

