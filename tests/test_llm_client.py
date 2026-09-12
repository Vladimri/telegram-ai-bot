import httpx
import respx

from bot.llm.client import ChatClient


@respx.mock
async def test_chat_returns_message_content():
    respx.post("http://ollama.local/api/chat").mock(
        return_value=httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "Hello!"}},
        )
    )
    client = ChatClient(base_url="http://ollama.local", model="llama3.1:8b")

    result = await client.chat([{"role": "user", "content": "hi"}])

    assert result == "Hello!"
