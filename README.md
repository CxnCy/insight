# Insight 🔍

Insight is a data analysis app I built to make exploring a new dataset a little easier.

Upload a CSV and Insight automatically takes a look at the data, checks for common data quality issues, finds potential outliers and patterns, and creates interactive visualisations.

There's also an optional AI Analyst that takes the results from the analysis and explains the important findings in plain English.

## What it does

- Upload and preview CSV files
- Get a quick overview of the dataset
- Check missing values and duplicate rows
- Find constant and possible ID/index columns
- Flag potential data type issues
- Detect numerical outliers using the IQR method
- Spot possible inconsistencies in categorical data
- Explore numerical distributions
- Find correlations between numerical columns
- View top categories
- Generate interactive Plotly charts
- Get an overall Data Health Score
- Generate an optional AI summary of the analysis

## How it works

One of the main decisions I made while building Insight was to keep the actual data analysis separate from the AI.

```text
CSV
 ↓
Python Analysis
 ↓
Analysis Results
 ↓
Streamlit Dashboard
 ↓
Optional AI Analyst
```

Python handles the calculations and data checks. The AI Analyst only receives the results after the analysis is complete and helps explain them in plain English.

This means the core analysis still works without an API key or an AI service.

## Insight Core vs Insight AI

There are two versions of the app.

### Insight Core — `app_core.py`

The standalone version of Insight.

It includes the data analysis, quality checks, insights, and visualisations without requiring an API key.

### Insight AI — `app.py`

Includes everything in Insight Core, plus the optional AI Analyst.

You'll need your own OpenAI API key with available API credits to use the AI features.

## Built with

- Python
- Streamlit
- Pandas
- NumPy
- SciPy
- Plotly
- OpenAI API

## Getting started

Clone the repository:

```bash
git clone https://github.com/CxnCy/insight.git
cd insight
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Or on Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run Insight Core

If you just want to use the data analysis features, run:

```bash
streamlit run app_core.py
```

No API key needed.

## Run Insight AI

To use the AI Analyst, create a `.env` file in the project folder and add:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

You can use the included `.env.example` file as a reference.

Then run:

```bash
streamlit run app.py
```


## Why I built it

When working with a new dataset, there's usually a lot of repetitive checking before you can actually start digging into the interesting parts.

I built Insight to automate some of that initial exploration and bring the most useful information into one place.

The goal wasn't to have AI do the analysis itself. Instead, I wanted the calculations to stay deterministic and reproducible, while using AI where it's more useful: helping interpret and communicate the results.

## What's next

Insight is currently an MVP, so there's plenty I could add in the future:

- Excel file support
- Exportable analysis reports
- Downloadable cleaned datasets
- More statistical tests
- Better time-series analysis
- More visualisation options
- Cloud deployment

## Author

**CxnCy**