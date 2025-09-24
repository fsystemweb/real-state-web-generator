# real-state-web-generator
This project provides a REST API that transforms structured property data (JSON) into SEO-optimized, multilingual HTML listings for real estate websites.
It uses FastAPI, LangChain, and OpenAI for generation and evaluation.

## Features
- ✅ Generates structured HTML (title, meta description, description, features, neighborhood, CTA)
- 🌍 Multilingual support: English 🇬🇧 and Portuguese  🇵🇹 and Spanish 🇪🇸
- 🔍 SEO keyword enrichment
- 🧪 Automatic evaluation of output:
    - Structure compliance
    - Language fluency & SEO
    - Multilingual adaptability

- 🔁 Retry mechanism: Up to 3 attempts if evaluation score < 3/5
- 📦 Modular design: Prompts stored separately for easier editing

## Installation
 - ```bash git clone https://github.com/fsystemweb/real-state-web-generator.git ```
 - ```bash cd real-state-web-generator ```

### Create virtual environment
 1. Create a virtual environment called "venv"
  - ```bash python3.12 -m venv venv ```
 2. Activate it
  * On Linux / macOS:
    - ```bash source venv/bin/activate ```
  * On Windows (PowerShell):
    - ```bash .\venv\Scripts\Activate.ps1 ```
 3. Install dependecies:
    - ```bash pip install -r requirements.txt ```

* Set environement variable
  - OPENAI_API_KEY=your_openai_api_key_here

## Running the API
 - ```bash python -m app.main ```

## Usage
Example Request:
- POST /generate-listing
```json
{
  "title": "T3 apartment in Lisbon",
  "location": {
    "city": "Lisbon",
    "neighborhood": "Campo de Ourique"
  },
  "features": {
    "bedrooms": 3,
    "bathrooms": 2,
    "area_sqm": 120,
    "balcony": true,
    "parking": false,
    "elevator": true,
    "floor": 2,
    "year_built": 2005
  },
  "price": 650000,
  "listing_type": "sale",
  "language": "en"
}
```

Example response: 
```json
{
  "html": "<title>...</title>\n<meta ... > ...",
  "evaluation": {
    "structure_compliance": 5,
    "language_fluency_seo": 4,
    "multilingual_adaptability": 4,
    "total_score": 4
  },
  "retries": 0,
  "failed_criteria_log": []
}
```

## Run app
 1. Start API
  - ```bash python -m app.main ```
 2. Start Webapp
  - ```bash python -m http.server 5500```
 3. Open browser on this url:
    - ```json http://localhost:5500/webapp.html ```


## Evaluation Criteria
Each generated listing is automatically evaluated against:

- ✅ Structure compliance (HTML tags + hierarchy)
- 📣 Language fluency & SEO effectiveness
- 🌍 Multilingual adaptability

Each criterion is scored 0–5. The total score must be ≥ 3 to be accepted.

## License
MIT License – free to use and modify.