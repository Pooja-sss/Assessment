# Question 5 - Fallback Strategy for Multi-AI Services

## Question

In KeaBuilder, if we use multiple AI services:

- What fallback would you implement if one model fails?
- What fallback would you implement if an API times out?
- How would the platform handle this without breaking user experience?

## Answer

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
