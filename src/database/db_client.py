'
import aiosqlite
import os
from contextlib import asynccontextmanager
from typing import Any, List, Tuple, Optional, Dict

class DatabaseClient:
    def __init__(self, db_path: str = "data/concierge.db"):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Initialize database connection and enable WAL mode."""
        self._connection = await aiosqlite.connect(self.db_path)
        # Enable WAL mode for better concurrency
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        await self._connection.commit()

    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    @asynccontextmanager
    async def cursor(self):
        """Provide a transactional cursor."""
        if not self._connection:
            await self.connect()
        async with self._connection.cursor() as cursor:
            yield cursor

    async def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute a query without returning results."""
        async with self.cursor() as cursor:
            await cursor.execute(query, params)
            await self._connection.commit()

    async def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute a query multiple times with different parameters."""
        async with self.cursor() as cursor:
            await cursor.executemany(query, params_list)
            await self._connection.commit()

    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """Fetch a single row."""
        async with self.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Fetch all rows."""
        async with self.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchall()

    async def fetch_all_dict(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        async with self.cursor() as cursor:
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in rows]

# Global instance
db = DatabaseClient()
'
