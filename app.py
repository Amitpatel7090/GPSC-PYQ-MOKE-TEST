"""
GPSC PYQ Mock Test Platform
A comprehensive platform for GPSC exam preparation using Previous Year Questions.
"""
import os
import re
import json
import uuid
import logging
from pathlib import Path

import pdfplumber
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gpsc-mock-test-secret-key-2024")
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Subject classification keywords
# ---------------------------------------------------------------------------

SUBJECT_KEYWORDS = {
    "Indian Polity": [
        "constitution", "parliament", "president", "governor", "article",
        "fundamental rights", "directive principles", "lok sabha", "rajya sabha",
        "supreme court", "high court", "amendment", "preamble", "citizenship",
        "election commission", "attorney general", "comptroller", "rajyapal",
        "judge", "judiciary", "federal", "union", "state list",
        "concurrent", "emergency", "impeachment", "cabinet", "council of ministers",
        "prime minister", "chief minister", "speaker", "vice president",
        "fundamental duties", "dpsp", "rajya", "lok", "writ", "habeas corpus",
        "public interest litigation", "pil", "electoral", "vote",
    ],
    "History of India": [
        "mughal", "british", "independence", "gandhi", "nehru", "revolt",
        "civil disobedience", "quit india", "maurya", "gupta", "harsha",
        "maratha", "ashoka", "chandragupta", "swadeshi", "partition",
        "viceroy", "governor general", "lord", "company", "east india",
        "sepoy", "rani", "sultan", "khalji", "tughlaq", "lodi", "delhi sultanate",
        "bahmani", "vijayanagara", "akbar", "aurangzeb", "shivaji",
        "first war of independence", "battle", "treaty", "samiti",
        "mahajanapada", "magadha", "kosala", "pataliputra", "nanda",
        "pushyamitra", "kharoshti", "brahmi", "pallava", "chola", "rashtrakuta",
        "chandellas", "chaulukya", "ghurid", "slave dynasty", "khilji",
        "sayyid", "lodi", "sur", "babur", "humayun", "jahangir", "shahjahan",
        "social reform", "sati", "widow remarriage", "brahmo samaj", "arya samaj",
        "prarthana samaj", "indian national congress", "boycott", "moderates",
        "extremists", "tilak", "gokhale", "lajpat rai", "bipin chandra pal",
        "revolutionary", "bhagat singh", "subhas chandra bose", "non-cooperation",
        "khilafat", "rowlatt", "jallianwala", "salt march", "dandi",
        "bamiyan", "silk route", "inscriptions", "edict", "pillar",
        "jury act", "hindu college", "vernacular press", "age of consent",
        "hunter commission", "wood's dispatch", "minto morley", "montagu",
        "simon commission", "round table", "cripps", "wavell",
        "chauth", "sardeshmukhi", "peshwa", "maratha confederacy",
        "portuguese", "french", "dutch", "danish", "colonial",
        "vasco da gama", "albuquerque", "almeida", "dupleix",
    ],
    "History of Gujarat": [
        "gujarat", "junagadh", "somnath", "sardar patel", "patel",
        "baroda", "vadodara", "ahmedabad", "surat", "rajkot", "gandhinagar",
        "rani sipri", "rani ki vav", "dholavira", "lothal", "solanki",
        "chaulukya", "gaekwad", "sayajirao", "gujarat sultanate", "mahmud begada",
        "cut", "bharuch", "bhavnagar",
    ],
    "Geography": [
        "river", "mountain", "plateau", "climate", "soil", "ocean", "sea",
        "lake", "tropical", "latitude", "longitude", "mineral", "rainfall",
        "monsoon", "desert", "peninsula", "gulf", "strait", "cape",
        "watershed", "delta", "estuary", "tidal", "continental", "tectonic",
        "himalayas", "deccan", "vindhya", "arabian", "bay of bengal",
        "black soil", "alluvial", "narmada", "sabarmati", "tapti",
        "jet stream", "atmosphere", "tropic", "equator", "arctic",
        "pass", "zoji la", "bara lacha", "jelep la", "niti pass",
        "indo-gangetic", "flood plain", "gorge", "meander", "tributary",
        "western ghats", "eastern ghats", "aravalli", "satpura",
        "brahmaputra", "ganga", "yamuna", "indus", "krishna", "cauvery",
    ],
    "Economy": [
        "economy", "gdp", "inflation", "budget", "reserve bank", "rbi",
        "tax", "niti aayog", "planning commission", "five year plan",
        "poverty", "unemployment", "fiscal", "monetary", "credit",
        "wto", "imf", "world bank", "msme", "fdi", "gst", "disinvestment",
        "public sector", "private sector", "green revolution", "white revolution",
        "harrod-domar", "advance estimates", "gva", "purchasing power",
        "direct tax", "indirect tax", "subsidies", "revenue", "capital",
        "trade deficit", "balance of payment", "current account",
        "inflation", "deflation", "stagflation", "recession",
    ],
    "Science & Technology": [
        "science", "physics", "chemistry", "biology", "space", "isro",
        "technology", "satellite", "nuclear", "atom", "molecule", "cell",
        "dna", "rna", "protein", "vitamin", "disease", "vaccine", "antibiotic",
        "internet", "computer", "artificial intelligence", "robot",
        "electric", "magnetic", "newton", "einstein", "periodic table",
        "hcf", "lcm", "nanotechnology", "biotechnology", "genome",
        "crispr", "quantum", "semiconductor", "photosynthesis",
        "respiration", "metabolism", "enzyme", "hormone", "neuron",
        "sphere", "cylinder", "cone", "curved surface area",
    ],
    "Environment": [
        "environment", "ecology", "pollution", "climate change", "biodiversity",
        "wildlife", "forest", "national park", "sanctuary", "greenhouse gas",
        "carbon", "ozone", "acid rain", "species", "endangered", "biosphere",
        "wetland", "mangrove", "coral reef", "tiger", "lion", "elephant",
        "net-zero", "carbon neutral", "renewable energy", "solar", "wind energy",
        "paris agreement", "kyoto", "cop", "unfccc", "emission",
        "tiger reserve", "kawal", "biosphere reserve",
    ],
    "Current Affairs": [
        "recent", "2023", "2024", "summit", "award", "scheme", "mission",
        "g20", "g7", "brics", "sco", "nato", "united nations", "who",
        "covid", "pandemic", "digital india", "startup", "unicorn",
        "olympic", "commonwealth", "asian games", "d-sii", "net-zero",
        "insurance", "domestic systemically", "advance estimates", "fae",
    ],
    "Culture": [
        "dance", "music", "art", "festival", "culture", "religion", "temple",
        "heritage", "craft", "classical", "folk", "bharat natyam", "kathak",
        "garba", "navratri", "diwali", "eid", "christmas", "pongal",
        "rann utsav", "kite festival", "tribal", "handicraft",
        "bamiyan", "silk", "buddha", "buddhist", "jain", "jainism",
        "hinduism", "islam", "christianity", "sikhism",
        "giddha", "ghoomar", "bhangra", "kuchipudi", "odissi",
        "carnatic", "hindustani", "tansen", "bhimsen joshi", "ravi shankar",
        "pandit", "classical music", "tabla", "sitar", "veena",
        "painting", "sculpture", "architecture", "monument", "cave",
        "ajanta", "ellora", "khajuraho", "mahabalipuram", "elephanta",
        "philosophy", "vedanta", "mimansa", "sankhya", "vaisheshika",
        "yoga", "nyaya", "shankaracharya", "ramanuja",
    ],
    "Reasoning / Aptitude": [
        "probability", "average", "series", "arithmetic", "logical", "reasoning",
        "consecutive", "natural numbers", "square", "cube", "ratio",
        "percentage", "profit", "loss", "interest", "time", "work",
        "distance", "speed", "clock", "calendar", "coding", "decoding",
        "hcf", "lcm", "sum of", "remainder", "divisible", "digit",
        "triangle", "perimeter", "area", "volume", "sphere", "cylinder",
        "probability", "toss", "coin", "dice", "combination", "permutation",
        "train", "bridge", "stream", "boat", "upstream", "downstream",
        "efficient", "alone", "together", "fraction", "decimal",
    ],
}


