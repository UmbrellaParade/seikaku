from flask import Flask, render_template, request, session
from types_data import pick_questions, TYPES, TYPE_MAPPING, SPECIAL_TYPES
from life_data import LIFE_DATA
import random

app = Flask(__name__)
app.secret_key = "umbrella-parade-seikaku-secret"


def calculate_result(answers, questions):
    """16問の回答から種族を決定する"""
    axis_scores = {"A": 0, "B": 0, "C": 0, "D": 0}
    axis_counts = {"A": 0, "B": 0, "C": 0, "D": 0}

    q_map = {q["id"]: q for q in questions}

    for qid, val in answers.items():
        if qid in q_map:
            axis = q_map[qid]["axis"]
            axis_scores[axis] += int(val)
            axis_counts[axis] += 1

    a = 1 if axis_scores["A"] / max(axis_counts["A"], 1) >= 1.5 else 0
    b = 1 if axis_scores["B"] / max(axis_counts["B"], 1) >= 1.5 else 0
    c = 1 if axis_scores["C"] / max(axis_counts["C"], 1) >= 1.5 else 0
    d = 1 if axis_scores["D"] / max(axis_counts["D"], 1) >= 1.5 else 0

    total = sum(axis_scores.values())
    total_max = sum(axis_counts.values()) * 3
    ratio = total / max(total_max, 1)

    if ratio <= 0.15:
        return random.choice(["神", "賢者"])
    if ratio >= 0.85:
        return random.choice(["悪魔", "龍", "メデューサ"])

    result = TYPE_MAPPING.get((a, b, c, d))
    if result:
        return result

    return random.choice(SPECIAL_TYPES)


@app.route("/", methods=["GET"])
def index():
    questions = pick_questions()
    session["questions"] = questions
    return render_template("index.html", questions=questions)


@app.route("/result", methods=["POST"])
def result():
    questions = session.get("questions", pick_questions())

    name = request.form.get("name", "あなた").strip() or "あなた"
    birth_year = request.form.get("birth_year", "")
    birth_month = request.form.get("birth_month", "")
    birth_day = request.form.get("birth_day", "")

    birthday = ""
    if birth_year and birth_month and birth_day:
        birthday = f"{birth_year}年{birth_month}月{birth_day}日"
    elif birth_month:
        birthday = f"{birth_month}月生まれ"

    answers = {}
    for q in questions:
        val = request.form.get(q["id"])
        if val is not None:
            answers[q["id"]] = val

    result_type = calculate_result(answers, questions)
    type_data = TYPES.get(result_type, TYPES["ハーフ"])

    life_info = LIFE_DATA.get(result_type, {})

    return render_template(
        "result.html",
        name=name,
        birthday=birthday,
        result_type=result_type,
        type_data=type_data,
        life_info=life_info,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8789)
