# NER Model Evaluation on Acknowledgements — Phase 5c Report

**Project**: G4_OPENSCIENCE — Knowledge Graph for Research Publications
**Course**: Open Science and Artificial Intelligence in Research Software Engineering, ETSI Informáticos, Universidad Politécnica de Madrid
**Repository**: https://github.com/SergioZSZ/OS-IA-Pipegrobid

---

## 1. Introduction and objective

This report documents the evaluation and selection of a Named Entity Recognition (NER) model for the **Acknowledgements** component of Deliverable 2. The assignment requires running NER over the acknowledgements section of a 30-paper corpus to extract the persons, organizations, and funded projects that will later populate the funding subgraph of the project's Knowledge Graph. Before that extraction can be trusted at corpus scale, a model has to be chosen — and the choice has to be defensible.

The course makes this requirement explicit. Session 11 (slide 26, *"Needed for assignments!"*) states that the use of a NER model must be justified on two fronts: the choice of model must rest on a **comparison of existing models**, and the model's performance must be measured **on the team's own data** by building a small annotated gold standard and computing precision, recall, and F1 per category. This phase delivers exactly that: a controlled comparison of four NER models against a manually annotated gold standard, with per-category metrics and a justified winner.

The evaluation targets three entity categories, fixed by the annotation guidelines and aligned with the project ontology:

- **PER** — persons explicitly thanked or acknowledged, annotated literally (initials such as `SS` or `A.-F. B.` are *not* expanded).
- **ORG** — organizations in the broad sense: funding agencies, institutions, foundations, framework programmes, collaborations, and named awards without a code.
- **PROJ** — strictly alphanumeric grant, award, or contract identifiers (e.g. `EP/S023356/1`, `851173`).

The gold standard consists of eight acknowledgements (`paper_03, 07, 09, 11, 13, 19, 27, 28`) annotated by hand in a consensus session, following the conventions recorded in `ANNOTATION_GUIDELINES.md`. These eight texts were deliberately chosen to span the range of acknowledgement structures present in the corpus: from a single-funder one-liner (`paper_03`) to a dense paragraph with nineteen named people and five organizations (`paper_28`).

The scope of this phase ends at model selection. The winning model is subsequently applied to all 30 papers to build the RDF funding graph, but that downstream step belongs to a later phase and is not covered here. This report concerns only **which model to use, and why**.

---

## 2. Models under evaluation

Selecting a NER model is not a matter of picking the highest-rated entry on a leaderboard. A model is only useful here if it can recognize the three categories this project needs (PER, ORG, PROJ) on the kind of text this project has (scientific acknowledgements). To answer the assignment's question honestly — *which kind of model should the group use?* — the four models were not chosen as four arbitrary candidates, but as four representatives of four distinct **approaches** to the task. The comparison is therefore between strategies, not just between model names.

### 2.1. Jean-Baptiste/roberta-large-ner-english — classical NER baseline

This is the model used as a worked example by the lecturer in Session 11 (slide 22). It is a RoBERTa-large model fine-tuned for token classification on standard English NER. It is included as the **baseline**: the reference point against which every other approach is measured. Including it answers a question the assignment implicitly poses — is a general-purpose, off-the-shelf NER model good enough, or does the task genuinely require something more specialized?

One property of this model must be stated up front, because it shapes the results: it emits the label set `PER / ORG / LOC / MISC`. It has **no label for grant codes**. `LOC` and `MISC` predictions are discarded during evaluation, and the PROJ category is, by design, unreachable for this model. This is not a defect to hide — it is exactly the kind of "does it support the entities you want to classify?" check that slide 24 tells students to perform before adopting a model.

### 2.2. kalawinka/flair-ner-acknowledgments — domain-specialized NER

This is a Flair model trained specifically on the acknowledgements sections of scientific papers (Smirnova & Mayr, *arXiv:2307.13377*). It represents the **domain-specialized** approach: instead of a general NER model, a model whose training data is the same genre of text the project is processing.

Its native label set has six tags, which are mapped onto the project's three categories: `IND` → PER; `UNI`, `FUND`, `COR` → ORG; `GRNB` → PROJ; `MISC` is discarded. Unlike the baseline, this model *can* produce PROJ predictions. Including it tests a reasonable hypothesis: a model trained on this exact genre might outperform both a generic NER model and a general-purpose LLM. Whether that hypothesis holds is one of the more interesting findings of the evaluation.

