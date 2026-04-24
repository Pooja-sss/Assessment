# Question 6 - High-Volume AI Request Handling

## Question

KeaBuilder wants to handle a large number of users generating AI outputs. How would you design a system to handle high-volume AI requests?

Consider:

- Performance
- Cost
- Reliability

## Answer

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
