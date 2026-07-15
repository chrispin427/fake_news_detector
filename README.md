# AI Fake News Detector

An AI-powered fake news detection web app that combines **machine learning** with **real-time multi-source news verification**.

This project analyzes pasted news articles (or URLs) using a trained NLP model, cross-checks claims against multiple news/search APIs, and runs a battery of analytical signals through a **weighted verdict engine** to produce a final credibility score and explanation. It also features an **Evidence Quality Score** that rewards evidence coming from highly trusted publishers.

---

## Features

- **Machine Learning Classification** — Logistic Regression model with TF-IDF vectorization (~96% accuracy)
- **Multi-Source Evidence Retrieval** — Queries NewsAPI, GNews, NewsData, and SerpAPI for corroborating articles
- **Source Reputation Scoring** — 200+ known publishers rated 0–100 (e.g. Reuters=98, BBC=95, CNN=88)
- **Evidence Quality Score** — Deduplicates evidence sources, averages their reputation, and classifies as Excellent / High / Moderate / Weak / Poor
- **Fact Check Engine** — Compares extracted claims against evidence titles using similarity matching
- **Headline Analysis** — Detects clickbait, shock words, urgency phrases, and excessive capitalization
- **Content Manipulation Detection** — Flags rewritten or fabricated content by comparing claims to trusted sources
- **Sentiment Analysis** — Detects sensational language and emotional manipulation
- **Timeline Analysis** — Checks how recent an article is (penalizes recycled old news)
- **Risk Assessment** — Categorises content into Health, Political, Financial, or Scam risk
- **Source Consensus** — Measures agreement between the claim and evidence sources
- **Verdict Engine** — Multi-signal weighted system (source rep, evidence quantity, evidence quality, fact check, timeline, manipulation, headline, ML prediction)
- **PDF Report Generation** — Downloads a professional PDF report using ReportLab
- **Social Media Support** — Lower word thresholds for Facebook, X/Twitter, Instagram, TikTok, YouTube, Threads, LinkedIn
- **URL Fallback** — Automatically searches the web for related coverage when direct article extraction fails
- **Debug Audit Tool** — Full pipeline trace for diagnosing false positives/negatives
- **Streamlit Web UI** — Interactive interface with expandable advanced analysis sections

---

## How It Works

```
User Input (URL or pasted text)
   ↓
URL? → Extract article text (newspaper3k) → Fallback: web search
   ↓
Text Preprocessing (TF-IDF)
   ↓
ML Classifier (Logistic Regression)
   ↓
Multi-API Evidence Retrieval (NewsAPI, GNews, NewsData, SerpAPI)
   ↓
Parallel Analysis Pipeline:
   ├─ Fact Check (claim vs evidence)
   ├─ Headline Analysis (clickbait detection)
   ├─ Content Manipulation Detection
   ├─ Sentiment Analysis
   ├─ Timeline Analysis
   ├─ Risk Assessment
   ├─ Source Comparison (keyword overlap)
   ├─ Evidence Quality (publisher reputation)
   └─ Virality Estimation
   ↓
Weighted Verdict Engine (8 signals)
   ↓
Result: Score 0–100 + Verdict + Explanations + PDF/TXT Report
```

---

## Project Structure

