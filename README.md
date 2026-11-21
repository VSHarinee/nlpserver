```markdown
# Location-Based Reminder NLP Server

Backend service built with **FastAPI** and **spaCy** for extracting structured reminder details (`action`, `location`, `person`, and `confidence`) from natural-language text (including voice-to-text transcripts sent from a **Flutter** location-based reminder app) and learning from user corrections via an adaptive memory store.

## 🚀 Features

* **Location-Based Reminder Extraction (`POST /extract_reminder`):** Parses reminder text and an optional `friend_list` into `action`, `location`, `person`, and `confidence` for consumption by the Flutter client.
* **Person-First Pipeline & Fuzzy Matching:** Resolves friend names using exact matches, Levenshtein edit distance (for name spelling variations), `PERSON` / `PROPN` candidates, and optional spaCy vector similarity, then masks the person before extracting actions and locations.
* **Action & Location Parsing + Spell Correction:** Uses spaCy dependency/NER cues and regex fallbacks to extract actions and locations (such as landmarks or areas like *Reliance Mall* or *Five Roads*), plus `pyspellchecker` to clean action text.
* **Human-in-the-Loop Learning (`POST /learn`):** Stores user corrections in `adaptive_memory.json` when a user marks an extraction as incorrect (`NO` in the Flutter app) so future matching inputs bypass extraction and return the saved result.

## 🛠️ Tech Stack

* **Python**
* **FastAPI** & **Pydantic** (REST API, request validation, CORS)
* **spaCy (`en_core_web_sm`)** (lemmatization, POS tagging, dependency parsing, NER, similarity)
* **pyspellchecker** (action word spelling correction)
* **JSON (`adaptive_memory.json`)** (local adaptive memory storage)
* **Render** (cloud deployment)
* **Flutter** (client app for voice-to-text input, `YES/NO` confirmation UI, and real-world place/location handling)

## 📂 Project Structure

* `main.py` — FastAPI app, request models, CORS middleware, and endpoints (`/`, `/extract_reminder`, `/learn`).
* `reminder_engine.py` — Intent detection, person extraction/masking, action/location extraction, spell correction, confidence scoring, and memory persistence.
* `adaptive_memory.json` — Persisted dictionary mapping normalized (`strip().lower()`) input text to corrected reminder outputs.
* `requirements.txt` — Python dependencies.

## 📦 Getting Started

### Prerequisites

Make sure Python is installed on your system. Using a virtual environment is recommended:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### Installation

1. Clone the repository:

```bash
git clone [https://github.com/VSHarinee/nlpserver.git](https://github.com/VSHarinee/nlpserver.git)
cd nlpserver

```

2. Install dependencies and download the spaCy English model:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm

```

### Running the Server Locally

```bash
uvicorn main:app --reload

```

### Deploying on Render

* **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
* **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🔌 API Endpoints

### `POST /extract_reminder`

Example request from the Flutter app after voice-to-text conversion:

```json
{
  "text": "Remind me to buy shoes near Reliance Mall",
  "friend_list": ["Sowmiya", "Karthik"]
}

```

Example response:

```json
{
  "result": {
    "intent": "location_based_reminder",
    "action": "buy shoes",
    "location": "Reliance Mall",
    "person": "self",
    "confidence": 1.0
  },
  "message": "Check if this is correct (YES/NO in frontend)"
}

```

### `POST /learn`

Example request when the user taps **NO** in the Flutter app and submits a correction (e.g., *"Tell Sowmiya to pick up the parcel at Five Roads"*):

```json
{
  "original_text": "Tell Sowmiya to pick up the parcel at Five Roads",
  "action": "pick up the parcel",
  "location": "Five Roads",
  "person": "Sowmiya"
}

```

Example response:

```json
{
  "message": "Correction learned successfully ✅",
  "corrected_output": {
    "intent": "location_based_reminder",
    "action": "pick up the parcel",
    "location": "Five Roads",
    "person": "Sowmiya",
    "confidence": 1.0
  }
}

```

## ⚠️ Current Limitations

* `adaptive_memory.json` matches exact lowercased strings (`text.strip().lower()`) and writes to a local JSON file, so slight phrasing or voice-to-text variations won't hit the cache unless exact.
* Extraction relies on spaCy `en_core_web_sm`, rules/regexes, and edit-distance heuristics rather than a fine-tuned model.
* Real-world place resolution/geofencing and voice capture live in the companion Flutter app rather than this NLP service.

## 📄 License

This project is open-source and available under the MIT License.