def classify_subject(question_text: str) -> str:
    """Return best-matching subject for the given question text."""
    text_lower = question_text.lower()
    scores = {subject: 0 for subject in SUBJECT_KEYWORDS}
    for subject, keywords in SUBJECT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[subject] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General"


# ---------------------------------------------------------------------------
# PDF parsing helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(pdf_path: str) -> list[str]:
    """Return a list of page texts extracted from a PDF."""
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text)
    except Exception as exc:
        logger.error("PDF extraction error: %s", exc)
    return pages


def is_english_page(text: str) -> bool:
    """Detect whether a page is primarily English (vs. Gujarati)."""
    if not text:
        return False
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) >= 0.95


def _split_questions_by_number(combined: str) -> list[tuple[int, str]]:
    """
    Split combined page text into (question_number, body) pairs.
    Uses 3-digit zero-padded numbers (e.g. 001–200) as question boundaries
    to avoid confusing intra-question statement numbers (1., 2., 3.) with real
    question markers.

    First-occurrence wins: if a question number appears twice (e.g. two exam
    papers in the same PDF), only the first occurrence is returned.
    """
    pattern = re.compile(r"(?:^|\n)(\d{3})\.\s+", re.MULTILINE)
    matches = list(pattern.finditer(combined))

    result: list[tuple[int, str]] = []
    seen: set[int] = set()
    for i, m in enumerate(matches):
        q_num = int(m.group(1))
        if q_num < 1 or q_num > 300:
            continue
        if q_num in seen:
            continue  # skip duplicate (second paper in the same PDF)
        seen.add(q_num)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(combined)
        body = combined[start:end].strip()
        result.append((q_num, body))

    return result