```
fake_news_detector/
│
├── app/
│   └── app.py                     # Streamlit web application (entry point)
│
├── src/
│   ├── __init__.py                # Package marker
│   ├── analyzer.py                # ML model prediction wrapper
│   ├── claim_extractor.py         # Extracts main claim from article text
│   ├── credibility.py             # Legacy credibility scoring function
│   ├── data_cleaning.py           # Dataset cleaning for model training
│   ├── debug_audit.py             # Full pipeline diagnostic audit tool
│   ├── dynamic_reputation.py      # Advanced reputation signals (domain age, HTTPS)
│   ├── canonical_domain.py        # Resolves shortened/mobile URLs to canonical domains
│   ├── entity_extractor.py        # Named entity recognition (people, orgs, locations)
│   ├── evidence_finder.py         # Queries all 4 news APIs and deduplicates results
│   ├── evidence_pipeline.py       # Shared evidence retrieval pipeline (used by app + audit)
│   ├── evidence_quality.py        # Evidence Quality Score (publisher reputation averaging)
│   ├── explainer.py               # Legacy explanation generator
│   ├── ai_explainer.py            # AI-powered explanation generation
│   ├── fact_checker.py            # Verdict on claim support (Supported/Partially/Unsupported/Unverified)
│   ├── headline_checker.py        # Clickbait, shock word, urgency phrase detection
│   ├── news_api.py                # Legacy single-API verification functions
│   ├── predict.py                 # Model loading and prediction
│   ├── preprocess.py              # Text cleaning for ML pipeline
│   ├── query_builder.py           # Generates search query variants (title, claim, keywords, URL slug, entities)
│   ├── report_generator.py        # TXT and PDF report generation
│   ├── rewrite_detector.py        # Content manipulation detection via similarity scoring
│   ├── risk_detector.py           # Risk category detection (Health, Political, Financial, Scam)
│   ├── search_fallback.py         # Web search fallback when article extraction fails
│   ├── sentiment_analyzer.py      # Polarity and sensational word detection
│   ├── similarity_checker.py      # SequenceMatcher-based text comparison
│   ├── social_media.py            # URL detection helper
│   ├── social_preview.py          # Open Graph / preview metadata extraction
│   ├── source_comparison.py       # Keyword Jaccard + string similarity hybrid
│   ├── source_rating.py           # Publisher reputation scores (200+ domains, 0-100)
│   ├── test_queries.py            # Diagnostic test functions for the pipeline
│   ├── timeline_checker.py        # Article freshness analysis
│   ├── train.py                   # Model training script
│   ├── ui.py                      # Streamlit UI component functions
│   ├── url_extractor.py           # Article extraction from URL (newspaper3k)
│   ├── verdict_engine.py          # Multi-signal weighted verdict generator
│   └── virality_detector.py       # Virality level estimation from API result counts
│
├── model/
│   ├── model.pkl                  # Trained Logistic Regression model
│   └── vectorizer.pkl             # TF-IDF vectorizer
│
├── data/
│   └── cleaned_data.csv           # Training dataset
│
├── forensic_debug.py              # Standalone forensic diagnostic script
├── test_improvements.py           # Validation test suite (10 tests)
├── validate_evidence_quality.py   # Evidence Quality validation report with before/after comparison
├── api.md                         # API documentation
├── api_test.py                    # API connectivity tests
├── requirements.txt               # Python dependencies
├── .env                           # API keys (not committed)
└── README.md                      # This file
```

---

## File-by-File Descriptions

### Application Layer

| File | Purpose |
|---|---|
| `app/app.py` | **Streamlit entry point.** Handles user input, URL extraction, runs the full analysis pipeline, renders the verdict card and all analysis sections, provides TXT/PDF download. |
| `src/ui.py` | **UI components.** All Streamlit render functions: `render_verdict_card`, `render_evidence_section`, `render_fact_check_result`, `render_entity_metrics`, `render_source_verification`, `render_technical_metrics`, `render_sentiment_analysis`, `render_virality_analysis`, `render_timeline_analysis`, `render_risk_analysis`, `render_source_comparison`, `render_headline_analysis`, `render_rewrite_analysis`, `render_similarity_analysis`, `render_download_section`, and layout helpers. |

### Machine Learning

| File | Purpose |
|---|---|
| `src/preprocess.py` | **Text cleaning.** `clean_text()` — lowercasing, punctuation removal, stopword filtering for the ML pipeline. |
| `src/train.py` | **Model training.** Reads cleaned data, builds TF-IDF vectors, trains LogisticRegression, saves `model.pkl` and `vectorizer.pkl`. |
| `src/predict.py` | **Model inference.** `predict_news()` — loads the model and vectorizer, transforms text, returns prediction and confidence. |
| `src/analyzer.py` | **Analysis wrapper.** `analyze_article()` — loads model, preprocesses text, returns prediction (0/1), probabilities, and confidence. |

### Evidence Retrieval

