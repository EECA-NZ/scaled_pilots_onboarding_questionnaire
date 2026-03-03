#!/usr/bin/env python3
"""Build codebook CSV and review HTML from questionnaire YAML files."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SECTIONS_DIR = ROOT / "questionnaire" / "sections"
CODEBOOK_CSV = ROOT / "questionnaire" / "codebook.csv"
REVIEW_HTML = ROOT / "questionnaire" / "review.html"

INSTRUCTION_PATTERNS = [
    "Please select one option.",
    "Please select all that apply.",
    "Please select as many as apply.",
    "Please enter the number of each type of room present.",
    "Please enter an approximate year/decade if you are unsure.",
    "Please enter a number for adults and children usually resident.",
]


def load_sections():
    sections = []
    for path in sorted(SECTIONS_DIR.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        sections.append((path, data))
    return sections


def option_summary(options):
    if not options:
        return ""
    return " | ".join(f"{opt['code']}: {opt['label']}" for opt in options)


def build_codebook(sections):
    with CODEBOOK_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question_number", "question_id", "question_text", "response_type", "options"])
        question_number = 1
        for _, section in sections:
            for q in section.get("questions", []):
                writer.writerow([
                    question_number,
                    q.get("id", ""),
                    q.get("question_text", ""),
                    q.get("response_type", ""),
                    option_summary(q.get("options", [])),
                ])
                question_number += 1


def h(text):
    return html.escape(str(text), quote=True)


def slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned or "section"


def infer_instruction(question_text: str, response_type: str) -> tuple[str, str]:
    text = (question_text or "").strip()
    for pattern in INSTRUCTION_PATTERNS:
        marker = " " + pattern
        if text.endswith(marker):
            return text[: -len(marker)].rstrip(), pattern

    if response_type == "single_choice":
        return text, "Please select one option."
    if response_type == "multi_choice":
        return text, "Please select all that apply."
    if response_type == "numeric":
        if "how many" in text.lower() or "enter a number" in text.lower() or "enter the number" in text.lower():
            return text, "Enter a number."
        return text, "Enter a numeric response."
    if response_type == "free_text":
        return text, "Write your response in the space provided."
    return text, ""


def format_skip_note(skip_logic: dict) -> str:
    if not isinstance(skip_logic, dict):
        return ""

    human = str(skip_logic.get("human", "")).strip()
    if human and not human.lower().startswith("none specified"):
        return human

    rules = skip_logic.get("rules", [])
    if not rules:
        return ""

    rendered = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        option_code = rule.get("if_option_code")
        goto_q = rule.get("goto_question_id")
        if option_code and goto_q:
            rendered.append(f"If {option_code}, go to {goto_q}.")
    return " ".join(rendered)


def render_choice_options(options: list[dict], qid: str, input_type: str) -> str:
    if not options:
        return ""

    lines = ["<ul class='options'>"]
    for idx, opt in enumerate(options, start=1):
        code = h(opt.get("code", ""))
        label = h(opt.get("label", ""))
        input_name = h(f"{qid}_choice")
        input_id = h(f"{qid}_{idx}")
        lines.append(
            "<li>"
            f"<label for='{input_id}' class='option-row'>"
            f"<input id='{input_id}' name='{input_name}' type='{h(input_type)}'>"
            f"<span class='option-label'>{label}</span>"
            f"<span class='option-code' data-code>[{code}]</span>"
            "</label>"
            "</li>"
        )
    lines.append("</ul>")
    return "".join(lines)


def render_grouped_multi_choice_options(options: list[dict], qid: str) -> str:
    if not options:
        return ""

    groups = [
        ("SHOWERS_", "Showers"),
        ("BATHS_", "Baths"),
        ("WASHING_DISHES_", "Washing dishes"),
        ("LAUNDRY_", "Laundry"),
    ]

    lines: list[str] = []
    global_idx = 0
    for prefix, heading in groups:
        group_opts = [opt for opt in options if str(opt.get("code", "")).startswith(prefix)]
        if not group_opts:
            continue
        # One selection per activity row: use a radio group keyed by activity prefix.
        group_name = h(f"{qid}_{prefix.rstrip('_')}_choice")
        lines.append(f"<div class='option-group'><p class='option-group-title'>{h(heading)}</p><ul class='options'>")
        for opt in group_opts:
            global_idx += 1
            code = h(opt.get("code", ""))
            label = h(opt.get("label", ""))
            input_id = h(f"{qid}_{global_idx}")
            lines.append(
                "<li>"
                f"<label for='{input_id}' class='option-row'>"
                f"<input id='{input_id}' name='{group_name}' type='radio'>"
                f"<span class='option-label'>{label}</span>"
                f"<span class='option-code' data-code>[{code}]</span>"
                "</label>"
                "</li>"
            )
        lines.append("</ul></div>")

    if lines:
        return "".join(lines)
    return render_choice_options(options, qid, "checkbox")


def render_single_select_matrix(
    *,
    qid: str,
    row_defs: list[tuple[str, str]],
    col_defs: list[tuple[str, str]],
    code_lookup: dict[tuple[str, str], str],
) -> str:
    lines = ["<table class='matrix-grid'><thead><tr><th></th>"]
    for _, col_label in col_defs:
        lines.append(f"<th>{h(col_label)}</th>")
    lines.append("</tr></thead><tbody>")

    input_idx = 0
    for row_key, row_label in row_defs:
        lines.append(f"<tr><td class='matrix-row-label'>{h(row_label)}</td>")
        for col_key, _ in col_defs:
            input_idx += 1
            cell_code = code_lookup.get((row_key, col_key), "")
            input_id = h(f"{qid}_mx_{input_idx}")
            input_name = h(f"{qid}_mx_{row_key}")
            lines.append(
                "<td class='matrix-cell'>"
                f"<input id='{input_id}' name='{input_name}' type='radio' aria-label='{h(row_label)} - {h(col_key)}'>"
                f"<span class='option-code' data-code>[{h(cell_code)}]</span>"
                "</td>"
            )
        lines.append("</tr>")
    lines.append("</tbody></table>")
    return "".join(lines)


def render_multi_select_matrix(
    *,
    qid: str,
    row_defs: list[tuple[str, str]],
    col_defs: list[tuple[str, str]],
    code_lookup: dict[tuple[str, str], str],
) -> str:
    lines = ["<table class='matrix-grid'><thead><tr><th></th>"]
    for _, col_label in col_defs:
        lines.append(f"<th>{h(col_label)}</th>")
    lines.append("</tr></thead><tbody>")

    input_idx = 0
    for row_key, row_label in row_defs:
        lines.append(f"<tr><td class='matrix-row-label'>{h(row_label)}</td>")
        for col_key, _ in col_defs:
            input_idx += 1
            cell_code = code_lookup.get((row_key, col_key), "")
            input_id = h(f"{qid}_mx_{input_idx}")
            input_name = h(f"{qid}_mx_{row_key}")
            lines.append(
                "<td class='matrix-cell'>"
                f"<input id='{input_id}' name='{input_name}' type='checkbox' aria-label='{h(row_label)} - {h(col_key)}'>"
                f"<span class='option-code' data-code>[{h(cell_code)}]</span>"
                "</td>"
            )
        lines.append("</tr>")
    lines.append("</tbody></table>")
    return "".join(lines)


def render_hot_water_activity_matrix(options: list[dict], qid: str) -> str:
    if not options:
        return ""

    row_defs = [
        ("SHOWERS", "Showers"),
        ("BATHS", "Baths"),
        ("WASHING_DISHES", "Washing dishes"),
        ("LAUNDRY", "Laundry"),
    ]
    col_defs = [
        ("MULTIPLE_TIMES_DAILY", "Multiple times daily"),
        ("DAILY", "Daily"),
        ("ONE_TO_TWO_PER_WEEK", "1-2 times per week"),
        ("THREE_TO_FIVE_PER_WEEK", "3-5 times per week"),
        ("WEEKLY", "Weekly"),
        ("NEVER", "Seldom or Never"),
    ]

    option_codes = {str(opt.get("code", "")) for opt in options}
    code_lookup: dict[tuple[str, str], str] = {}
    for row_key, _ in row_defs:
        for col_key, _ in col_defs:
            code = f"{row_key}_{col_key}"
            if code in option_codes:
                code_lookup[(row_key, col_key)] = code

    return render_single_select_matrix(
        qid=qid,
        row_defs=row_defs,
        col_defs=col_defs,
        code_lookup=code_lookup,
    )


def render_heating_frequency_matrix(options: list[dict], qid: str) -> str:
    row_defs = [
        ("MAIN_LIVING_AREA", "Main living area"),
        ("BEDROOM", "Bedroom"),
    ]
    col_defs = [
        ("EVERY_DAY", "Every day"),
        ("MOST_DAYS", "Most days"),
        ("SOME_DAYS", "Some days"),
        ("HARDLY_EVER", "Hardly ever"),
        ("NEVER", "Never"),
    ]

    option_codes = {str(opt.get("code", "")) for opt in options}
    code_lookup: dict[tuple[str, str], str] = {}
    for row_key, _ in row_defs:
        for col_key, _ in col_defs:
            code = f"{row_key}_{col_key}"
            if code in option_codes:
                code_lookup[(row_key, col_key)] = code

    return render_single_select_matrix(qid=qid, row_defs=row_defs, col_defs=col_defs, code_lookup=code_lookup)


def render_heating_appliances_matrix(options: list[dict], qid: str) -> str:
    # Transposed layout for readability: appliances as rows, home areas as columns.
    row_defs = [
        ("HEAT_PUMP", "Heat pump"),
        ("ENCLOSED_WOOD_BURNER", "Enclosed wood burner"),
        ("PELLET_BURNER", "Pellet burner"),
        ("OPEN_FIRE", "Open fire"),
        ("FIXED_ELECTRIC_HEATER", "Fixed electric heater"),
        ("FIXED_GAS_HEATER", "Fixed gas heater"),
        ("PORTABLE_ELECTRIC_HEATER", "Portable electric heater"),
        ("PORTABLE_GAS_HEATER", "Portable gas heater"),
        ("CENTRAL_HEATING", "Central heating"),
        ("DUCTED_HEAT_PUMP", "Ducted heat pump"),
        ("UNDERFLOOR_HEATING", "Underfloor heating"),
        ("OTHER", "Other"),
        ("UNSURE", "Unsure"),
    ]
    col_defs = [
        ("MAIN_LIVING_AREA", "Main living area"),
        ("BEDROOM", "Bedroom"),
        ("OTHER_ROOMS_AREAS", "Other rooms/areas"),
    ]

    option_codes = {str(opt.get("code", "")) for opt in options}
    code_lookup: dict[tuple[str, str], str] = {}
    for appliance_code, _ in row_defs:
        for area_code, _ in col_defs:
            code = f"{area_code}_{appliance_code}"
            if code in option_codes:
                code_lookup[(appliance_code, area_code)] = code

    return render_multi_select_matrix(
        qid=qid,
        row_defs=row_defs,
        col_defs=col_defs,
        code_lookup=code_lookup,
    )


def render_numeric_answer_area(options: list[dict]) -> str:
    if options:
        rows = ["<table class='numeric-grid'><thead><tr><th>Item</th><th>Response</th></tr></thead><tbody>"]
        for idx, opt in enumerate(options, start=1):
            label = h(opt.get("label", ""))
            code = h(opt.get("code", ""))
            rows.append(
                "<tr>"
                f"<td>{label} <span class='option-code' data-code>[{code}]</span></td>"
                f"<td><input type='number' inputmode='numeric' class='numeric-input' aria-label='Numeric response {idx}'></td>"
                "</tr>"
            )
        rows.append("</tbody></table>")
        return "".join(rows)
    return "<input type='number' inputmode='numeric' class='numeric-input single-numeric' aria-label='Numeric response'>"


def render_free_text_area() -> str:
    return "<textarea class='free-text-area' rows='4' aria-label='Free text response'></textarea>"


def build_review(sections):
    all_sections = []
    for idx, (_, section) in enumerate(sections, start=1):
        title = str(section.get("section_title", f"Section {idx}"))
        section_id = slug(f"{idx}-{title}")
        all_sections.append((section_id, section))

    parts = [
        "<!doctype html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>Scaled Demand Flexibility Pilots Questionnaire Review</title>",
        "<style>",
        ":root { color-scheme: light; }",
        "body { font-family: Georgia, 'Times New Roman', Times, serif; background: #fff; color: #111; margin: 0; }",
        ".page { max-width: 820px; margin: 0 auto; padding: 28px 34px 48px; }",
        "h1 { font-size: 1.55rem; margin: 0 0 0.35rem 0; font-weight: 700; letter-spacing: 0.01em; }",
        ".subtitle { margin: 0 0 1.1rem 0; color: #444; font-size: 0.95rem; }",
        ".code-toggle { font-family: Arial, Helvetica, sans-serif; font-size: 0.9rem; margin: 0.6rem 0 1.2rem; }",
        ".contents { border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; padding: 0.8rem 0 0.9rem; margin: 0 0 1.2rem 0; }",
        ".contents h2 { margin: 0 0 0.45rem 0; font: 700 1rem Arial, Helvetica, sans-serif; text-transform: uppercase; letter-spacing: 0.04em; }",
        ".contents ol { margin: 0; padding-left: 1.15rem; }",
        ".contents li { margin: 0.2rem 0; }",
        ".contents a { color: #111; text-decoration: none; border-bottom: 1px dotted #666; }",
        ".section { margin: 1.65rem 0 0; }",
        ".section h2 { font: 700 1.25rem Arial, Helvetica, sans-serif; margin: 0 0 0.5rem; }",
        ".section-intro { margin: 0 0 0.8rem; color: #444; font: italic 0.95rem Georgia, 'Times New Roman', Times, serif; }",
        ".question { margin: 0.95rem 0 1.25rem; break-inside: avoid; page-break-inside: avoid; }",
        ".q-label { font: 700 0.95rem Arial, Helvetica, sans-serif; margin: 0 0 0.3rem; display: flex; justify-content: space-between; align-items: baseline; gap: 0.75rem; }",
        ".q-code { font-style: italic; font-weight: 400; text-align: right; white-space: nowrap; }",
        ".q-text { margin: 0 0 0.35rem; font-size: 1rem; }",
        ".instruction { margin: 0 0 0.45rem; font-size: 0.9rem; font-style: italic; color: #444; }",
        ".options { margin: 0.25rem 0 0.25rem 0; padding: 0; list-style: none; }",
        ".options li { margin: 0.22rem 0; }",
        ".option-row { display: flex; align-items: baseline; gap: 0.5rem; cursor: pointer; }",
        ".option-row input[type='radio'], .option-row input[type='checkbox'] { transform: translateY(1px); }",
        ".option-label { flex: 1; }",
        ".option-code { font: 0.75rem 'Courier New', Courier, monospace; color: #888; margin-left: 0.45rem; display: none; }",
        "body.show-codes .option-code { display: inline; }",
        ".option-group { margin: 0.25rem 0 0.45rem; }",
        ".option-group-title { margin: 0.2rem 0 0.25rem; font: 700 0.9rem Arial, Helvetica, sans-serif; }",
        ".matrix-grid { width: 100%; border-collapse: collapse; margin-top: 0.3rem; table-layout: fixed; }",
        ".matrix-grid th, .matrix-grid td { border: 1px solid #cfcfcf; padding: 0.32rem 0.25rem; text-align: center; vertical-align: middle; }",
        ".matrix-grid th:first-child { width: 30%; }",
        ".matrix-row-label { text-align: left !important; font: 600 0.88rem Arial, Helvetica, sans-serif; }",
        ".matrix-cell input { transform: translateY(1px); }",
        ".numeric-grid { width: 100%; border-collapse: collapse; margin-top: 0.3rem; }",
        ".numeric-grid th { text-align: left; font: 700 0.86rem Arial, Helvetica, sans-serif; border-bottom: 1px solid #888; padding: 0.22rem 0.25rem; }",
        ".numeric-grid td { padding: 0.32rem 0.25rem 0.28rem; border-bottom: 1px solid #ddd; vertical-align: middle; }",
        ".numeric-input { width: 120px; height: 1.4rem; border: 1px solid #666; padding: 0.05rem 0.25rem; font: inherit; }",
        ".single-numeric { margin-top: 0.3rem; }",
        ".free-text-area { width: 100%; min-height: 4.1rem; border: 1px solid #666; margin-top: 0.3rem; padding: 0.3rem; font: inherit; resize: vertical; box-sizing: border-box; }",
        ".skip-note { margin-top: 0.4rem; font-size: 0.84rem; color: #555; font-style: italic; }",
        "@media print {",
        "  .page { max-width: none; padding: 0.35in 0.45in; }",
        "  .contents a { border-bottom: none; text-decoration: none; }",
        "  .question { margin-bottom: 0.9rem; }",
        "  .code-toggle { display: none; }",
        "  .free-text-area { resize: none; }",
        "}",
        "</style>",
        "</head>",
        "<body>",
        "<main class='page'>",
        "<h1>Scaled Demand Flexibility Pilots</h1>",
        "<p class='subtitle'>Householder questionnaire review</p>",
        "<label class='code-toggle'><input id='show-codes-toggle' type='checkbox'> Show analysis codes</label>",
        "<nav class='contents' aria-label='Contents'><h2>Contents</h2><ol>",
    ]

    for section_id, section in all_sections:
        title = h(section.get("section_title", "Untitled Section"))
        parts.append(f"<li><a href='#{h(section_id)}'>{title}</a></li>")

    parts.append("</ol></nav>")

    display_question_number = 1

    for section_id, section in all_sections:
        title = str(section.get("section_title", "Untitled Section"))
        section_intro = str(section.get("instruction_text", "")).strip()

        parts.append(f"<section class='section' id='{h(section_id)}'>")
        parts.append(f"<h2>{h(title)}</h2>")
        if section_intro:
            parts.append(f"<p class='section-intro'>{h(section_intro)}</p>")

        section_questions = section.get("questions", [])
        skip_ids: set[str] = set()
        for q in section_questions:
            qid = str(q.get("id", ""))
            if qid in skip_ids:
                continue

            q_num = display_question_number
            q_text = str(q.get("question_text", ""))
            response_type = str(q.get("response_type", ""))
            stem, instruction = infer_instruction(q_text, response_type)
            skip_note = format_skip_note(q.get("skip_logic", {}))
            options = q.get("options", [])

            if qid == "HEAT_30":
                parts.append("<article class='question'>")
                parts.append(f"<p class='q-label'>Q{q_num}. <span class='q-code'>[{h(qid)}]</span></p>")
                parts.append("<p class='q-text'>How often do you usually heat the following areas in winter?</p>")
                parts.append("<p class='instruction'>Select one option per row.</p>")
                parts.append(render_heating_frequency_matrix(options, qid))
                if skip_note:
                    parts.append(f"<p class='skip-note'>{h(skip_note)}</p>")
                parts.append("</article>")
                display_question_number += 1
                continue

            if qid == "HEAT_31":
                parts.append("<article class='question'>")
                parts.append(f"<p class='q-label'>Q{q_num}. <span class='q-code'>[{h(qid)}]</span></p>")
                parts.append("<p class='q-text'>What appliance(s) do you use to heat the following areas of your home in winter?</p>")
                parts.append("<p class='instruction'>Select all that apply in each area.</p>")
                parts.append(render_heating_appliances_matrix(options, qid))
                if skip_note:
                    parts.append(f"<p class='skip-note'>{h(skip_note)}</p>")
                parts.append("</article>")
                display_question_number += 1
                continue

            parts.append("<article class='question'>")
            parts.append(f"<p class='q-label'>Q{q_num}. <span class='q-code'>[{h(qid)}]</span></p>")
            parts.append(f"<p class='q-text'>{h(stem)}</p>")
            if instruction:
                parts.append(f"<p class='instruction'>{h(instruction)}</p>")

            if response_type == "single_choice":
                parts.append(render_choice_options(options, qid, "radio"))
            elif response_type == "multi_choice":
                if qid == "HW_22":
                    parts.append(render_hot_water_activity_matrix(options, qid))
                else:
                    parts.append(render_choice_options(options, qid, "checkbox"))
            elif response_type == "numeric":
                parts.append(render_numeric_answer_area(options))
            elif response_type == "free_text":
                parts.append(render_free_text_area())

            if skip_note:
                parts.append(f"<p class='skip-note'>{h(skip_note)}</p>")

            parts.append("</article>")
            display_question_number += 1

        parts.append("</section>")

    parts.extend(
        [
            "</main>",
            "<script>",
            "(function(){",
            "  const toggle = document.getElementById('show-codes-toggle');",
            "  if (!toggle) return;",
            "  toggle.addEventListener('change', function(){",
            "    document.body.classList.toggle('show-codes', toggle.checked);",
            "  });",
            "})();",
            "</script>",
            "</body>",
            "</html>",
        ]
    )

    REVIEW_HTML.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    sections = load_sections()
    build_codebook(sections)
    build_review(sections)
    question_count = sum(len(section.get("questions", [])) for _, section in sections)
    print(f"Built {CODEBOOK_CSV} and {REVIEW_HTML} for {question_count} questions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
