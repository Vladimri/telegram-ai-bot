import httpx
import respx

from bot.llm.embeddings import EmbeddingClient


@respx.mock
async def test_embed_returns_vector():
    respx.post("http://ollama.local/api/embeddings").mock(
        return_value=httpx.Response(200, json={"embedding": [0.1, 0.2, 0.3]})
    )
    client = EmbeddingClient(base_url="http://ollama.local", model="nomic-embed-text")

    result = await client.embed("BMW X5 2019")

    assert result == [0.1, 0.2, 0.3]