### 2.3. groq/llama-3.3-70b-versatile — large language model via Groq

This is a 70-billion-parameter Llama 3.3 model accessed through the Groq API. It directly reproduces the approach the lecturer demonstrates in Session 11 (slides 19–20), where Llama is prompted through Groq to extract persons, organizations, and project IDs as JSON. It represents the **LLM** approach: no task-specific training, the model is instead *instructed* via a prompt.

It is run with `temperature=0` and JSON-mode output, to make responses as deterministic and as machine-parseable as possible. The prompt encodes the annotation rules of the gold standard and includes a one-shot example.

### 2.4. hf/Qwen/Qwen2.5-7B-Instruct — large language model, different family

This is a 7-billion-parameter Qwen 2.5 Instruct model accessed through HuggingFace Inference Providers. It is the **second LLM**, included deliberately from a *different model family* (Qwen, not Llama) and at a very different scale (7B vs 70B). It runs with `temperature=0`, `max_tokens=1024`, JSON mode, and — crucially — **the exact same prompt as the Groq model**.

Using an identical prompt for both LLMs is a deliberate methodological choice. If the two LLMs were given different prompts, any performance gap between them could be attributed either to the model or to the prompt, and the comparison would be uninterpretable. With the prompt held constant, the LLM-vs-LLM difference isolates the effect of the model itself.

### 2.5. Summary of the design

| Model | Approach | Technology | Produces PROJ? |
|---|---|---|---|
| Jean-Baptiste/roberta-large-ner-english | Classical NER (baseline) | RoBERTa, token classification | No (by design) |
| kalawinka/flair-ner-acknowledgments | Domain-specialized NER | Flair, trained on acknowledgements | Yes (`GRNB` tag) |
| groq/llama-3.3-70b-versatile | LLM, instructed via prompt | Llama 3.3 70B, Groq API | Yes |
| hf/Qwen/Qwen2.5-7B-Instruct | LLM, instructed via prompt | Qwen 2.5 7B, HF Inference | Yes |

The four models span the realistic space of options a practitioner faces: a generic pretrained NER model, a NER model specialized in the exact genre, and two LLMs of different families and sizes. Two of the four (Jean-Baptiste and Groq) are the specific examples shown by the lecturer, which grounds the comparison in the course material. The remaining two extend it: one tests whether domain specialization beats generality, the other tests whether the LLM result generalizes across model families.

---

## 3. Evaluation methodology

A fair comparison of four models requires that every model be measured against the same ground truth, with the same matching rules, and the same metrics. This section documents those choices. Each is a deliberate decision with a rationale, and each is also a limitation to be aware of when reading the results.

### 3.1. The gold standard

The ground truth is `corpus/gold_standard.json`: eight acknowledgement texts (`paper_03, 07, 09, 11, 13, 19, 27, 28`), each annotated by hand with its PER, ORG, and PROJ entities. The annotations were produced by two annotators working in a consensus session, following the rules in `ANNOTATION_GUIDELINES.md`; disagreements were resolved with at least three group members present.

The eight texts were not chosen at random. They span the structural range of acknowledgements found across the 30-paper corpus: a single-funder one-liner (`paper_03`), medium statements combining a few people and organizations (`paper_11`, `paper_19`), a compact funding sentence with a framework programme and a grant code (`paper_13`), and a long dense paragraph naming nineteen people and five organizations (`paper_28`). This variety matters: a model that does well only on short, clean text would be exposed by the harder cases, and vice versa.

The single most important annotation rule, because it governs how every metric below is computed, is the **literal text principle**: entities are annotated exactly as they appear in the source. Initials are not expanded (`A.-F. B.` stays `A.-F. B.`, never `Anne-Florence Bitbol`); implicit entities are not inferred; variant spellings are not normalized. The reason is methodological — NER operates on the literal surface text, and expanding initials in the gold standard would penalize a model for not performing *entity resolution*, which is a separate task belonging to a later pipeline stage.

### 3.2. Matching policy

