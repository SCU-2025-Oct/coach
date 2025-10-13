import sys
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class JobsMCPClient:
    def __init__(self, server_script: str):
        self.server_script = server_script
        self._session: Optional[ClientSession] = None
        self._ctx = None  # holds the (read, write) context manager

    async def _ensure_session(self) -> ClientSession:
        if self._session is not None:
            return self._session
        params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script],
            env=None,
        )
        self._ctx = stdio_client(params)
        read, write = await self._ctx.__aenter__()
        session = ClientSession(read, write)
        await session.initialize()
        self._session = session
        return session

    async def search_jobs(self, query: str, location: str = "", limit: int = 10) -> Any:
        session = await self._ensure_session()
        args: Dict[str, Any] = {"q": query, "location": location, "limit": limit}
        result = await session.call_tool("search_jobs", arguments=args)
        if getattr(result, "structuredContent", None):
            return result.structuredContent
        # fallback: return raw
        return {"content": [getattr(b, "text", "") for b in (result.content or [])]}

    async def aclose(self):
        if self._session is not None:
            await self._session.close()
            self._session = None
        if self._ctx is not None:
            await self._ctx.__aexit__(None, None, None)
            self._ctx = None

jobs_client: Optional[JobsMCPClient] = None
