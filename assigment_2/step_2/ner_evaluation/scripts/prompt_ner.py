"""
Shared prompt for LLM-based NER on scientific acknowledgements.

This module defines the single prompt used by BOTH LLM prediction scripts
(03_predict_groq.py and 04_predict_hf_inference.py). Keeping the prompt
identical across both models ensures the comparison measures the model's
capability, not differences in prompting.

The prompt encodes the annotation rules of our gold standard (see
corpus/ANNOTATION_GUIDELINES.md), so that LLM output is directly comparable
to the manual annotations.

The one-shot example below is FICTIONAL and does NOT correspond to any of the
8 documents in the gold standard. This avoids leaking test-set content into
the prompt.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# System prompt: defines the task, categories, rules and output format.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT: str = """\
You are an expert information extraction system specialized in the \
Acknowledgements sections of scientific papers.

Your task: given an acknowledgement text, extract named entities into exactly \
three categories and return them as JSON.

CATEGORIES:

1. PER - Person.
   A person thanked, acknowledged or recognized for a contribution.
   Includes full names (e.g. "Daniel Garijo"), initials (e.g. "SS", "A.-F. B."),
   names with academic titles written inline (e.g. "Prof. C.Z. Zhang"), and
   online handles referring to a person (e.g. "xlr8harder").
   Does NOT include pronouns or generic references ("our collaborators",
   "the authors", "the team").

2. ORG - Organization.
   Any organizational entity: universities, research centers, funding agencies,
   foundations, companies providing resources, government departments,
   supranational bodies, research groups, collaborations and named initiatives.
   IMPORTANT: funding framework programmes (e.g. "Horizon 2020", "FP7",
   "Marie Sklodowska-Curie Actions") are ORG, not PROJ.
   IMPORTANT: named awards that have a proper name but NO alphanumeric code
   (e.g. "Schmidt Sciences Polymath Award") are ORG, not PROJ.
   Does NOT include software, libraries or tools (e.g. "PyTorch", "FEniCS",
   "GitHub"), and does NOT include URLs or web addresses.

3. PROJ - Project / Grant / Award identifier.
   ONLY alphanumeric identifier codes of grants, awards or contracts
   (e.g. "IIS-2229876", "EP/S023356/1", "851173", "26-23955S",
   "SA-AUT-2024-015b").
   Does NOT include the names of programmes or awards, only their codes.

ANNOTATION RULES:

- Literal text: annotate entities exactly as they appear in the text. Do NOT
  expand initials (annotate "A.-F. B.", never "Anne-Florence Bitbol").
- Clean spans: do not include leading determiners or connectors. Annotate
  "US Office of Naval Research", not "the US Office of Naval Research".
  Annotate "EP/S023356/1", not "grant number EP/S023356/1".
- Long form and acronym: when an entity appears as a long form followed by its
  acronym in parentheses, output BOTH as SEPARATE entities of the same type.
  Example: "the National Eye Institute (NEI)" -> ORG: "National Eye Institute"
  AND ORG: "NEI".
- Do not infer entities that are not literally written in the text.

OUTPUT FORMAT:

Return ONLY a valid JSON object, with no extra text, no explanation, no
markdown fences. The object must have exactly these three keys, each mapping
to a list of strings (use an empty list if there are no entities):

{"PER": [...], "ORG": [...], "PROJ": [...]}
"""


# ---------------------------------------------------------------------------
# One-shot example: a FICTIONAL acknowledgement, not present in the gold set.
# It is crafted to illustrate the tricky rules: initials, long-form+acronym
# split, framework programme as ORG, named award without code as ORG, and a
# grant code as PROJ.
# ---------------------------------------------------------------------------

EXAMPLE_INPUT: str = (
    "Acknowledgements We thank Maria Olsen and J.K. for helpful discussions. "
    "This work was supported by the National Research Foundation (NRF) under "
    "the European Union's Horizon Europe programme (grant agreement No. "
    "990123), and by a Turing Excellence Award."
)

EXAMPLE_OUTPUT: str = (
    '{"PER": ["Maria Olsen", "J.K."], '
    '"ORG": ["National Research Foundation", "NRF", "European Union", '
    '"Horizon Europe", "Turing Excellence Award"], '
    '"PROJ": ["990123"]}'
)


# ---------------------------------------------------------------------------
# Builder for the user message.
# ---------------------------------------------------------------------------

def build_user_message(acknowledgement_text: str) -> str:
    """Build the user message for a given acknowledgement text.

    The message includes the one-shot example followed by the real text to
    process. This anchors the model to the expected output format and rules.
    """
    return (
        "Here is one solved example.\n\n"
        f"EXAMPLE INPUT:\n{EXAMPLE_INPUT}\n\n"
        f"EXAMPLE OUTPUT:\n{EXAMPLE_OUTPUT}\n\n"
        "Now process the following text. Return ONLY the JSON object.\n\n"
        f"INPUT:\n{acknowledgement_text}"
    )
