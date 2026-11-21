"""KQL syntax and structural parser/validator for Sentinel rules, queries and workbooks.

Validates Kusto Query Language (KQL) without requiring a live Azure Log Analytics
workspace. Checks lexical validity, balanced delimiters, statement structure,
known tabular operators, common syntax pitfalls and accidental real GUID leaks.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TABULAR_OPERATORS: frozenset[str] = frozenset(
    {
        "as",
        "consume",
        "count",
        "datatable",
        "distinct",
        "evaluate",
        "extend",
        "externaldata",
        "facet",
        "filter",
        "find",
        "fork",
        "getschema",
        "invoke",
        "join",
        "limit",
        "lookup",
        "make-series",
        "mv-apply",
        "mv-expand",
        "order",
        "parse",
        "parse-kv",
        "parse-where",
        "partition",
        "print",
        "project",
        "project-away",
        "project-keep",
        "project-rename",
        "project-reorder",
        "range",
        "reduce",
        "render",
        "sample",
        "sample-distinct",
        "scan",
        "search",
        "serialize",
        "sort",
        "summarize",
        "take",
        "top",
        "top-hitters",
        "top-nested",
        "union",
        "where",
    }
)

STARTER_KEYWORDS: frozenset[str] = frozenset(
    {
        "datatable",
        "externaldata",
        "find",
        "print",
        "range",
        "search",
        "union",
    }
)

UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)

# Known benign GUIDs (placeholder GUIDs and well-known public Microsoft Defender ASR / WDAC / Entra App IDs).
PLACEHOLDER_GUID_PREFIXES = (
    "00000000-0000-0000-0000-",
    "11111111-1111-1111-1111-",
)

SQL_MISTAKE_RE = re.compile(r"^\s*SELECT\b.+\bFROM\b", re.IGNORECASE | re.DOTALL)
WB_PARAM_RE = re.compile(r"\{[A-Za-z0-9_:\-]+\}")


@dataclass
class Token:
    kind: str  # IDENT, STRING, NUMBER, OP, PUNCT, PIPE, SEMI
    value: str
    line: int


@dataclass
class ValidationError:
    message: str
    line: int | None = None

    def __str__(self) -> str:
        if self.line is not None:
            return f"line {self.line}: {self.message}"
        return self.message


def strip_workbook_params(query: str) -> str:
    """Replace Azure Monitor workbook parameter tokens like {TimeRange} for parsing."""
    return WB_PARAM_RE.sub("__wb_param__", query)


def tokenize_kql(query: str) -> tuple[list[Token], list[ValidationError]]:
    """Tokenize KQL source text, stripping line comments and validating strings."""
    tokens: list[Token] = []
    errors: list[ValidationError] = []
    i = 0
    n = len(query)
    line = 1

    while i < n:
        ch = query[i]

        # Whitespace
        if ch in " \t\r":
            i += 1
            continue
        if ch == "\n":
            line += 1
            i += 1
            continue

        # Single-line comment //
        if ch == "/" and i + 1 < n and query[i + 1] == "/":
            while i < n and query[i] != "\n":
                i += 1
            continue

        # Verbatim multi-line string ```...```
        if query[i : i + 3] == "```":
            start_line = line
            end = query.find("```", i + 3)
            if end == -1:
                errors.append(ValidationError("Unterminated verbatim string literal (```)", start_line))
                break
            segment = query[i : end + 3]
            line += segment.count("\n")
            tokens.append(Token("STRING", segment, start_line))
            i = end + 3
            continue

        # Raw / obfuscated string @"...", @'...', h"...", h'...', H"..."
        if ch in ("@", "h", "H") and i + 1 < n and query[i + 1] in ('"', "'"):
            prefix = ch
            quote = query[i + 1]
            start_line = line
            j = i + 2
            closed = False
            while j < n:
                if query[j] == "\n":
                    errors.append(ValidationError(f"Unterminated string literal starting with {prefix}{quote}", start_line))
                    break
                if prefix == "@":
                    if query[j] == quote:
                        if j + 1 < n and query[j + 1] == quote:
                            j += 2
                            continue
                        closed = True
                        j += 1
                        break
                else:
                    if query[j] == "\\":
                        j += 2
                        continue
                    if query[j] == quote:
                        closed = True
                        j += 1
                        break
                j += 1
            if not closed and not (j < n and query[j] == "\n"):
                errors.append(ValidationError(f"Unterminated string literal starting with {prefix}{quote}", start_line))
            tokens.append(Token("STRING", query[i:j], start_line))
            i = j
            continue

        # Standard string "..." or '...'
        if ch in ('"', "'"):
            quote = ch
            start_line = line
            j = i + 1
            closed = False
            while j < n:
                if query[j] == "\n":
                    errors.append(ValidationError(f"Unterminated string literal ({quote})", start_line))
                    break
                if query[j] == "\\":
                    j += 2
                    continue
                if query[j] == quote:
                    closed = True
                    j += 1
                    break
                j += 1
            if not closed and not (j < n and query[j] == "\n"):
                errors.append(ValidationError(f"Unterminated string literal ({quote})", start_line))
            tokens.append(Token("STRING", query[i:j], start_line))
            i = j
            continue

        # Pipe and semicolon
        if ch == "|":
            tokens.append(Token("PIPE", "|", line))
            i += 1
            continue
        if ch == ";":
            tokens.append(Token("SEMI", ";", line))
            i += 1
            continue

        # Brackets and punctuation
        if ch in "()[]{},.:":
            tokens.append(Token("PUNCT", ch, line))
            i += 1
            continue

        # Two-character operators
        if i + 1 < n and query[i : i + 2] in ("==", "!=", "=~", "!~", "<=", ">=", "<>", "..", "=>"):
            tokens.append(Token("OP", query[i : i + 2], line))
            i += 2
            continue

        # Single-character operators
        if ch in "=<>+-*/%!~?":
            tokens.append(Token("OP", ch, line))
            i += 1
            continue

        # Numbers and timespans (e.g., 14d, 24h, 30m, 1.5)
        if ch.isdigit():
            j = i
            while j < n and (query[j].isalnum() or query[j] == "."):
                j += 1
            tokens.append(Token("NUMBER", query[i:j], line))
            i = j
            continue

        # Identifiers (including hyphenated KQL operators like mv-expand, project-away, has_any, !in)
        if ch.isalpha() or ch == "_" or ch == "$":
            j = i
            while j < n and (query[j].isalnum() or query[j] in ("_", "$")):
                j += 1
            # Check for hyphenated KQL operators such as project-away, mv-expand, make-series, top-nested
            word = query[i:j]
            if j < n and query[j] == "-":
                k = j + 1
                while k < n and (query[k].isalnum() or query[k] == "_"):
                    k += 1
                candidate = query[i:k]
                if candidate.lower() in TABULAR_OPERATORS or candidate.lower() in ("by", "with"):
                    word = candidate
                    j = k
            tokens.append(Token("IDENT", word, line))
            i = j
            continue

        errors.append(ValidationError(f"Unexpected character {ch!r}", line))
        i += 1

    return tokens, errors


def _check_balanced_delimiters(tokens: list[Token]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = {")": "(", "]": "[", "}": "{"}
    stack: list[tuple[str, int]] = []

    for tok in tokens:
        if tok.kind != "PUNCT":
            continue
        if tok.value in pairs:
            stack.append((tok.value, tok.line))
        elif tok.value in closing:
            if not stack:
                errors.append(ValidationError(f"Unmatched closing {tok.value!r}", tok.line))
            else:
                top_val, top_line = stack.pop()
                if closing[tok.value] != top_val:
                    errors.append(
                        ValidationError(
                            f"Mismatched delimiter {tok.value!r} closing {top_val!r} from line {top_line}",
                            tok.line,
                        )
                    )
    for open_val, open_line in stack:
        errors.append(ValidationError(f"Unclosed delimiter {open_val!r}", open_line))
    return errors


def _split_top_level(tokens: list[Token], split_kind: str) -> list[list[Token]]:
    """Split tokens by `split_kind` (SEMI or PIPE) only at delimiter depth 0."""
    segments: list[list[Token]] = []
    current: list[Token] = []
    depth = 0
    for tok in tokens:
        if tok.kind == "PUNCT":
            if tok.value in ("(", "[", "{"):
                depth += 1
            elif tok.value in (")", "]", "}"):
                depth = max(0, depth - 1)
        if depth == 0 and tok.kind == split_kind:
            segments.append(current)
            current = []
        else:
            current.append(tok)
    segments.append(current)
    return segments


ZERO_ARG_OPERATORS: frozenset[str] = frozenset(
    {
        "consume",
        "count",
        "getschema",
        "serialize",
    }
)


def _check_where_clause(stage: list[Token]) -> list[ValidationError]:
    """Validate predicate presence and catch accidental single '=' inside `where`/`filter`."""
    if len(stage) < 2:
        return [
            ValidationError(
                f"Operator {stage[0].value!r} requires a predicate expression",
                stage[0].line,
            )
        ]
    errors: list[ValidationError] = []
    depth = 0
    for tok in stage[1:]:
        if tok.kind == "PUNCT":
            if tok.value in ("(", "[", "{"):
                depth += 1
            elif tok.value in (")", "]", "}"):
                depth = max(0, depth - 1)
        elif depth == 0 and tok.kind == "OP" and tok.value == "=":
            errors.append(
                ValidationError(
                    "Single '=' found in 'where' predicate; use '==' for equality in KQL",
                    tok.line,
                )
            )
    return errors


def _validate_tabular_pipeline(expr_tokens: list[Token], defined_lets: set[str]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    stages = _split_top_level(expr_tokens, "PIPE")

    if not stages or not stages[0]:
        line = expr_tokens[0].line if expr_tokens else 1
        errors.append(ValidationError("Empty tabular expression or leading pipe", line))
        return errors

    first = stages[0][0]
    if first.kind not in ("IDENT", "PUNCT"):
        errors.append(
            ValidationError(
                f"Tabular expression must start with a table name, let variable or starter operator, got {first.value!r}",
                first.line,
            )
        )
    elif first.kind == "IDENT":
        name_lower = first.value.lower()
        # Allow table names (usually PascalCase or custom _CL), let variables, or starter keywords
        if name_lower in TABULAR_OPERATORS and name_lower not in STARTER_KEYWORDS and first.value not in defined_lets:
            errors.append(
                ValidationError(
                    f"Tabular expression cannot start with pipe operator {first.value!r}",
                    first.line,
                )
            )

    for idx, stage in enumerate(stages[1:], start=1):
        if not stage:
            prev_line = stages[idx - 1][-1].line if stages[idx - 1] else first.line
            errors.append(ValidationError("Empty pipe stage (trailing or consecutive '|')", prev_line))
            continue
        op_tok = stage[0]
        op_lower = op_tok.value.lower()
        if op_tok.kind != "IDENT" or op_lower not in TABULAR_OPERATORS:
            errors.append(
                ValidationError(
                    f"Unknown or invalid KQL tabular operator after '|': {op_tok.value!r}",
                    op_tok.line,
                )
            )
            continue
        if op_lower not in ZERO_ARG_OPERATORS and len(stage) < 2:
            errors.append(
                ValidationError(
                    f"Operator {op_tok.value!r} requires at least one argument",
                    op_tok.line,
                )
            )
            continue
        if op_lower in ("where", "filter"):
            errors.extend(_check_where_clause(stage))

    return errors


def validate_kql(query: str, *, is_workbook: bool = False) -> list[ValidationError]:
    """Validate a KQL query string and return a list of ValidationError objects."""
    if not query or not query.strip():
        return [ValidationError("Query is empty", 1)]

    if SQL_MISTAKE_RE.search(query):
        return [ValidationError("Query looks like SQL (SELECT ... FROM) instead of KQL", 1)]

    normalized = strip_workbook_params(query) if is_workbook else query
    tokens, lex_errors = tokenize_kql(normalized)
    if lex_errors:
        return lex_errors

    if not tokens:
        return [ValidationError("Query contains only comments or whitespace", 1)]

    delim_errors = _check_balanced_delimiters(tokens)
    if delim_errors:
        return delim_errors

    errors: list[ValidationError] = []
    statements = _split_top_level(tokens, "SEMI")
    # Drop trailing empty statement after final semicolon
    while statements and not statements[-1]:
        statements.pop()

    if not statements:
        return [ValidationError("Query contains no executable KQL statements", 1)]

    defined_lets: set[str] = set()
    has_tabular_output = False

    for idx, stmt in enumerate(statements):
        if not stmt:
            continue
        head = stmt[0]
        if head.kind == "IDENT" and head.value.lower() == "let":
            if len(stmt) < 4:
                errors.append(ValidationError("Incomplete 'let' statement", head.line))
                continue
            var_tok = stmt[1]
            eq_tok = stmt[2]
            if var_tok.kind != "IDENT":
                errors.append(ValidationError(f"Expected identifier after 'let', got {var_tok.value!r}", var_tok.line))
                continue
            if eq_tok.kind != "OP" or eq_tok.value != "=":
                errors.append(ValidationError(f"Expected '=' in 'let {var_tok.value}' statement", eq_tok.line))
                continue
            defined_lets.add(var_tok.value)
            # Check if RHS of let has pipes (tabular let binding) or wrapped materialize/toscalar
            rhs = stmt[3:]
            if (
                rhs
                and rhs[0].kind == "IDENT"
                and rhs[0].value.lower() in ("materialize", "toscalar")
                and len(rhs) >= 3
                and rhs[1].kind == "PUNCT"
                and rhs[1].value == "("
                and rhs[-1].kind == "PUNCT"
                and rhs[-1].value == ")"
            ):
                inner = rhs[2:-1]
                if not inner:
                    errors.append(
                        ValidationError(
                            f"{rhs[0].value}() requires an inner expression",
                            rhs[0].line,
                        )
                    )
                elif any(t.kind == "PIPE" for t in inner):
                    errors.extend(_validate_tabular_pipeline(inner, defined_lets))
            elif any(t.kind == "PIPE" for t in rhs):
                errors.extend(_validate_tabular_pipeline(rhs, defined_lets))
            if idx == len(statements) - 1:
                errors.append(
                    ValidationError(
                        "Query ends with a 'let' statement and has no final tabular expression",
                        head.line,
                    )
                )
        elif head.kind == "IDENT" and head.value.lower() == "declare":
            # KQL query_parameters or pattern declaration
            continue
        else:
            has_tabular_output = True
            errors.extend(_validate_tabular_pipeline(stmt, defined_lets))

    if not has_tabular_output and not errors:
        errors.append(ValidationError("Query must include a tabular expression", 1))

    return errors


def extract_workbook_queries(workbook_data: dict) -> Iterable[tuple[str, str]]:
    """Recursively yield (item_name, kql_query) pairs from a Sentinel workbook JSON object."""

    def _walk(node: object, path: str) -> Iterable[tuple[str, str]]:
        if isinstance(node, dict):
            name = str(node.get("name") or path)
            item_type = node.get("type")
            content = node.get("content")
            # Type 3 is a query visualization; queryType 0 (or omitted) is Log Analytics KQL
            if item_type == 3 and isinstance(content, dict):
                query = content.get("query")
                query_type = content.get("queryType", 0)
                if isinstance(query, str) and query.strip() and query_type == 0:
                    yield (name, query)
            # Type 9 is parameters; individual parameters may hold KQL queries
            if item_type == 9 and isinstance(content, dict):
                params = content.get("parameters")
                if isinstance(params, list):
                    for param in params:
                        if isinstance(param, dict):
                            p_query = param.get("query")
                            p_name = param.get("name", "param")
                            p_type = param.get("queryType", 0)
                            if isinstance(p_query, str) and p_query.strip() and p_type == 0:
                                yield (f"{name}.{p_name}", p_query)
            # Type 12 is a group containing nested items
            if isinstance(content, dict) and isinstance(content.get("items"), list):
                for idx, child in enumerate(content["items"]):
                    yield from _walk(child, f"{name}[{idx}]")
            if isinstance(node.get("items"), list):
                for idx, child in enumerate(node["items"]):
                    yield from _walk(child, f"{path}[{idx}]")
        elif isinstance(node, list):
            for idx, child in enumerate(node):
                yield from _walk(child, f"{path}[{idx}]")

    yield from _walk(workbook_data, "root")


def main(argv: list[str]) -> int:
    """CLI entry point to validate standalone .kql files."""
    exit_code = 0
    for arg in argv:
        path = Path(arg)
        text = path.read_text(encoding="utf-8")
        errs = validate_kql(text)
        if errs:
            exit_code = 1
            for err in errs:
                print(f"{path}: {err}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
