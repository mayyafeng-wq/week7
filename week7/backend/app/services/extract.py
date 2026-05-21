import re
from dataclasses import dataclass

PRIORITY_KEYWORDS = {
    "urgent": "high",
    "asap": "high",
    "critical": "high",
    "important": "medium",
    "soon": "medium",
}

ACTION_PREFIXES = ("todo:", "action:", "task:", "fix:")
MODAL_VERBS = ("need to", "should", "must", "have to")
CHECKBOX_PATTERN = re.compile(r"^\s*[-*]?\s*\[[ xX]?\]\s*(.+)$")
NUMBERED_PATTERN = re.compile(r"^\s*\d+[.)]\s+(.+)$")
ASSIGNEE_PATTERN = re.compile(r"@([\w.-]+)")
DUE_DATE_PATTERN = re.compile(
    r"\b(?:due|by)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}(?:/\d{2,4})?|monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|next week)\b",
    re.IGNORECASE,
)
PRIORITY_PATTERN = re.compile(r"\b(p\d|urgent|asap|critical|important|low priority)\b", re.IGNORECASE)


@dataclass
class ExtractedItem:
    text: str
    priority: str | None = None
    assignee: str | None = None
    due_date: str | None = None


def _normalize_line(line: str) -> str:
    return line.strip().lstrip("-* ").strip()


def _detect_priority(text: str) -> str | None:
    lower = text.lower()
    match = PRIORITY_PATTERN.search(lower)
    if match:
        token = match.group(1).lower()
        if token.startswith("p") and token[1:].isdigit():
            level = int(token[1:])
            if level <= 1:
                return "high"
            if level <= 2:
                return "medium"
            return "low"
        return PRIORITY_KEYWORDS.get(token, "medium")
    for keyword, priority in PRIORITY_KEYWORDS.items():
        if keyword in lower:
            return priority
    return None


def _detect_assignee(text: str) -> str | None:
    match = ASSIGNEE_PATTERN.search(text)
    return match.group(1) if match else None


def _detect_due_date(text: str) -> str | None:
    match = DUE_DATE_PATTERN.search(text)
    return match.group(1) if match else None


def _is_action_line(line: str) -> bool:
    normalized = _normalize_line(line)
    if not normalized:
        return False

    lower = normalized.lower()
    if lower.startswith(ACTION_PREFIXES):
        return True

    checkbox = CHECKBOX_PATTERN.match(line)
    if checkbox:
        return True

    if NUMBERED_PATTERN.match(line) and any(verb in lower for verb in MODAL_VERBS):
        return True

    if any(lower.startswith(verb) for verb in MODAL_VERBS):
        return True

    if line.rstrip().endswith("!"):
        return True

    if re.search(r"\b(follow up|follow-up)\b", lower):
        return True

    return False


def _extract_text(line: str) -> str:
    checkbox = CHECKBOX_PATTERN.match(line)
    if checkbox:
        return checkbox.group(1).strip()

    numbered = NUMBERED_PATTERN.match(line)
    if numbered:
        return numbered.group(1).strip()

    return _normalize_line(line)


def extract_action_items(text: str) -> list[str]:
    """Backward-compatible helper returning plain action strings."""
    return [item.text for item in analyze_action_items(text)]


def analyze_action_items(text: str) -> list[ExtractedItem]:
    seen: set[str] = set()
    results: list[ExtractedItem] = []

    for raw_line in text.splitlines():
        if not _is_action_line(raw_line):
            continue

        extracted_text = _extract_text(raw_line)
        if not extracted_text:
            continue

        key = extracted_text.lower()
        if key in seen:
            continue
        seen.add(key)

        results.append(
            ExtractedItem(
                text=extracted_text,
                priority=_detect_priority(extracted_text),
                assignee=_detect_assignee(extracted_text),
                due_date=_detect_due_date(extracted_text),
            )
        )

    return results