| File | Purpose |
|---|---|
| `src/evidence_finder.py` | **Multi-API evidence retrieval.** Queries NewsAPI, GNews, NewsData, and SerpAPI for a given query. `find_evidence()` uses multiple query variants (title, claim, keywords, URL slug, entities) and deduplicates results across all variants. |
| `src/evidence_pipeline.py` | **Shared evidence pipeline.** `build_evidence_query()` — constructs the search query from article title/claim/text. `retrieve_evidence()` — fetches evidence and optionally supplements with search fallback results. `normalise_source()` — handles source being a string, dict, or None. `build_results_dict()` — counts evidence items per source. `compute_evidence_quality()` — delegates to the quality module. |
| `src/evidence_quality.py` | **Evidence Quality Score.** `compute_evidence_quality()` — deduplicates evidence sources, looks up each publisher's reputation score (via `source_rating.py`), averages them, and classifies: Excellent (90+), High (75-89), Moderate (60-74), Weak (40-59), Poor (0-39). Returns score, label, source count, and breakdown. Includes a PUBLISHER_NAME_MAP (170+ entries) to translate display names like "Reuters" to domain keys like "reuters.com". |
| `src/query_builder.py` | **Search query generator.** `build_queries()` — generates up to 7 query variants from title, claim, URL slug, keywords, and entities, prioritised by expected relevance. |
| `src/search_fallback.py` | **Web search fallback.** `search_from_failed_url()` — searches Google via DuckDuckGo when direct article extraction fails. `get_best_search_result()` — returns the most relevant search result. |

### Analysis Signals

| File | Purpose |
|---|---|
| `src/fact_checker.py` | **Fact check engine.** `fact_check()` — extracts a claim from the article, compares it against evidence titles using SequenceMatcher, returns verdict: Supported (≥3 matches), Partially Supported (≥1 match), Unsupported, or Unverified. |
| `src/claim_extractor.py` | **Claim extraction.** `extract_claim()` — extracts the first 3 meaningful sentences from article text as the primary claim. |
| `src/sentiment_analyzer.py` | **Sentiment analysis.** `analyze_sentiment()` — computes TextBlob polarity and counts sensational words (15 known words). Returns manipulation_risk: Low/Medium/High. |
| `src/headline_checker.py` | **Headline analysis.** `analyze_headline()` — checks for clickbait phrases, shock words, emotional manipulation, urgency phrases, excessive capitalization, and ALL CAPS. Returns risk (Low/Medium/High) and score (0-100). |
| `src/timeline_checker.py` | **Timeline analysis.** `check_timeline()` — determines if an article is Recent (<30 days), Not Recent (<1 year), or Old (≥1 year). Returns status and years_old. |
| `src/risk_detector.py` | **Risk assessment.** `detect_risk()` — scans text for Health, Political, Financial, and Scam keywords. Returns list of risk categories and a high_risk flag. |
| `src/virality_detector.py` | **Virality estimation.** `calculate_virality()` — estimates spread level (Low/Moderate/High/Very High) based on total API result mentions. |
| `src/rewrite_detector.py` | **Content manipulation.** `detect_rewrite()` — compares extracted claim against evidence titles via SequenceMatcher. Returns risk (Low/Medium/High/Unknown) and similarity percentage. |
| `src/source_comparison.py` | **Source consensus.** `compare_sources()` — hybrid approach: 70% keyword Jaccard similarity + 30% string similarity between claim and evidence titles. Returns agreement % and classification. |
| `src/similarity_checker.py` | **Text similarity.** `calculate_similarity()` — SequenceMatcher ratio between two text strings. |

### Source Reputation

| File | Purpose |
|---|---|
| `src/source_rating.py` | **Publisher reputation database.** `get_source_rating()` — looks up a URL's domain in a curated database of 200+ publishers rated 0-100. `SOURCE_SCORES` dictionary with scores for Reuters (98), AP (97), BBC (95), AFP (95), and many more. Labels: Highly Trusted (90+), Trusted (75+), Mixed Reliability (60+), Low Reliability. |
| `src/canonical_domain.py` | **Domain resolution.** `resolve_canonical_domain()` — resolves shortened URLs (e.g. aje.news → aljazeera.com), mobile subdomains (m.bbc.co.uk → bbc.com), and regional variants. |
| `src/dynamic_reputation.py` | **Dynamic reputation.** `compute_dynamic_reputation()` — adjusts base reputation based on HTTPS validity, domain age signals, and publisher consistency. |

### Entity Extraction

| File | Purpose |
|---|---|
| `src/entity_extractor.py` | **Named entity recognition.** `extract_entities()` — uses spaCy to extract people, organizations, locations, and dates from text. |

### URL Handling

