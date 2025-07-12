# Smart Restaurant Recommender

A personalized, content-based restaurant recommendation system for people moving or traveling to new cities. By learning from your past favorite restaurants in cities you've lived in, the system suggests places you'll likely enjoy in your new destination — before you even get there.

## Project Highlights

- **Content-Based Filtering** using restaurant descriptions, categories, and review scores
- **Semantic Matching** via sentence embeddings (Sentence-BERT)
- **Custom City-by-City Parsing** of restaurant datasets (cleaned and deduplicated)
- **Weighted Scoring Logic** combining rating, review count, and semantic similarity
- **Autocomplete Search** for cities and restaurants with real-time suggestions
- **User Preference Memory** (session or optional login)
- **Streamlit Web App** hosted on a personal domain for public interaction

## 📦 Features

| Feature                         | Description                                                  |
|----------------------------------|--------------------------------------------------------------|
| Multi-City Input              | Add favorite restaurants from cities you’ve lived in         |
| Personalized Recommendations | Find top restaurants in your **new** city                    |
| NLP-Based Similarity          | Uses vector similarity of restaurant descriptions            |
| Feature Weighting             | Review count + rating impact score more than rating alone    |
| Autocomplete Engine           | Smart dropdown for cities and restaurants                    |
| Deployed App                  | Fully hosted frontend using Streamlit on `luigidata.com`     |

---

## Project Layout
```
restaurant-recommender/
├── app/               # Streamlit or Gradio app files
│   └── main.py        # App entry point
├── data/              # Sample data, cached API results, etc.
├── notebooks/         # Jupyter notebooks for exploration and testing
├── src/               # Core logic (recommender, utils, API handlers)
│   └── recommender.py # Recommendation engine (initial version)
├── requirements.txt   # Python dependencies
├── .gitignore         # Ignored files/folders
├── README.md          # This file
└── venv/              # Python virtual environment (excluded from Git)
```

## How It Works

1. **Input your favorite restaurants** from past cities (e.g., LA, Houston, Chicago)
2. **Select your new city** (e.g., Knoxville)
3. The system:
    - Matches cuisine, category, and flavor profile
    - Weighs review count and rating
    - Embeds and compares descriptions using Sentence-BERT
4. Returns a ranked list of restaurant suggestions tailored to you

##  EDA Snapshots

Exploratory analysis performed on each city dataset includes:
- Distribution of star ratings
- Category distribution (e.g. “Mexican,” “BBQ”)
- Top restaurants by popularity
- Review-based word clouds for flavor patterns

## Tech Stack

| Layer         | Tools Used                                               |
|---------------|-----------------------------------------------------------|
| Language      | Python 3.12                                               |
| NLP & ML      | SentenceTransformers, scikit-learn                        |
| API Access    | Yelp Fusion API                                           |
| Web Scraping  | Playwright (Google Maps, TripAdvisor)                     |
| App Framework | Streamlit                                                |
| Deployment    | Vercel (frontend), GitHub Pages / Hugging Face (optional)|
| Data Storage  | In-memory / JSON / Optional user login (Firebase-ready)  |

---

## Run It Locally

```bash
git clone https://github.com/iLuigi98/restaurant-recommender.git
cd restaurant-recommender
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
```