A model's prediction is compared against the gold standard as **sets of strings per category**, after a light normalization. Normalization is implemented in `utils.py:normalize_entity` and does three things: it strips leading/trailing whitespace, collapses runs of multiple spaces into one, and normalizes hyphens *only* where spacing around the hyphen is inconsistent. That last rule is deliberately narrow — the regex targets a hyphen with inconsistent surrounding spaces, so legitimate hyphens are left untouched. This protects both real hyphenated terms (`SARS-CoV-2`) and the grant codes (`EP/S023356/1`, `26-23955S`), which must not be altered or the PROJ category would break.

Normalization is intentionally *light*. A more aggressive normalization (lowercasing, stripping all punctuation, fuzzy matching) would inflate everyone's scores and blur exactly the distinctions the evaluation is meant to detect — for instance, whether a model correctly keeps `Prof.` attached to a name. Keeping normalization minimal means the metrics reflect real model behaviour, not the generosity of the matching code.

### 3.3. Counting: TP, FP, FN

For each category of each document, the model's predicted set and the gold set are compared:

- **True Positive (TP)** — an entity predicted by the model that is also in the gold standard for that category.
- **False Positive (FP)** — an entity predicted by the model that is *not* in the gold standard (a hallucination, a wrong span, or a misclassification into that category).
- **False Negative (FN)** — a gold entity the model failed to predict (a miss, a wrong span, or a misclassification *out of* that category).

Note that a span error counts twice: if the gold has `Prof. C.Z. Zhang` and the model predicts `C.Z. Zhang`, that is simultaneously one FN (the gold entity was missed) and one FP (a non-gold entity was emitted). This is the standard, strict way to score NER and it correctly penalizes partial matches.

### 3.4. Metrics

From the TP/FP/FN counts, the three standard metrics defined in Session 11 (slide 25) are computed:

- **Precision** = TP / (TP + FP) — of the entities the model predicted, how many were correct.
- **Recall** = TP / (TP + FN) — of the entities that truly exist, how many the model found.
- **F1** = 2 · Precision · Recall / (Precision + Recall) — the harmonic mean of the two.

Metrics are reported **per category** (PER, ORG, PROJ) and as an **overall** figure. All figures are **micro-averaged**: the TP, FP, and FN counts are summed across all eight documents first, and the metrics are computed once on those totals. Micro-averaging means every individual entity contributes equally to the result, so a long acknowledgement like `paper_28` carries more weight than a one-line one like `paper_03` — which is the desired behaviour, since the goal is to predict entities well, not documents well.

### 3.5. Known limitations of the methodology

Three limitations follow directly from the choices above and are stated here so the results are read correctly:

1. **Set-based comparison, not span offsets.** The gold standard records entities as strings, not as character offsets. Matching is therefore by string identity within a category, not by position in the text. A practical consequence: if the same entity string appeared twice in one acknowledgement, the set representation would collapse it to a single item. In this corpus that situation does not affect the counts, but it is a real limitation of the method and is acknowledged as such.
2. **Eight documents is a small sample.** As slide 26 notes, "the bigger the validation corpus, the better." Eight annotated acknowledgements are enough to produce a clear and defensible ranking, but the absolute metric values should be read as indicative, not as precise population estimates.
3. **LLM non-determinism.** Slide 18 lists "you may not obtain the same results twice" as a known LLM limitation. The two LLMs are run with `temperature=0` to make outputs as stable as possible, but determinism is not strictly guaranteed at the API level. The metrics for the LLMs reflect one execution run.

None of these limitations invalidates the comparison. They define its scope: this evaluation reliably answers *which of these four models performs best on this kind of text*, and the four-approach design makes that answer informative beyond the eight specific documents.

---

## 4. Results

The four models were run over the eight gold-standard acknowledgements and scored with the methodology of Section 3. This section presents the numbers; the *why* behind them is the subject of Section 5.

### 4.1. Overall ranking

| Model | Approach | Overall F1 |
|---|---|---|
| groq/llama-3.3-70b-versatile | LLM (Llama 3.3 70B) | **0.9489** |
| hf/Qwen/Qwen2.5-7B-Instruct | LLM (Qwen 2.5 7B) | 0.9051 |
| kalawinka/flair-ner-acknowledgments | Domain-specialized NER | 0.7460 |
| Jean-Baptiste/roberta-large-ner-english | Classical NER (baseline) | 0.6119 |

### 4.2. F1 per category

