import httpx


class ChatClient:
    def __init__(
        self, base_url: str, model: str, http_client: httpx.AsyncClient | None = None
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._http = http_client or httpx.AsyncClient(timeout=60.0)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        response = await self._http.post(
            f"{self._base_url}/api/chat",
            json={"model": self._model, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        return str(response.json()["message"]["content"])
