"""Extract individual requirements and their priority from a job description."""

import re
from dataclasses import dataclass
from typing import Literal


Priority = Literal["required", "preferred", "unspecified"]

_HEADINGS: dict[str, Priority] = {
    "requirements": "required",
    "job requirements": "required",
    "qualification requirements": "required",
    "position requirements": "required",
    "minimum requirements": "required",
    "minimum qualifications": "required",
    "minimum required qualifications": "required",
    "basic qualifications": "required",
    "required qualifications": "required",
    "required skills": "required",
    "required education and experience": "required",
    "required": "required",
    "must have": "required",
    "must haves": "required",
    "preferred qualifications": "preferred",
    "preferred skills": "preferred",
    "preferred education and experience": "preferred",
    "preferred": "preferred",
    "desired qualifications": "preferred",
    "nice to have": "preferred",
    "nice to haves": "preferred",
    "bonus points": "preferred",
    "qualifications": "unspecified",
    "qualifications & requirements": "unspecified",
    "skills and experience": "unspecified",
    "what you bring": "unspecified",
    "what you have": "unspecified",
}

_OTHER_HEADING = re.compile(
    r"(?:(?:key|main|primary|essential|job|core) )?(?:duties|responsibilities)"
    r"|(?:duties and responsibilities|responsibilities and duties)"
    r"|(?:about|meet) (?:the .+|us|you)"
    r"|what you(?:'ll| will) do|what we offer|why join us"
    r"|(?:perks & |employee )?benefits|compensation|salary|overview|job description"
    r"|job summary|how to apply|learn more|eeo[c]?",
    re.IGNORECASE,
)
_BULLET = re.compile(r"^(?:[-*+–—]\s+|[•·▪◦●]\s*|(?:\d+[.)]|\(\d+\))\s+)")
_INLINE_BULLET = re.compile(r"\s*[•·▪◦●]\s*")
_EMBEDDED_HEADING = re.compile(
    r"(?<=[.!?])(?=[ \t]*(?:"
    + "|".join(re.escape(heading) for heading in _HEADINGS)
    + "|" + _OTHER_HEADING.pattern + r")[ \t]*:)",
    re.IGNORECASE,
)
_SENTENCE_BREAK = re.compile(
    r"(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bU\.S\.)(?<!\bB\.S\.)(?<!\bM\.S\.)"
    r"(?<=[.!?])(?:\s+(?=[A-Z0-9])|(?<=[a-z)]\.)(?=[A-Z][a-z]))"
)
_TRAILING_HASHTAGS = re.compile(r"(?<=[.!?])(?:\s*#[\w-]+)+\s*$")

_REQUIRED = re.compile(
    r"\bmust(?:-have|\s+(?:have|be|hold|possess|demonstrate|know))\b"
    r"|\b(?:is|are)\s+(?:strictly\s+)?required\b"
    r"|^required\b|\brequired(?=[\s).!]*$)",
    re.IGNORECASE,
)
_PREFERRED = re.compile(
    r"\b(?:not (?:required|mandatory)|optional|nice[- ]to[- ]have)\b"
    r"|\b(?:is|are)\s+(?:(?:strongly|highly|also)\s+)?(?:preferred|desired|desirable)\b"
    r"|^preferred\b|\b(?:preferred|desired|desirable|a plus|an advantage|a bonus)(?=[\s).!]*$)",
    re.IGNORECASE,
)
_QUALIFICATION = re.compile(
    r"^(?:(?:you (?:have|bring|need)|candidates? (?:should have|will have))\b"
    r"|requires? experience\b"
    r"|(?:(?:strong|proven|demonstrated|hands-on|practical|working|prior|previous)\s+)*"
    r"experience (?:with|in|using|working|building|developing|managing|leading)\b"
    r"|(?:proficiency|proficient|skilled|knowledge|understanding|familiarity) (?:in|of|with)\b)"
    r"|\b\d+\s*(?:(?:[-–]|to)\s*\d+\s*)?\+?\s+years?\b[^.!?]*\bexperience\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Requirement:
    """The original requirement text and its one-based source line."""

    text: str
    priority: Priority
    line_number: int


def _priority(text: str, default: Priority | None) -> Priority | None:
    # Optional wording is checked first so "not required" counts as preferred.
    if _PREFERRED.search(text):
        return "preferred"
    if _REQUIRED.search(text):
        return "required"
    if default is None and _QUALIFICATION.search(text):
        return "unspecified"
    return default


def _items(text: str, *, bullet: bool) -> list[str]:
    if bullet:
        return _INLINE_BULLET.split(text)
    text = _TRAILING_HASHTAGS.sub("", text)
    return [
        sentence
        for part in _INLINE_BULLET.split(text)
        for sentence in _SENTENCE_BREAK.split(part)
    ]


def extract_requirements(job_description: str) -> list[Requirement]:
    """Return requirements in source order, preserving wording and alternatives.

    Recognized qualification sections supply the default priority. If none are
    present, only text with a qualification or priority cue is returned.
    """
    # Some postings lose their section breaks when copied from a website.
    lines = [
        (number, part)
        for number, line in enumerate(job_description.splitlines(keepends=True), start=1)
        for part in ([line] if _BULLET.match(line.lstrip()) else _EMBEDDED_HEADING.split(line))
    ]
    requirements: list[Requirement] = []
    fallback: list[Requirement] = []
    section_priority = None
    has_qualification_heading = False
    line_index = 0

    while line_index < len(lines):
        line_number, source_line = lines[line_index]
        line_index += 1
        text = source_line.strip()
        if not text:
            continue

        marker = _BULLET.match(text)
        if marker:
            text = text[marker.end():]

        heading_text, separator, inline_text = text.partition(":")
        heading = " ".join(heading_text.strip("#* ").lower().replace("-", " ").split())
        if heading_text.startswith("**") and not heading_text.endswith("**"):
            inline_text = inline_text.removeprefix("**")
        if heading in _HEADINGS:
            section_priority = _HEADINGS[heading]
            has_qualification_heading = True
            text = inline_text.strip()
            marker = None
            if not text:
                continue
        elif _OTHER_HEADING.fullmatch(heading):
            section_priority = None
            text = inline_text.strip()
            marker = None
            if not text:
                continue
        elif (
            not marker
            and separator
            and not inline_text
            and len(heading.split()) <= 6
            and _priority(heading_text, None) is None
        ):
            section_priority = None
            continue

        if marker:
            # An indented, non-list line continues the same bullet.
            indent = len(source_line) - len(source_line.lstrip())
            text = source_line.lstrip()[marker.end():]
            while line_index < len(lines):
                next_number, continuation = lines[line_index]
                stripped = continuation.lstrip()
                if (
                    next_number == line_number
                    or not stripped
                    or len(continuation) - len(stripped) <= indent
                ):
                    break
                next_heading = stripped.strip().strip(":").lower()
                if (
                    _BULLET.match(stripped)
                    or stripped.rstrip().endswith(":")
                    or next_heading in _HEADINGS
                    or _OTHER_HEADING.fullmatch(next_heading)
                ):
                    break
                text += continuation
                line_index += 1

        for item in _items(text, bullet=marker is not None):
            item = item.strip()
            if not item:
                continue
            priority = _priority(item, section_priority)
            if priority is not None:
                target = requirements if section_priority is not None else fallback
                target.append(Requirement(item, priority, line_number))

    return requirements if has_qualification_heading else fallback
