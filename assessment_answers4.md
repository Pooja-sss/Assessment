# Question 4 - Face or Text Similarity Search

## Question

KeaBuilder stores user assets such as images, text, and templates.
How would you implement a face or text similarity search system?

Example:

- Find similar images/templates
- Match similar user inputs

Explain:

- Storage
- Retrieval
- Matching logic

## Answer

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