| Model | PER F1 | ORG F1 | PROJ F1 | Overall F1 |
|---|---|---|---|---|
| groq/llama-3.3-70b-versatile | 0.9565 | 0.9200 | 1.0000 | **0.9489** |
| hf/Qwen/Qwen2.5-7B-Instruct | 0.9565 | 0.8511 | 0.8571 | 0.9051 |
| kalawinka/flair-ner-acknowledgments | 0.7937 | 0.5778 | 1.0000 | 0.7460 |
| Jean-Baptiste/roberta-large-ner-english | 0.6857 | 0.6182 | 0.0000 | 0.6119 |

### 4.3. Full Precision / Recall / F1 breakdown

| Model | Category | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| groq/llama-3.3-70b-versatile | PER | 33 | 1 | 2 | 0.9706 | 0.9429 | 0.9565 |
| | ORG | 23 | 2 | 2 | 0.9200 | 0.9200 | 0.9200 |
| | PROJ | 9 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| | **Overall** | **65** | **3** | **4** | **0.9559** | **0.9420** | **0.9489** |
| hf/Qwen/Qwen2.5-7B-Instruct | PER | 33 | 1 | 2 | 0.9706 | 0.9429 | 0.9565 |
| | ORG | 20 | 2 | 5 | 0.9091 | 0.8000 | 0.8511 |
| | PROJ | 9 | 3 | 0 | 0.7500 | 1.0000 | 0.8571 |
| | **Overall** | **62** | **6** | **7** | **0.9118** | **0.8986** | **0.9051** |
| kalawinka/flair-ner-acknowledgments | PER | 25 | 3 | 10 | 0.8929 | 0.7143 | 0.7937 |
| | ORG | 13 | 7 | 12 | 0.6500 | 0.5200 | 0.5778 |
| | PROJ | 9 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| | **Overall** | **47** | **10** | **22** | **0.8246** | **0.6812** | **0.7460** |
| Jean-Baptiste/roberta-large-ner-english | PER | 24 | 11 | 11 | 0.6857 | 0.6857 | 0.6857 |
| | ORG | 17 | 13 | 8 | 0.5667 | 0.6800 | 0.6182 |
| | PROJ | 0 | 0 | 9 | 0.0000 | 0.0000 | 0.0000 |
| | **Overall** | **41** | **24** | **28** | **0.6308** | **0.5942** | **0.6119** |

### 4.4. Reading the table

Four observations stand out, each developed further in Section 5.

**The two LLMs clearly outperform the two dedicated NER models.** Groq Llama 3.3 (0.9489) and Qwen 2.5 (0.9051) sit well above the specialized Flair model (0.7460) and the classical baseline (0.6119). The gap is not marginal: the best LLM commits 3 false positives across the whole corpus, while the baseline commits 24. This is the headline result of the evaluation, and Section 7 examines a structural reason behind it.

**Domain specialization did not win.** A reasonable prior was that kalawinka — a model trained specifically on scientific acknowledgements — would lead. It did not. It outscores the generic baseline (0.7460 vs 0.6119), so specialization helps relative to a general NER model, but it lands far behind both general-purpose LLMs. Section 5.2 shows that a substantial part of its ORG gap is a *convention mismatch* rather than blindness, which qualifies this observation.

**PROJ splits the field sharply.** Two models score a perfect 1.0 on grant codes (Groq and kalawinka), one scores 0.0 (Jean-Baptiste), and one scores 0.8571 (Qwen). The 0.0 is structural, not a performance failure: the baseline has no label for grant codes and cannot produce PROJ predictions at all — the "does it support the entities you want?" check from slide 24, made concrete. Qwen's 0.8571 reflects perfect recall undermined by 3 false positives, analysed in Section 5.4.

**ORG is the hardest category for every model.** Each model scores its lowest, or near-lowest, F1 on ORG: 0.9200 for Groq, 0.8511 for Qwen, 0.5778 for kalawinka, 0.6182 for Jean-Baptiste. Organizations carry the structural difficulty of the task — long multi-token spans, acronym-plus-long-form pairs, named collaborations, and entities joined by "and" — which is precisely where span boundaries are hardest to get right.

The clear, consistent winner across overall score and per-category behaviour is **groq/llama-3.3-70b-versatile**. Section 6 sets out the justification in full.

---

## 5. Qualitative error analysis

The metrics in Section 4 rank the models. This section explains *why* they rank as they do, by examining the actual entities each model got wrong. The errors are read from `reports/evaluation_report.json`, which records the specific TP, FP, and FN entities for every category of every paper. Models are presented worst-to-best, so the analysis builds toward the winner.

