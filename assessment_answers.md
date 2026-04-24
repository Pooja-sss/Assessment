# Dream Reflection Media - AI Engineer Assessment

## 1. Lead Processing and Intelligent Response

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

## 2. Multi-Provider Content Generation

I would build a provider-router service that exposes one internal API to the frontend while routing requests to specialized providers.

### Routing Logic

- `image` -> image provider such as OpenAI Images or another image model provider
- `video` -> video provider such as Runway or another video generation API
- `voice` -> TTS/voice provider such as ElevenLabs or OpenAI speech

Routing decisions should depend on:

- requested asset type
- user plan and quotas
- provider health
- latency and cost
- brand-specific requirements such as LoRA or voice cloning

### Frontend -> Backend Flow

1. Builder UI sends a request like:

```json
{
  "type": "image",
  "prompt": "Luxury gym ad banner with bold CTA",
  "project_id": "proj_123",
  "page_id": "page_456"
}
```

2. Backend validates input and creates a job record.
3. Router selects the provider.
4. Generation happens synchronously for fast tasks or asynchronously for heavy jobs.
5. Frontend polls or listens via WebSocket/SSE for status updates.

### Output Management

- Store generated files in object storage such as S3
- Save metadata in DB:
  - prompt
  - provider
  - asset URL
  - project/page association
  - generation status
  - cost and latency
- Surface the asset in the builder media library so users can reuse it across funnels and templates

## 3. Personalized AI Images with LoRA

For consistent faces or branded visuals, I would treat LoRA as a user-owned style adapter in the image pipeline.

### Integration Flow

1. User uploads 10-20 approved training images.
2. Backend runs preprocessing and moderation.
3. A training job creates a LoRA adapter and stores:
   - `lora_model_id`
   - owner `user_id`
   - trigger token
   - training status
4. When the user generates an image, the backend passes the selected `lora_model_id` into the image inference request.

### In-Product Experience

- User chooses `Brand Style` or `My Face Model` in the KeaBuilder UI
- Backend injects the LoRA adapter into the generation request
- Final image metadata stores both base model and LoRA id for reproducibility

This keeps the UX simple while supporting consistent personal branding.

## 4. Face or Text Similarity Search

I would implement similarity search with embeddings plus vector retrieval.

### Storage

- Images:
  - store original file in object storage
  - store image embedding in a vector database
- Text/templates:
  - store raw content in relational DB
  - store text embeddings in vector database

### Retrieval

1. Convert the query image or text to an embedding.
2. Run nearest-neighbor search in a vector DB such as Pinecone, Weaviate, pgvector, or FAISS.
3. Filter by tenant, asset type, campaign, or brand.

### Matching Logic

- cosine similarity for embeddings
- optional metadata filters for user/project separation
- threshold-based match acceptance
- hybrid ranking:
  - semantic similarity from vectors
  - recency
  - usage/popularity

Use cases:

- find similar funnel templates
- find similar brand images
- recommend pages based on similar user prompts

## 5. Fallback Strategy for Multi-AI Services

The platform should degrade gracefully without breaking the user experience.

### Fallback Design

- retry transient failures 1-2 times with exponential backoff
- enforce timeouts per provider
- route to a backup provider when primary fails
- save the job in a queue if both providers fail temporarily
- return a job id immediately so the UI does not freeze

### UX Behavior

- show `Generating...` while the backend works
- if fallback is triggered, keep the same job visible to the user
- if delayed, notify the user in-app or by email when complete
- if failure persists, show a friendly message and let the user retry

This prevents hard failures and preserves trust.

## 6. High-Volume AI Request Handling

I would use an async, queue-based architecture.

### Performance

- API layer for request intake
- Redis/SQS/Kafka queue for generation jobs
- worker pools separated by task type:
  - text workers
  - image workers
  - video workers
- cache repeated prompts or common template generations where allowed

### Cost

- route simple tasks to cheaper models
- reserve premium models for high-value or high-complexity requests
- batch non-urgent embedding jobs
- autoscale GPU workers only when needed

### Reliability

- health checks per provider
- circuit breaker around unstable vendors
- request tracing and structured logs
- idempotent job processing
- quotas and rate limiting per tenant

Suggested stack:

- Python FastAPI/Flask API
- Redis queue or Celery workers
- Postgres for metadata
- S3 for assets
- vector DB for semantic search

## 7. Tools and Platforms

I have worked with:

- Python
- Flask
- OpenCV
- TensorFlow
- Scikit-learn
- Pandas
- MySQL
- Git/GitHub
- HTML/CSS
- JavaScript
- REST APIs
- Basic deployment workflows

## Submission Links

- Code / ZIP / GitHub: add your repository or ZIP link here
- Sample outputs: add `sample_outputs.json` or screenshots here
- Loom video: add your Loom link here

## Loom Video Structure

For the 3-5 minute Loom, I would explain:

1. The overall KeaBuilder AI architecture
2. Why I implemented the lead-processing workflow as the practical demo
3. How scoring, prompts, and fallback logic work
4. How the same design extends to content generation, LoRA, retrieval, and scale