def parse_english_questions(pages: list[str]) -> dict[int, dict]:
    """
    Parse English-language question pages.
    Returns {question_number: {text, option_a, option_b, option_c, option_d}}.
    """
    questions: dict[int, dict] = {}

    # Combine all English page texts
    combined = "\n".join(p for p in pages if is_english_page(p))
    combined = re.sub(r" {2,}", " ", combined)

    opt_pattern = re.compile(
        r"\(A\)\s*(.+?)\s*\(B\)\s*(.+?)\s*\(C\)\s*(.+?)\s*\(D\)\s*(.+?)$",
        re.DOTALL,
    )

    for q_num, body in _split_questions_by_number(combined):
        body = body.strip()

        opt_match = opt_pattern.search(body)
        if opt_match:
            q_text = body[: opt_match.start()].strip()
            q_text = re.sub(r"\n+", " ", q_text).strip()
            options = [g.strip().replace("\n", " ") for g in opt_match.groups()]
        else:
            q_text = re.sub(r"\n+", " ", body).strip()
            options = ["", "", "", ""]

        questions[q_num] = {
            "question_number": q_num,
            "question_text_english": q_text,
            "option_a": options[0],
            "option_b": options[1],
            "option_c": options[2],
            "option_d": options[3],
        }

    return questions


def parse_gujarati_questions(pages: list[str]) -> dict[int, str]:
    """
    Parse Gujarati-language question pages.
    Returns {question_number: question_text_gujarati}.
    """
    questions: dict[int, str] = {}

    combined = "\n".join(p for p in pages if not is_english_page(p))
    combined = re.sub(r" {2,}", " ", combined)

    for q_num, body in _split_questions_by_number(combined):
        body = body.strip()
        opt_idx = re.search(r"\(A\)", body)
        if opt_idx:
            body = body[: opt_idx.start()].strip()
        body = re.sub(r"\n+", " ", body).strip()
        questions[q_num] = body

    return questions


