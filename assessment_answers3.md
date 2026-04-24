# Question 3 - Personalized AI Images with LoRA

## Question

KeaBuilder wants to allow users to generate personalised AI images, for example consistent faces or branding.

- How would you integrate a pre-trained LoRA model into the inference pipeline?
- How would this work when a user generates images inside KeaBuilder?

## Answer

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
