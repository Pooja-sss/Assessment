# KeaBuilder AI Assessment

This folder contains a lightweight submission pack for the Dream Reflection Media AI Engineer assessment.

## What is included

- `assessment_answers.md`: polished answers for the form
- `lead_ai_demo.py`: working lead-processing workflow demo
- `sample_leads.json`: example form submissions
- `sample_outputs.json`: example processed outputs from the demo

## What the demo does

The demo simulates an AI workflow inside KeaBuilder:

1. Accept a lead submitted through a funnel form
2. Normalize and validate the payload
3. Score the lead using transparent business rules
4. Classify the lead as `hot`, `warm`, `cold`, or `needs_review`
5. Build prompts for:
   - AI classification
   - AI response generation
6. Generate a human-sounding reply
7. Return structured JSON that can be stored or pushed into CRM/automation flows

The script works offline with a deterministic rules-based reply so it can be demonstrated without API keys.

## Run locally

```powershell
python assessment/lead_ai_demo.py
```

To process the bundled sample file explicitly:

```powershell
python assessment/lead_ai_demo.py assessment/sample_leads.json
```

## Suggested submission package

- Share this folder as a ZIP or GitHub repo
- Paste the contents of `assessment_answers.md` into the form
- Use `sample_outputs.json` as evidence of implementation
- In the Loom video, walk through:
  - the architecture decisions
  - the scoring rules
  - the prompts
  - the fallback strategy
