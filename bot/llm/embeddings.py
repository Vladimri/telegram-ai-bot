import httpx


class EmbeddingClient:
    def __init__(
        self, base_url: str, model: str, http_client: httpx.AsyncClient | None = None
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._http = http_client or httpx.AsyncClient(timeout=60.0)

    async def embed(self, text: str) -> list[float]:
        response = await self._http.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._model, "prompt": text},
        )
        response.raise_for_status()
        return list(response.json()["embedding"])
