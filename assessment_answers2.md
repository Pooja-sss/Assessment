# Question 2 - Multi-Provider Content Generation

## Question

KeaBuilder allows users to generate different types of content. How would you design a system where:

- Images -> handled by one provider
- Videos -> another provider
- Voice -> another provider

Explain:

- Routing logic
- How frontend (builder UI) interacts with backend
- How outputs are managed inside the platform

## Answer

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
