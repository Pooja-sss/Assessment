# Question 1 - Lead Processing and Intelligent Response

## Question

Design how KeaBuilder would use AI to process incoming leads from forms and respond intelligently.

Answer along with implementation:

- a. How would you classify leads into hot, warm, cold based on form inputs?
- b. Write the prompt for:
  - Classification
  - Response generation
- c. How would you ensure responses feel human and personalized?
- d. How would you handle incomplete or unclear inputs?
  Show sample input -> output (JSON format)

## Answer

I would implement lead handling as an event-driven workflow inside KeaBuilder:

1. A user submits a funnel form.
2. The backend normalizes the payload and validates required fields.
3. A lead scorer computes a transparent score from budget, urgency, business type, company size, and message intent.
4. The lead is classified into `hot`, `warm`, `cold`, or `needs_review`.
5. The system generates a personalized reply and stores both the structured result and generated message.
6. Based on category, KeaBuilder triggers CRM sync, internal alerts, or nurture automation.

### a. Lead Classification Logic

I would combine deterministic scoring with LLM reasoning:

- `Urgency`: immediate or this week strongly increases score
- `Budget`: higher budget signals readiness
- `Intent`: phrases like "launch", "book calls", "landing page", "automation", or "urgent" increase score
- `Company size`: larger teams usually have stronger commercial value
- `Completeness`: if critical fields are missing, classify as `needs_review`

Example thresholds:

- `hot`: score >= 75 and no major missing fields
- `warm`: score 45-74
- `cold`: score < 45
- `needs_review`: missing critical fields or unclear message

### b. Prompts

#### Classification Prompt

```text
You are an AI lead triage assistant for KeaBuilder, a SaaS platform for funnels, lead capture, and automation.

Classify the lead into one of: hot, warm, cold, needs_review.

Rules:
- Hot: urgent timeline, clear commercial intent, sufficient budget, strong purchase signal
- Warm: real interest but moderate urgency or moderate budget
- Cold: vague interest, weak urgency, limited budget, low buying signal
- Needs_review: missing critical inputs or message is too unclear to classify confidently

Return JSON only with:
{
  "category": "hot|warm|cold|needs_review",
  "confidence": 0-1,
  "reasoning": ["short reason", "short reason"],
  "follow_up_questions": ["question 1", "question 2"]
}

Lead:
{
  "name": "Rahul",
  "business_type": "Gym",
  "budget": 5000,
  "urgency": "Immediate",
  "goal": "Launch a landing page and booking funnel",
  "message": "We need a landing page urgently for our gym and want to start generating trial bookings this week."
}
```

#### Response Generation Prompt

```text
You are KeaBuilder's AI sales assistant.

Write a short, warm, human reply to this inbound lead.

Guidelines:
- Use the lead's first name if available
- Mention their business type or goal when possible
- Match the urgency without sounding pushy
- Sound like a helpful human, not a template
- Keep it between 50 and 90 words
- If information is missing, ask one clear follow-up question

Lead category: hot
Lead data:
{
  "name": "Rahul",
  "business_type": "Gym",
  "goal": "Launch a landing page and booking funnel",
  "urgency": "Immediate"
}

Return JSON only:
{
  "subject": "email subject",
  "reply": "message body"
}
```

### c. How I keep responses human and personalized

- Use structured lead fields so the reply references real context, not generic templates
- Personalize with name, business type, goal, urgency, and pain point
- Keep tone warm and concise
- Add prompt rules that explicitly avoid robotic phrases and overselling
- Store prior messages so later replies can use conversation memory

### d. Handling incomplete or unclear inputs

- Mark records with missing critical fields as `needs_review`
- Ask one follow-up question instead of generating a confident but weak answer
- Use conservative scoring when budget or urgency is missing
- Log confidence and route very low-confidence results to human review

### Sample Input -> Output

```json
{
  "lead": {
    "name": "Rahul",
    "email": "rahul@example.com",
    "business_type": "Gym",
    "company_size": "11-50",
    "budget": 5000,
    "urgency": "Immediate",
    "goal": "Launch a landing page and booking funnel",
    "message": "We need a landing page urgently for our gym and want to start generating trial bookings this week."
  },
  "score": 95,
  "category": "hot",
  "missing_fields": [],
  "unclear_signals": [],
  "scoring_reasons": [
    "high_urgency",
    "strong_budget",
    "team_with_growth_potential",
    "intent:launch",
    "intent:landing page",
    "intent:funnel",
    "intent:urgent"
  ],
  "response": {
    "subject": "KeaBuilder inquiry for Gym",
    "reply": "Hi Rahul, thanks for reaching out. It sounds like you want help with Launch a landing page and booking funnel for Gym, and your timeline is active. We'd be a great fit to move quickly here. If you're available, send your target launch date and current funnel status, and we can suggest the fastest next step."
  }
}
```

Implementation: [lead_ai_demo.py](./lead_ai_demo.py)
