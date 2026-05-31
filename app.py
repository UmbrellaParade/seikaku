from flask import Flask, render_template, request, session
from types_data import QUESTIONS, TYPES, TYPE_MAPPING, SPECIAL_TYPES
import random

app = Flask(__name__)
app.secret_key = "umbrella-parade-seikaku-secret"

def calculate_result(answers):
    """16問の回答から種族を決定する"""
    axis_scores = {"A": 0, "B": 0, "C": 0, "D": 0}
    axis_counts = {"A": 0, "B": 0, "C": 0, "D": 0}

    for q in QUESTIONS:
        qid = q["id"]
        if qid in answers:
            val = int(answers[qid])
            axis = q["axis"] if "axis" in q else q["options"][0]["axis"]
            # 各軸のスコア(0-3)を合計
            axis_scores[axis] += val
            axis_counts[axis] += 1

    # 各軸の平均スコアで0or1に二値化（1.5以上なら1）
    a = 1 if axis_scores["A"] / max(axis_counts["A"], 1) >= 1.5 else 0
    b = 1 if axis_scores["B"] / max(axis_counts["B"], 1) >= 1.5 else 0
    c = 1 if axis_scores["C"] / max(axis_counts["C"], 1) >= 1.5 else 0
    d = 1 if axis_scores["D"] / max(axis_counts["D"], 1) >= 1.5 else 0

    # 極端なスコアパターンで特殊種族を出現させる
    total = sum(axis_scores.values())
    total_max = sum(axis_counts.values()) * 3

    ratio = total / max(total_max, 1)

    # 全部0寄り → 神 or 悪魔
    if ratio <= 0.15:
        return random.choice(["神", "賢者"])
    # 全部3寄り → カリスマ系
    if ratio >= 0.85:
        return random.choice(["悪魔", "龍", "メデューサ"])

    # 通常マッピング
    result = TYPE_MAPPING.get((a, b, c, d))
    if result:
        return result

    return random.choice(SPECIAL_TYPES)


def get_axis_for_question(q):
    return q["options"][0]["axis"]


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", questions=QUESTIONS)


@app.route("/result", methods=["POST"])
def result():
    name = request.form.get("name", "あなた").strip() or "あなた"
    birth_year = request.form.get("birth_year", "")
    birth_month = request.form.get("birth_month", "")
    birth_day = request.form.get("birth_day", "")

    # 誕生日をまとめる
    birthday = ""
    if birth_year and birth_month and birth_day:
        birthday = f"{birth_year}年{birth_month}月{birth_day}日"
    elif birth_month:
        birthday = f"{birth_month}月生まれ"

    # 各質問の回答を収集
    answers = {}
    for q in QUESTIONS:
        qid = q["id"]
        val = request.form.get(qid)
        if val is not None:
            answers[qid] = val
        # axisをquestion本体に付与
        q["axis"] = get_axis_for_question(q)

    result_type = calculate_result(answers)
    type_data = TYPES.get(result_type, TYPES["ハーフ"])

    return render_template(
        "result.html",
        name=name,
        birthday=birthday,
        result_type=result_type,
        type_data=type_data,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8789)
