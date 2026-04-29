# AI Fake News Detector

An AI-powered fake news detection web app that combines **machine learning** with **real-time multi-source news verification**.

This project analyzes pasted news articles using a trained NLP model and cross-checks claims against multiple news/search APIs to help users assess whether content may be real, misleading, or suspicious.

---

## FEATURES

* **Machine Learning Classification**

  * Trained fake vs real news classifier using:

    * Python
    * Scikit-learn
    * TF-IDF Vectorization
    * Logistic Regression

* **Multi-Source Verification Layer**
  Cross-checks user input against:

  * NewsAPI
  * GNews API
  * NewsData API
  * SerpApi (Google Search verification)

* **Confidence Scoring**

  * Model prediction confidence
  * Verification score (matched sources / total sources)

* **Input Validation**

  * Rejects short prompts
  * Requires full article-style text (minimum word threshold)

* **Streamlit Web App UI**

  * Interactive interface
  * Source verification breakdown
  * AI disclaimer footer

---

## How It Works

User pastes article text:

1. Text is cleaned and preprocessed
2. TF-IDF converts text into features
3. ML model predicts fake or real
4. APIs search for corroborating evidence
5. App combines ML + source verification for final result

Architecture:

```text
User Input
   ↓
Text Preprocessing
   ↓
ML Classifier
   ↓
Multi-API Verification
   ↓
Combined Analysis Result
```

---

## Project Structure

```bash
fake_news_detector/
│
├── app/
│   └── app.py
│
├── src/
│   ├── preprocess.py
│   ├── train.py
│   ├── predict.py
│   ├── news_api.py
│   ├── data_cleaning.py
│   └── ui.py
│
├── model/
│   ├── model.pkl
│   └── vectorizer.pkl
│
├── data/
│   ├── Fake.csv
│   ├── True.csv
│   └── cleaned_data.csv
│
├── .env
├── requirements.txt
└── README.md

```

---

## ⚙️ Installation

Create virtual environment:

```bash
python -m venv venv
```

Activate:

Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
NEWS_API_KEY=your_key
GNEWS_API_KEY=your_key
NEWSDATA_API_KEY=your_key
SERP_API_KEY=your_key
```

Never commit `.env`.

Add to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
```

---

## ▶ Run the App

```bash
streamlit run app/app.py
```

App will open in browser:

```text
http://localhost:8501
```

---

## 🧪 Train the Model

(Optional retraining)

```bash
python src/data_cleaning.py
python src/train.py
```

---

## Current Model

* Model: Logistic Regression
* Vectorizer: TF-IDF
* Dataset: Combined real + fake news corpus
* Accuracy: ~96%

*Accuracy does not guarantee truth detection for novel or breaking claims. Cross-verification is essential.*

---

## Disclaimer

This tool is AI-generated and intended for reference only.
Users should conduct additional research and verify news using trusted sources.

---

## 🛠 Future Improvements

Possible next upgrades:

* Claim-level fact checking with LLMs
* Bias detection analysis
* Source credibility scoring
* Misinformation trend dashboard
* User analytics
* Article URL ingestion
* Video/deepfake detection expansion

---

## Tech Stack

* Python
* Streamlit
* Scikit-learn
* Pandas
* Requests
* python-dotenv

---

## Author

Built as a bachelor project in Artificial Intelligence.

If this project interests you, feel free to connect on LinkedIn and share feedback.

---

## If You Like It

Star the repo and share it.