def parse_question_paper(pdf_path: str) -> list[dict]:
    """
    Full pipeline: extract, parse, classify, and return list of question dicts.
    """
    pages = extract_text_from_pdf(pdf_path)
    english_qs = parse_english_questions(pages)
    gujarati_qs = parse_gujarati_questions(pages)

    merged: list[dict] = []
    for q_num in sorted(english_qs.keys()):
        q = english_qs[q_num].copy()
        q["question_text_gujarati"] = gujarati_qs.get(q_num, "")
        q["subject"] = classify_subject(q.get("question_text_english", ""))
        q["difficulty_level"] = "Medium"
        q["correct_answer"] = ""
        q["is_cancelled"] = False
        merged.append(q)

    return merged


def parse_answer_key(pdf_path: str) -> tuple[dict[int, str], list[int]]:
    """
    Parse the answer key PDF.
    Returns (answers_dict, cancelled_list) where answers_dict maps
    question number → answer letter ('A'/'B'/'C'/'D') or '*' for cancelled.
    """
    pages = extract_text_from_pdf(pdf_path)
    answers: dict[int, str] = {}
    cancelled: list[int] = []

    for page_text in pages:
        # Match "q_num A/B/C/D" or "q_num *"
        # Use lookahead/lookbehind to avoid consuming surrounding digits
        for match in re.finditer(r"(?<!\d)(\d{1,3})\s+([ABCD\*])(?!\w)", page_text):
            q_num = int(match.group(1))
            answer = match.group(2)
            if 1 <= q_num <= 300 and q_num not in answers:
                answers[q_num] = answer
                if answer == "*":
                    cancelled.append(q_num)

    return answers, cancelled


def merge_answers_into_questions(
    questions: list[dict],
    answers: dict[int, str],
    cancelled: list[int],
) -> list[dict]:
    """Attach correct answers and cancellation flags to questions."""
    for q in questions:
        q_num = q["question_number"]
        q["correct_answer"] = answers.get(q_num, "")
        q["is_cancelled"] = q_num in cancelled
    return questions


# ---------------------------------------------------------------------------
# Subject statistics helper
# ---------------------------------------------------------------------------

