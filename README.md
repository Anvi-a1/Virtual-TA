# Virtual TA

A RAG-based question-answering API using FAISS for semantic search and Google Gemini for response generation.

## Live API

**Base URL:** https://virtual-ta-9gss.onrender.com

**Interactive Documentation:** https://virtual-ta-9gss.onrender.com/docs

## Endpoints

### GET /
Returns API information and available endpoints.

### GET /health
Check API health status and system information.

### POST /query
Submit questions and receive AI-generated answers with sources.

**Request Body:**
```
{
  "question": "Your question here"
}
```

**Response:**
```
{
  "answer": "Generated answer based on indexed content",
  "links": [
    {
      "url": "source_url",
      "text": "relevant snippet"
    }
  ]
}
```

## Usage Examples

### cURL
```
curl -X POST https://virtual-ta-9gss.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

### Python
```
import requests

response = requests.post(
    "https://virtual-ta-9gss.onrender.com/query",
    json={"question": "What is Python?"}
)
print(response.json())
```

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Installation
```
pip install -r requirements.txt
playwright install
```

### Environment Variables
Create a `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

### Run Locally
```
uvicorn app:app --reload
```

API will be available at http://localhost:8000

## Project Structure

- `app.py` - FastAPI application and query endpoint
- `embedding.py` - FAISS index generation and document processing
- `python_script.py` - Discourse forum scraper with authentication
- `python_scraper.py` - Simplified scraper implementation
- `requirements.txt` - Python dependencies

## Tech Stack

- **FastAPI** - Web framework
- **FAISS** - Vector similarity search
- **Google Gemini** - Embeddings and text generation
- **Playwright** - Web scraping
- **BeautifulSoup4** - HTML parsing

## Deployment

Deployed on Render with automatic deployments from the main branch.

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
uvicorn app:app --host 0.0.0.0 --port $PORT
```