### 5.1. Jean-Baptiste/roberta-large-ner-english — the baseline

The baseline records the lowest score (overall F1 0.6119) and its errors fall into four recognizable patterns.

**No PROJ by design.** All 9 grant codes are false negatives. The model's label set has no tag for grant identifiers, so every PROJ entity in the corpus — `IIS-2229876`, `851173`, `EP/S023356/1`, and the rest — is unreachable. This single structural fact accounts for the 0.0 PROJ score and drags the overall figure down considerably.

**Initials misclassified as ORG.** In `paper_11`, the person initials `SS` and `LM` are not recognized as PER; instead they surface as ORG false positives. The model has no notion that a bare two-letter token in an acknowledgement is very likely a person, and defaults to an organizational reading.

**Tokenization noise.** The model repeatedly emits a bare period `.` as an entity — as a PER false positive in `paper_11`, `paper_13`, `paper_19`, and `paper_27`. It also produces fragmentary spans: `ation on` (a slice of "Collaboration on…") and a lone `E` as ORG false positives in `paper_27` and `paper_28`. These are not recognition errors in any meaningful sense; they are artefacts of subword tokenization surfacing as entities.

**Span boundary errors.** Where the model does find the right entity, it often gets the boundary wrong. The handle `xlr8harder` is emitted as `lr8harder` — the leading character lost (`paper_07`). `Prof. C.Z. Zhang` loses its title and appears as `C.Z. Zhang` (`paper_11`). In `paper_28`, two people joined in text — "Yiheng Du, Michael Psenka" — are emitted as a *single* PER span instead of two. Each of these is scored, correctly, as one FP plus one FN.

The baseline is not a bad model; it is a general-purpose model meeting a task it was not built for. Its failure is informative precisely because it is the lecturer's worked example: it demonstrates, on real data, why slide 24's question — "does it support the entities you want to classify?" — must be asked before adoption.

### 5.2. kalawinka/flair-ner-acknowledgments — the domain-specialized model

This model improves on the baseline (overall F1 0.7460) and, notably, scores a perfect 1.0 on PROJ — its `GRNB` tag captures every grant code. Its weakness is concentrated in ORG (F1 0.5778), and the errors there deserve a careful, honest reading.

**Acronym and long form not separated.** The gold standard annotates `European Research Council` and `ERC` as two distinct ORG entities (guideline 3.3). In `paper_13`, kalawinka instead emits the whole string `European Research Council (ERC)` as one entity. This produces, at once, false negatives for both gold entities and a false positive for the merged string. The same single decision damages precision and recall together.

**Organizations joined by "and" are split wrongly.** In `paper_28` the text reads "Research Corporation for Science Advancement and Arnold and Mabel Beckman Foundation" — two distinct organizations. The model breaks them at the wrong point, emitting `Research Corporation for Science Advancement and Arnold` as one entity and `Mabel Beckman Foundation` as another. Both gold ORGs are missed; both emitted strings are false positives.

**Initials clipped.** Like the baseline, kalawinka mishandles initials, though differently: it tends to clip rather than misclassify. `A.-F. B.` is reduced to `F. B.` (`paper_13`), and `C. Lawrence Zitnick` loses its leading initial to become `Lawrence Zitnick` (`paper_28`).

**An honest qualification.** Part of kalawinka's ORG deficit is not blindness — it is a *convention mismatch*. The corpus this model was trained on annotated acronym-plus-long-form constructs differently from the convention adopted in this project's gold standard (guideline 3.3). When kalawinka emits `European Research Council (ERC)` as one span, it is applying its own training convention consistently, not failing to see the entity. Under a different but equally defensible annotation scheme, some of these "errors" would be correct. This does not change the ranking — the project needs a model that matches *its* gold standard — but it would be unfair to describe the entire ORG gap as a model deficiency. It is partly a measurement of convention distance.

### 5.3. groq/llama-3.3-70b-versatile — the winner

The Groq model is the cleanest of the four (overall F1 0.9489): 65 true positives against only 3 false positives and 4 false negatives across the whole corpus. Its few errors are minor and worth listing precisely, because an honest report names the winner's mistakes too.