def compute_subject_stats(questions: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for q in questions:
        subj = q.get("subject", "General")
        counts[subj] = counts.get(subj, 0) + 1
    return [{"subject": s, "count": c} for s, c in sorted(counts.items(), key=lambda x: -x[1])]


# ---------------------------------------------------------------------------
# Score calculation
# ---------------------------------------------------------------------------

CORRECT_MARKS = 1.0
WRONG_MARKS = -1 / 3
NOT_ATTEMPTED_MARKS = 0.0


def calculate_results(questions: list[dict], user_answers: dict[str, str]) -> dict:
    """
    Calculate score and per-subject analytics.
    user_answers: {str(question_number): 'A'/'B'/'C'/'D'/''}.
    """
    total_questions = len(questions)
    correct = 0
    wrong = 0
    not_attempted = 0
    cancelled_skipped = 0
    subject_stats: dict[str, dict] = {}

    for q in questions:
        q_num = str(q["question_number"])
        subj = q.get("subject", "General")
        correct_ans = q.get("correct_answer", "")
        user_ans = user_answers.get(q_num, "")
        is_cancelled = q.get("is_cancelled", False)

        if subj not in subject_stats:
            subject_stats[subj] = {"correct": 0, "wrong": 0, "not_attempted": 0, "score": 0.0}

        if is_cancelled:
            cancelled_skipped += 1
            continue

        if not user_ans:
            not_attempted += 1
            subject_stats[subj]["not_attempted"] += 1
        elif user_ans == correct_ans:
            correct += 1
            subject_stats[subj]["correct"] += 1
            subject_stats[subj]["score"] += CORRECT_MARKS
        else:
            wrong += 1
            subject_stats[subj]["wrong"] += 1
            subject_stats[subj]["score"] += WRONG_MARKS

    attempted = correct + wrong
    raw_score = correct * CORRECT_MARKS + wrong * WRONG_MARKS
    max_score = (total_questions - cancelled_skipped) * CORRECT_MARKS
    accuracy = round((correct / attempted * 100) if attempted > 0 else 0, 1)

    # Identify weak/strong subjects
    scored_subjects = [
        {"subject": s, **v}
        for s, v in subject_stats.items()
        if (v["correct"] + v["wrong"]) > 0
    ]
    scored_subjects.sort(key=lambda x: x["score"])

    weak = [s["subject"] for s in scored_subjects[:3] if s["score"] < 0]
    strong = [s["subject"] for s in reversed(scored_subjects) if s["score"] > 0][:3]

    return {
        "total_questions": total_questions,
        "attempted": attempted,
        "correct": correct,
        "wrong": wrong,
        "not_attempted": not_attempted,
        "cancelled_skipped": cancelled_skipped,
        "raw_score": round(raw_score, 2),
        "max_score": max_score,
        "accuracy": accuracy,
        "subject_stats": subject_stats,
        "weak_subjects": weak,
        "strong_subjects": strong,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle PDF upload and parse questions + answer key."""
    if "question_paper" not in request.files or "answer_key" not in request.files:
        return jsonify({"error": "Both question paper and answer key PDFs are required."}), 400

    qp_file = request.files["question_paper"]
    ak_file = request.files["answer_key"]

    if not (qp_file.filename and allowed_file(qp_file.filename)):
        return jsonify({"error": "Question paper must be a PDF file."}), 400
    if not (ak_file.filename and allowed_file(ak_file.filename)):
        return jsonify({"error": "Answer key must be a PDF file."}), 400

    test_id = str(uuid.uuid4())
    qp_path = UPLOAD_FOLDER / f"{test_id}_qp.pdf"
    ak_path = UPLOAD_FOLDER / f"{test_id}_ak.pdf"

    qp_file.save(str(qp_path))
    ak_file.save(str(ak_path))

    try:
        questions = parse_question_paper(str(qp_path))
        answers, cancelled = parse_answer_key(str(ak_path))
        questions = merge_answers_into_questions(questions, answers, cancelled)
    except Exception as exc:
        logger.error("Parsing error: %s", exc)
        return jsonify({"error": f"Failed to parse PDFs: {exc}"}), 500

    if not questions:
        return jsonify({"error": "No questions could be extracted. Please check the PDF format."}), 400

    # Persist to file (avoid bloating the session cookie)
    data_path = UPLOAD_FOLDER / f"{test_id}_data.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False)

    subject_stats = compute_subject_stats(questions)

    return jsonify({
        "test_id": test_id,
        "total_questions": len(questions),
        "cancelled_count": len(cancelled),
        "subject_stats": subject_stats,
    })


@app.route("/test/<test_id>")
def test_page(test_id: str):
    """Render the mock test interface."""
    if not re.match(r"^[0-9a-f\-]{36}$", test_id):
        flash("Invalid test ID.", "error")
        return redirect(url_for("index"))

    data_path = UPLOAD_FOLDER / f"{test_id}_data.json"
    if not data_path.exists():
        flash("Test not found. Please upload your PDFs again.", "error")
        return redirect(url_for("index"))

    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    duration_minutes = int(request.args.get("duration", 120))
    max_q = int(request.args.get("max_q", len(questions)))
    language = request.args.get("language", "both")

    # Slice to desired number of questions
    questions = questions[:max_q]

    # Expose only what the frontend needs (no correct answers in test mode)
    test_questions = []
    for q in questions:
        test_questions.append({
            "question_number": q["question_number"],
            "question_text_english": q.get("question_text_english", ""),
            "question_text_gujarati": q.get("question_text_gujarati", ""),
            "option_a": q.get("option_a", ""),
            "option_b": q.get("option_b", ""),
            "option_c": q.get("option_c", ""),
            "option_d": q.get("option_d", ""),
            "subject": q.get("subject", "General"),
            "is_cancelled": q.get("is_cancelled", False),
        })

    return render_template(
        "test.html",
        test_id=test_id,
        questions=test_questions,
        duration_minutes=duration_minutes,
        language=language,
        total_questions=len(test_questions),
    )


@app.route("/submit/<test_id>", methods=["POST"])
def submit_test(test_id: str):
    """Accept user answers and calculate results."""
    if not re.match(r"^[0-9a-f\-]{36}$", test_id):
        return jsonify({"error": "Invalid test ID."}), 400

    data_path = UPLOAD_FOLDER / f"{test_id}_data.json"
    if not data_path.exists():
        return jsonify({"error": "Test data not found."}), 404

    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    payload = request.get_json(silent=True) or {}
    user_answers: dict[str, str] = payload.get("answers", {})
    time_taken: int = payload.get("time_taken", 0)

    # Slice to same count as submitted (handles custom max_q)
    max_q = int(payload.get("total_questions", len(questions)))
    questions = questions[:max_q]

    results = calculate_results(questions, user_answers)
    results["time_taken"] = time_taken

    # Persist results
    res_path = UPLOAD_FOLDER / f"{test_id}_results.json"
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(
            {"results": results, "questions": questions, "user_answers": user_answers},
            f, ensure_ascii=False,
        )

    return jsonify({"redirect": url_for("results_page", test_id=test_id)})


@app.route("/results/<test_id>")
def results_page(test_id: str):
    """Render the results and analytics page."""
    if not re.match(r"^[0-9a-f\-]{36}$", test_id):
        flash("Invalid test ID.", "error")
        return redirect(url_for("index"))

    res_path = UPLOAD_FOLDER / f"{test_id}_results.json"
    if not res_path.exists():
        flash("Results not found.", "error")
        return redirect(url_for("index"))

    with open(res_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data["results"]
    questions = data["questions"]
    user_answers = data["user_answers"]

    # Build per-question review data
    review = []
    for q in questions:
        q_num = str(q["question_number"])
        user_ans = user_answers.get(q_num, "")
        correct_ans = q.get("correct_answer", "")
        is_cancelled = q.get("is_cancelled", False)

        if is_cancelled:
            status = "cancelled"
        elif not user_ans:
            status = "not_attempted"
        elif user_ans == correct_ans:
            status = "correct"
        else:
            status = "wrong"

        review.append({
            "question_number": q["question_number"],
            "question_text_english": q.get("question_text_english", ""),
            "option_a": q.get("option_a", ""),
            "option_b": q.get("option_b", ""),
            "option_c": q.get("option_c", ""),
            "option_d": q.get("option_d", ""),
            "correct_answer": correct_ans,
            "user_answer": user_ans,
            "subject": q.get("subject", "General"),
            "is_cancelled": is_cancelled,
            "status": status,
        })

    return render_template(
        "results.html",
        test_id=test_id,
        results=results,
        review=review,
    )


@app.route("/api/questions/<test_id>")
def api_questions(test_id: str):
    """Return full question list (for admin/review)."""
    if not re.match(r"^[0-9a-f\-]{36}$", test_id):
        return jsonify({"error": "Invalid test ID."}), 400

    data_path = UPLOAD_FOLDER / f"{test_id}_data.json"
    if not data_path.exists():
        return jsonify({"error": "Not found."}), 404

    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    return jsonify({"questions": questions, "total": len(questions)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