| File | Purpose |
|---|---|
| `src/url_extractor.py` | **Article extraction.** `extract_article()` — uses newspaper3k to extract title, text, authors, and publish date from a URL. |
| `src/social_media.py` | **URL detection.** `is_url()` — regex-based URL validation. |
| `src/social_preview.py` | **Metadata preview.** `get_preview()` — extracts Open Graph metadata (title, description, image) from a URL. |

### Verdict Engine

| File | Purpose |
|---|---|
| `src/verdict_engine.py` | **Multi-signal verdict generator.** `generate_verdict()` — combines 8 weighted signals into a final score:
  - Source Reputation (35%)
  - External Evidence quantity (15%)
  - Evidence Quality (10%)
  - Fact Check (15%)
  - Timeline (10%)
  - Manipulation (5%)
  - Headline (5%)
  - ML Prediction (5%)

  Applies trusted-source overrides (sources with score ≥90 get a presumption of credibility) and fake-condition safeguards. Returns score, verdict (Highly Credible / Likely Credible / Mixed Evidence / Suspicious / Highly Suspicious), explanations, breakdown, and conditions_met. |

### Reporting

| File | Purpose |
|---|---|
| `src/report_generator.py` | **Report generation.** `generate_report()` — builds a structured report dict. `generate_report_text()` — creates a plain-text report. `generate_pdf()` — creates a professional PDF using ReportLab with color-coded verdicts, score breakdown tables, and evidence lists. |

### Auditing & Testing

| File | Purpose |
|---|---|
| `src/debug_audit.py` | **Pipeline diagnostic.** `audit_article()` — runs the full pipeline on any input and returns a structured trace with every intermediate signal. `print_audit()` — pretty-prints the trace showing source, claim, evidence, similarity, evidence quality, source agreement, rewrite, fact check, timeline, ML prediction, and the final verdict with breakdown. Usage: `python src/debug_audit.py "URL or text"` |
| `forensic_debug.py` | **Forensic diagnostic script.** Runs 5 test cases (BBC, AP, Reuters, fake text, Facebook-style) through the full pipeline and prints detailed per-stage diagnostics. |
| `test_improvements.py` | **Validation test suite.** 10 automated tests covering evidence_finder, rewrite_detector, source_comparison, timeline_checker, and verdict_engine edge cases. |
| `validate_evidence_quality.py` | **Evidence Quality validation.** Runs 10 test scenarios (BBC, Reuters, AP, Al Jazeera, CCTV, 3 regional publishers, clickbait, mixed quality) through both old and new scoring systems, comparing before/after scores. |
| `src/test_queries.py` | **Query diagnostic.** `diagnose_text()` and `diagnose_url()` — test functions to debug claim extraction and evidence retrieval. |
| `api_test.py` | **API connectivity tests.** Verifies that all configured news API keys work. |
| `api.md` | **API documentation.** Details on each third-party API used and their endpoints. |

### Legacy

| File | Purpose |
|---|---|
| `src/credibility.py` | **Legacy credibility score.** `calculate_credibility_score()` — simple weighted score from ML confidence and source verification. Superseded by `verdict_engine.py`. |
| `src/explainer.py` | **Legacy explanation generator.** Superseded by `verdict_engine.py`'s explanation logic. |
| `src/ai_explainer.py` | **AI explanation generator.** Generates human-readable explanations using LLMs (optional, requires API key). |
| `src/news_api.py` | **Legacy single-API verification.** Superseded by `evidence_finder.py`. |
| `src/database.py` | **Database utilities.** Schema and query helpers for persistent storage (optional). |

---

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd fake_news_detector

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download required NLTK data (stopwords, punkt, etc.)
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