- **`paper_09`** — emits `UKRI` as an ORG false positive. The acronym is not annotated as a standalone entity in the gold standard for this text, so the extra prediction counts against precision.
- **`paper_11`** — emits `C.Z. Zhang` instead of the gold `Prof. C.Z. Zhang`. The academic title, which guideline 3.4 requires to be kept when attached in text, is dropped from the span. One FP, one FN.
- **`paper_19`** — misses `national SARS-CoV-2 biosurveillance initiative`, an ORG. This is a genuine recall miss: a lowercase, descriptively-phrased organization is harder to recognize as a named entity than a capitalized institutional name.
- **`paper_27`** — emits `Stanford Medicine Post-Baccalaureate Experience In Research` without the final word `program` present in the gold span (one FP, one FN), and misses `SAB`, a person given only as a parenthetical initialism after a grant code.

These four issues share a profile: boundary precision on long or unusually-formed spans, and one hard recall miss. There is no tokenization noise, no hallucination, no category confusion. The model respects the literal-text principle, the strict PROJ definition (a perfect 1.0, 9/9 with no false positives), and the span-cleanliness rule almost everywhere. This is the behaviour profile of a model that is genuinely usable downstream.

### 5.4. hf/Qwen/Qwen2.5-7B-Instruct — the second LLM

Qwen is the second-best model (overall F1 0.9051) and matches Groq exactly on PER (0.9565). Its gap to Groq is concentrated in two categories and two specific failure modes characteristic of LLMs.

**PROJ precision broken by category confusion.** Qwen reaches perfect PROJ recall (it finds every grant code) but scores only 0.7500 precision, because in `paper_27` it places three things in PROJ that are not grant codes: `SAB` (a person), and two organizations — `Simons Foundation Collaboration on the Physics of Learning and Neural Computation` and `Schmidt Sciences Polymath Award`. The strict PROJ definition (guideline 2.3: alphanumeric codes only) is explicitly stated in the shared prompt, and Qwen still violated it. This is a classification error: the model recognized the entities but assigned two of them to the wrong category and invented a third.

**Hallucination of a prompt entity.** In `paper_11`, Qwen emits `J.K.` as a person. `J.K.` does not appear anywhere in the `paper_11` text — it is an entity from the fictional one-shot example embedded in the shared prompt. The model copied an illustrative entity from its instructions into its output. This is a textbook LLM hallucination, and a useful one to document: it is a known risk of one-shot prompting (the example leaks into the answer), and it is exactly the kind of behaviour slide 18 warns about.

**ORG recall lower than Groq.** Qwen misses 5 ORG entities to Groq's 2. In `paper_07` it misses `Prime Intellect`; in `paper_27` it misses the longer, more complex organization names. Same category, same kind of difficulty as the other models — long multi-token organizational spans — but Qwen, the smallest model in the comparison at 7B, handles them less reliably than the 70B Groq model.

Qwen's profile confirms the LLM approach generalizes beyond a single model family — a 7B Qwen still beats both dedicated NER models comfortably — while also showing that scale and model choice matter: the same prompt on a larger, different model (Groq) yields cleaner category discipline and fewer hallucinations.

### 5.5. Summary of error patterns

| Model | Dominant error pattern | Consequence |
|---|---|---|
| Jean-Baptiste | No PROJ label; tokenization noise; span boundaries; initials → ORG | Lowest precision and recall; 24 FP, 28 FN |
| kalawinka | Acronym/long-form merged; "and"-joined ORGs split wrongly; clipped initials | ORG F1 collapses; partly a convention mismatch |
| Qwen 2.5 7B | PROJ category confusion; hallucinated prompt entity; weaker ORG recall | Strong but behind Groq on ORG and PROJ precision |
| Groq Llama 3.3 70B | Minor span-boundary slips on long/unusual entities; one recall miss | 3 FP, 4 FN total — cleanest model |

---

## 6. Justification of the selected model

The evaluation selects **groq/llama-3.3-70b-versatile** as the NER model for the Acknowledgements component. The justification rests on four points, in line with what Session 11 (slide 26) requires: a choice grounded in a comparison of existing models and in measured performance on the project's own data.

**1. Highest overall performance, by a clear margin.** Groq Llama 3.3 reaches an overall F1 of 0.9489, ahead of Qwen 2.5 (0.9051), kalawinka (0.7460), and the classical baseline (0.6119). The margin over the second-best model is roughly four F1 points, and over the dedicated NER models it is twenty to thirty-three points. This is not a narrow win that could flip with a slightly different sample.

