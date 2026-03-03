#!/usr/bin/env python3
"""Validate questionnaire YAML content against local schema rules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SECTIONS_DIR = ROOT / "questionnaire" / "sections"
SCHEMA_PATH = ROOT / "questionnaire" / "schema" / "question.schema.yaml"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_question(question: dict, required_fields: list[str], response_types: set[str], path: Path, idx: int) -> list[str]:
    errs: list[str] = []
    qref = f"{path.name} question[{idx}]"

    if not isinstance(question, dict):
        return [f"{qref}: must be an object"]

    for field in required_fields:
        if field not in question:
            errs.append(f"{qref}: missing required field '{field}'")

    response_type = question.get("response_type")
    if response_type not in response_types:
        errs.append(
            f"{qref}: response_type '{response_type}' not in allowed set {sorted(response_types)}"
        )

    for bool_field in ("allow_other", "required"):
        if bool_field in question and not isinstance(question[bool_field], bool):
            errs.append(f"{qref}: field '{bool_field}' must be boolean")

    options = question.get("options")
    if not isinstance(options, list):
        errs.append(f"{qref}: field 'options' must be a list")
    else:
        seen_codes: set[str] = set()
        for opt_idx, option in enumerate(options):
            if not isinstance(option, dict):
                errs.append(f"{qref}: option[{opt_idx}] must be an object")
                continue
            for key in ("code", "label"):
                if key not in option:
                    errs.append(f"{qref}: option[{opt_idx}] missing '{key}'")
            code = option.get("code")
            label = option.get("label")
            if isinstance(code, bool):
                errs.append(f"{qref}: option[{opt_idx}] code must be a string/int, not boolean")
            if not isinstance(label, str):
                errs.append(f"{qref}: option[{opt_idx}] label must be a string")
            if code is not None:
                code_s = str(code)
                if code_s in seen_codes:
                    errs.append(f"{qref}: duplicate option code '{code_s}'")
                seen_codes.add(code_s)

    skip_logic = question.get("skip_logic")
    if not isinstance(skip_logic, dict):
        errs.append(f"{qref}: field 'skip_logic' must be an object")
    else:
        for key in ("human", "rules"):
            if key not in skip_logic:
                errs.append(f"{qref}: skip_logic missing '{key}'")
        if "rules" in skip_logic and not isinstance(skip_logic["rules"], list):
            errs.append(f"{qref}: skip_logic.rules must be a list")
        elif isinstance(skip_logic.get("rules"), list):
            for ridx, rule in enumerate(skip_logic["rules"]):
                if not isinstance(rule, dict):
                    errs.append(f"{qref}: skip_logic.rules[{ridx}] must be an object")
                    continue
                for key in ("if_option_code", "goto_question_id"):
                    if key not in rule:
                        errs.append(f"{qref}: skip_logic.rules[{ridx}] missing '{key}'")

    page = question.get("provenance_page")
    if not isinstance(page, int) or page < 1:
        errs.append(f"{qref}: provenance_page must be a positive integer")

    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate questionnaire YAML files.")
    parser.add_argument(
        "--sections-dir",
        default=str(SECTIONS_DIR),
        help="Directory containing section YAML files",
    )
    parser.add_argument(
        "--schema",
        default=str(SCHEMA_PATH),
        help="Schema YAML path",
    )
    args = parser.parse_args()

    sections_dir = Path(args.sections_dir)
    schema_path = Path(args.schema)

    schema = load_yaml(schema_path)
    required_fields = schema.get("required", [])
    response_types = set(schema.get("properties", {}).get("response_type", {}).get("enum", []))

    all_errors: list[str] = []
    all_warnings: list[str] = []
    seen_question_ids: set[str] = set()

    files = sorted(sections_dir.glob("*.yaml"))
    if not files:
        print(f"No section files found in {sections_dir}")
        return 1

    for path in files:
        payload = load_yaml(path)
        questions = payload.get("questions") if isinstance(payload, dict) else None
        if not isinstance(questions, list):
            all_errors.append(f"{path.name}: missing or invalid 'questions' list")
            continue

        for idx, question in enumerate(questions):
            all_errors.extend(validate_question(question, required_fields, response_types, path, idx))
            qid = question.get("id") if isinstance(question, dict) else None
            if qid:
                if qid in seen_question_ids:
                    all_errors.append(f"{path.name}: duplicate question id '{qid}' across sections")
                seen_question_ids.add(qid)
    if all_errors:
        print("Validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    if all_warnings:
        print("Validation warnings:")
        for warning in all_warnings:
            print(f"- {warning}")

    print(f"Validation passed: {len(seen_question_ids)} questions checked across {len(files)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
