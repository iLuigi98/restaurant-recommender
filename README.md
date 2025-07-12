# Restaurant Recommender

An interactive app that recommends restaurants based on your favorites.

## Features
- Takes user restaurant preferences
- Returns personalized recommendations
- Built with Streamlit, APIs, and deep learning

## Project Layout
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

## Setup
```bash
git clone https://github.com/iLuigi98/restaurant-recommender.git
cd restaurant-recommender
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py