**2. Balanced across all three categories.** The winning model is not strong in one category and weak in another. It scores 0.9565 on PER, 0.9200 on ORG, and a perfect 1.0000 on PROJ. Every other model has at least one category where it is clearly deficient: the baseline collapses to 0.0 on PROJ, kalawinka drops to 0.5778 on ORG, and Qwen falls to 0.8511 on ORG and 0.8571 on PROJ. Because the downstream Knowledge Graph needs all three entity types, balance matters as much as the headline figure — a model that is excellent on PER but weak on PROJ would leave the funding subgraph incomplete.

**3. The cleanest error profile.** Across the entire corpus the model produces only 3 false positives and 4 false negatives. Its mistakes, examined in Section 5.3, are all of one benign kind — minor span-boundary slips on long or unusually-formed entities, plus a single hard recall miss. Critically, it shows *none* of the failure modes that would make a model risky to run unsupervised at corpus scale: no tokenization noise, no hallucinated entities, no category confusion. A perfect 1.0 on PROJ with zero false positives means every grant code it reports can be trusted directly.

**4. Reproducible and practical to deploy.** The model is run with `temperature=0` and JSON-mode output, which makes its responses as deterministic as the API allows and directly machine-parseable — no fragile post-processing of free text. Access is through the Groq API, requiring only an API key, with no local GPU, no model download, and no training. For a 30-paper corpus this is the lightest possible deployment path. It also reproduces the exact approach the lecturer demonstrates in Session 11 (slides 19–20), so the choice is consistent with the course material.

**A note on the runner-up.** Qwen 2.5 7B is a credible second choice and confirms that the LLM approach is not tied to one model family. It was not selected because its two weak spots are precisely the ones that would cause downstream damage: PROJ category confusion (it misfiled organizations as grant codes) and a prompt-entity hallucination. Both inject *wrong* data into the graph, which is harder to detect and repair than a simple miss. Groq's cleaner discipline is worth more here than Qwen's smaller size or any cost difference.

The recommendation, therefore, is unambiguous: **groq/llama-3.3-70b-versatile** is the model used to extract PER, ORG, and PROJ entities from the acknowledgements of the full 30-paper corpus in the subsequent pipeline stage.

---

## 7. A methodological note: the structural advantage of LLMs

Section 4 showed the two LLMs clearly ahead of the two dedicated NER models. Before accepting that result at face value, one asymmetry in the evaluation must be made explicit, because intellectual honesty requires it and because it changes how the numbers should be interpreted.

**The asymmetry.** The two LLMs (Groq, Qwen) were given a prompt that encodes the annotation rules of the gold standard: that initials are not expanded, that framework programmes are ORG and only alphanumeric codes are PROJ, that acronym and long form are separate entities, and so on. The prompt effectively *teaches the model the answer key's conventions* before it sees the text. The two dedicated NER models (Jean-Baptiste, kalawinka) received no such thing — they cannot. A token-classification model applies only what it learned during its own training; there is no channel through which the project's annotation guidelines can be communicated to it at inference time. The LLMs were instructed; the NER models were not, and could not be.

**Why this does not invalidate the comparison.** This asymmetry is not a flaw in the experimental design — it *is* the finding. Instructability is a real, intrinsic property of the LLM approach, not an unfair handicap granted to one side. In any actual deployment, the practitioner *would* write that prompt; the ability to align a model to a specific annotation convention through natural-language instructions, with no retraining, is precisely one of the practical advantages an LLM offers (Session 11, slide 18: "easier to query them"). Measuring the LLMs *with* a prompt is measuring them as they would really be used. Stripping the prompt to "level the field" would not produce a fairer comparison — it would produce a comparison of a capability the project would never actually deploy.

**What it does change.** It means the gap between the LLMs and the NER models should not be read as "LLMs are intrinsically 20-30 F1 points better at recognizing entities." A fairer statement is: *an instructable model that can be aligned to the project's exact annotation conventions outperforms a fixed model that cannot, on a task where those conventions are detailed and specific.* The conventions in this project are unusually detailed — strict PROJ definition, literal-text principle, acronym handling — so the value of instructability is correspondingly high. On a task with looser or more standard conventions, the gap would likely be smaller.

