# GPSC PYQ Mock Test Platform — PrepZone

A fully integrated **GPSC Mock Test Website** where you upload a **Previous Year Question Paper (PYQ) PDF** and **Answer Key PDF**, and the system automatically creates a structured mock test.

## Screenshots

| Landing Page | Mock Test Interface | Results & Analytics |
|:---:|:---:|:---:|
| ![Landing](https://github.com/user-attachments/assets/846f16e7-1793-4f70-9fc8-9aeaa15ce8b0) | ![Test](https://github.com/user-attachments/assets/096e1fd4-6f2b-4623-b110-cfebf6d9339a) | ![Results](https://github.com/user-attachments/assets/8152616d-3ebf-4325-bf70-6f2b32f9885d) |

---

## Features

- **PDF Upload** — Drag-and-drop upload for Question Paper and Answer Key PDFs
- **Intelligent Parsing** — Extracts all 200 questions from bilingual PDFs (Gujarati + English)
- **Answer Key Processing** — Auto-parses tabular answer keys; detects cancelled questions (⚠)
- **Subject Classification** — AI-based classification into 10 GPSC syllabus subjects
- **Real Exam Interface** — Timer, question navigation panel, mark for review, keyboard shortcuts
- **GPSC Marking Scheme** — +1 correct, −0.33 wrong, 0 not attempted, 0 cancelled
- **Result Analytics** — Subject-wise performance, accuracy, weak/strong areas, question review
- **Bilingual Support** — Toggle between English and Gujarati during the test

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
python app.py
```

The server starts at **http://localhost:5000**

### 3. Use the platform

1. Open http://localhost:5000 in your browser
2. Upload your **Question Paper PDF** and **Answer Key PDF**
3. Choose test settings (number of questions, time limit, language)
4. Click **Generate Mock Test**
5. Attempt the test, then submit for results

---

## Example Files

The repository includes sample GPSC files for testing:

| File | Description |
|---|---|
| `question_paper.pdf` | GPSC CSP-1 Question Paper (Bilingual, 200 Qs) |
| `answerkey.pdf` | GPSC CSP-1 Final Answer Key (200 answers) |

---

## PDF Format Support

**Question Paper:**
- Digital text PDFs (direct extraction)
- Scanned PDFs (OCR via Tesseract)
- Bilingual (Gujarati + English) — alternating pages
- English-only or Gujarati-only

**Answer Key:**
- Tabular format: `Q.No. Answer` columns
- Inline format: `1 A`, `2 B`, ...
- Cancelled questions marked with `*`

---

## Marking Scheme

| Result | Marks |
|--------|-------|
| Correct Answer | **+1** |
| Wrong Answer | **−0.33** |
| Not Attempted | **0** |
| Cancelled Question | **0** |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + Flask |
| PDF Parsing | pdfplumber |
| OCR (scanned PDFs) | pytesseract + Pillow |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Storage | JSON files (session-based) |

---

## Project Structure

```
├── app.py              # Flask backend (parsing, scoring, routes)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Landing/upload page
│   ├── test.html       # Mock test interface
│   └── results.html    # Results & analytics
├── static/
│   ├── css/style.css   # Global stylesheet
│   └── js/
│       ├── upload.js   # Upload form handling
│       └── test.js     # Test engine (timer, navigation, state)
├── uploads/            # Uploaded PDFs & session data (gitignored)
├── question_paper.pdf  # Sample PYQ (GPSC 2024)
└── answerkey.pdf       # Sample Answer Key (GPSC 2024)
```

---

## Keyboard Shortcuts (Test Mode)

| Key | Action |
|-----|--------|
| `A` / `B` / `C` / `D` | Select option |
| `→` / `←` | Next / Previous question |
| `R` | Mark for Review |
| `Esc` | Clear response |