# Download spaCy model (for entity extraction)
python -m spacy download en_core_web_sm
```

> **Note:** The app auto-downloads missing NLTK data on first use if not manually installed — the command above simply ensures everything is ready ahead of time.

### API Keys

Create a `.env` file in the project root:

```env
NEWS_API_KEY=your_key
GNEWS_API_KEY=your_key
NEWSDATA_API_KEY=your_key
SERP_API_KEY=your_key
```

Get free API keys from:
- [NewsAPI](https://newsapi.org/register) (free tier: 100 requests/day)
- [GNews](https://gnews.io/) (free tier: 100 requests/day)
- [NewsData](https://newsdata.io/) (free tier: 200 requests/day)
- [SerpAPI](https://serpapi.com/) (free tier: 100 searches/month)

> **Note:** The app runs without API keys but evidence retrieval will be limited. The ML model and local analysis signals (sentiment, headline, risk, timeline) work without any keys.

---

## Running the App

```bash
streamlit run app/app.py
```

The app opens at **http://localhost:8501**.

**Usage:**
1. Paste a news article URL or full article text
2. Click "Analyze Article"
3. View the verdict card, supporting evidence, and expandable advanced analysis
4. Download results as TXT or PDF

**Supported inputs:**
- Full news article URLs (bbc.com, reuters.com, etc.)
- Social media URLs (Facebook, X/Twitter, Instagram, TikTok, YouTube)
- Pasted article text (minimum 30 words for articles, 10 for social media)
- Claims or short statements (will be analyzed with limited evidence)

---

## Training the Model

To retrain the ML model from scratch:

```bash
# The training data should be in data/ directory as Fake.csv and True.csv
python src/data_cleaning.py
python src/train.py
```

This produces `model/model.pkl` and `model/vectorizer.pkl`.

The current pre-trained model achieves ~96% accuracy on the test set.

---

## Running Tests

```bash
# Validation test suite (10 tests, no API keys required)
python test_improvements.py

# Evidence Quality validation report
python validate_evidence_quality.py

# Debug audit on a specific article
python src/debug_audit.py "https://www.bbc.com/news/articles/..."

# Forensic diagnostic (5 test cases)
python forensic_debug.py
```

---

## Evidence Quality Score

The Evidence Quality Score (`src/evidence_quality.py`) evaluates the **credibility of supporting evidence** rather than just counting how many articles were found.

**How it works:**
1. Evidence items are collected from all 4 news APIs
2. Sources are **deduplicated** so 5 Reuters articles count as one (Reuters=98)
3. Each unique publisher's reputation score is looked up via `SOURCE_SCORES`
4. Unmatched sources get a neutral score of 50
5. All scores are averaged → final quality score (0-100)
6. Classified as **Excellent** (90+), **High** (75-89), **Moderate** (60-74), **Weak** (40-59), or **Poor** (0-39)

**Impact on verdicts:**
- The Evidence Quality Score contributes 10% of the final verdict weight
- Replaces part of the raw evidence quantity weight (reduced from 25% to 15%)
- Trusted wire services (BBC, Reuters, AP) receive **+4–5 points** boost
- Low-quality sources see minimal impact (~+1–2 points)
- Helps distinguish "lots of spammy sources" from "a few highly trusted sources"

---

## Verdict Categories

| Score Range | Verdict | Meaning |
|---|---|---|
| 90–100 | Highly Credible | Strong across all verification signals |
| 75–89 | Likely Credible | Generally trustworthy with minor concerns |
| 50–74 | Mixed Evidence | Conflicting signals — further verification recommended |
| 30–49 | Suspicious | Multiple red flags detected |
| 0–29 | Highly Suspicious | Strong indicators of misinformation |

---

## Tech Stack

- **Python 3.9+**
- **Streamlit** — Web UI framework
- **Scikit-learn** — ML model (Logistic Regression, TF-IDF)
- **Pandas** — Data processing
- **NLTK** — Text preprocessing
- **spaCy** — Named entity recognition
- **TextBlob** — Sentiment analysis
- **ReportLab** — PDF generation
- **BeautifulSoup4 / lxml** — HTML parsing
- **newspaper3k** — Article extraction
- **python-dotenv** — Environment configuration
- **Requests** — API calls

---

## License & Disclaimer

This tool is AI-generated and intended for **educational and reference purposes only**. It should NOT be used as a sole source of truth for news verification.

**Limitations:**
- ~96% ML accuracy does not guarantee correct classification of novel or breaking claims
- Evidence retrieval depends on third-party API availability
- Source reputation scores are curated manually and may not reflect current ownership changes
- The verdict engine's weights are tunable and may produce false positives/negatives

Users should conduct additional research and verify news using trusted sources.

---

## Author

Built as a bachelor project in Artificial Intelligence.

If this project interests you, feel free to connect on LinkedIn [www.linkedin.com/in/imena-chrispin-1360883b4] and share feedback.

---

## Star the Repo

If you find this project useful, please star the repository and share it with others.