**A corollary for the NER models.** This same asymmetry reframes part of the NER models' errors. As noted in Section 5.2, several of kalawinka's ORG "errors" are a convention mismatch: it annotates acronym-plus-long-form the way *its* training corpus did. The LLMs avoid that specific error not because they are better at recognition, but because the prompt told them which convention to follow. The NER models were never given that chance. This is the honest framing: the evaluation measures fitness *for this project's conventions*, and the LLMs' advantage is largely an advantage in convention alignment.

None of this dislodges the conclusion of Section 6. Groq Llama 3.3 remains the correct choice — the project needs a model that produces entities matching its gold standard, and instructability is exactly how that is achieved. But a reader of this report should understand that the headline gap reflects *instructability plus recognition*, not recognition alone.

---

## 8. Limitations

This evaluation produces a clear and defensible model choice, but its scope has boundaries. They are stated here so the results are neither over-read nor dismissed. Some of these limitations were introduced alongside the methodology in Section 3; they are collected here in one place.

**Small validation corpus.** The gold standard contains 8 annotated acknowledgements, holding 69 entities in total. Session 11 (slide 26) explicitly notes that "the bigger the validation corpus, the better." Eight documents are sufficient to produce a clear ranking — the gaps between models are large and consistent across categories — but the absolute metric values should be read as indicative rather than as precise population estimates. A single annotation decision on a single entity can move a per-category F1 by a noticeable amount at this sample size.

**Set-based comparison without span offsets.** The gold standard records entities as strings, not character offsets, so matching is by string identity within a category rather than by position (Section 3.5). If an identical entity string occurred twice within one acknowledgement, the set representation would collapse it to one item; this does not affect the counts in the current corpus, but it is a real limitation of the method. It also means the evaluation cannot distinguish two different occurrences of the same name, which a position-aware evaluation could.

**LLM non-determinism.** Slide 18 lists "you may not obtain the same results twice" as an intrinsic LLM limitation. Both LLMs were run with `temperature=0` to make outputs as stable as possible, but determinism is not strictly guaranteed at the API level. The metrics reported for Groq and Qwen reflect a single execution run; a repeated run could differ slightly. The two dedicated NER models do not have this limitation — their output is deterministic.

**The prompt asymmetry.** As developed in Section 7, the two LLMs received the gold standard's annotation conventions through their prompt, while the two NER models could not. This is a legitimate reflection of how the approaches differ in practice, but it means the measured gap reflects instructability *and* recognition, not recognition alone.

**Annotation is a single consensus reference.** The gold standard was produced by two annotators in consensus rather than by independent annotation with a measured inter-annotator agreement score. The conventions in `ANNOTATION_GUIDELINES.md` are detailed and were applied consistently, but no formal agreement metric (e.g. Cohen's kappa) is reported. On genuinely ambiguous cases, a different annotator pair could have reached a different reference.

**Scope of the result.** The evaluation answers one specific question: which of these four models best extracts PER, ORG, and PROJ entities from scientific acknowledgements, under this project's annotation conventions. It does not measure entity resolution (linking `A.-F. B.` to a person record), relationship extraction (which funder gave which grant), or performance on text other than acknowledgements. Those are separate tasks belonging to later pipeline stages.

None of these limitations undermines the central conclusion. The performance gaps are wide enough, and consistent enough across categories and across documents of very different structure, that the ranking is robust to the sample size. The evaluation reliably identifies **groq/llama-3.3-70b-versatile** as the model best suited to this task, and the four-approach design makes that finding informative beyond the eight documents it was measured on.

---

## 9. Conclusion

This phase addressed the requirement set out in Session 11 (slide 26): to justify the choice of a NER model through a comparison of existing models and an evaluation on the project's own annotated data.

Four models, chosen to represent four distinct approaches — a classical NER baseline, a domain-specialized NER model, and two LLMs of different families — were evaluated against a manually annotated gold standard of 8 acknowledgements, with precision, recall, and F1 computed per category. **groq/llama-3.3-70b-versatile** was selected, with an overall F1 of 0.9489, balanced performance across all three entity categories, and the cleanest error profile of the four models. This is the model applied to the full 30-paper corpus in the subsequent stage of the pipeline, where the extracted persons, organizations, and projects populate the funding subgraph of the Knowledge Graph.
