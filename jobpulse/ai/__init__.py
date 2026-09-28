"""AI service foundation for future job enrichment and embeddings."""

from .client import AIClient
from .enrichment import (
	EnrichmentGenerationError,
	EnrichmentResult,
	enrich_job,
	generate_and_save_job_enrichment,
)
from .embeddings import (
	EmbeddingGenerationError,
	build_job_embedding_text,
	create_embedding,
	generate_and_save_job_embedding,
)
from .search import semantic_search

__all__ = [
	"AIClient",
	"EmbeddingGenerationError",
	"EnrichmentGenerationError",
	"EnrichmentResult",
	"build_job_embedding_text",
	"create_embedding",
	"enrich_job",
	"generate_and_save_job_enrichment",
	"generate_and_save_job_embedding",
	"semantic_search",
]
