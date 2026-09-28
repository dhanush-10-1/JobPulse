"""Provider client boundary for AI services."""

import config


class AIClient:
    """Configured Gemini client without performing work during import."""

    def __init__(
        self,
        api_key=None,
        model=None,
        embedding_model=None,
    ):
        self.api_key = api_key if api_key is not None else config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required to initialize the AI client"
            )

        from google import genai

        self.model = model or config.AI_MODEL
        self.embedding_model = (
            embedding_model or config.AI_EMBEDDING_MODEL or "gemini-embedding-001"
        )
        self.provider_client = genai.Client(api_key=self.api_key)
