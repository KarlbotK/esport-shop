import asyncio
from typing import Dict, Set


class SeckillManager:
    """Manages seckill stock and anti-repeat checking using in-memory locks."""

    def __init__(self):
        self._locks: Dict[int, asyncio.Lock] = {}
        self._stock: Dict[int, int] = {}
        self._users: Dict[int, Set[int]] = {}

    def get_lock(self, sku_id: int) -> asyncio.Lock:
        """Get or create an asyncio.Lock for a given SKU."""
        if sku_id not in self._locks:
            self._locks[sku_id] = asyncio.Lock()
        return self._locks[sku_id]

    def load_stock(self, sku_id: int, stock: int):
        """Preload stock for a seckill event."""
        self._stock[sku_id] = stock
        self._users[sku_id] = set()

    def get_stock(self, sku_id: int) -> int:
        return self._stock.get(sku_id, 0)

    def has_user(self, sku_id: int, user_id: int) -> bool:
        return user_id in self._users.get(sku_id, set())

    def add_user(self, sku_id: int, user_id: int):
        if sku_id not in self._users:
            self._users[sku_id] = set()
        self._users[sku_id].add(user_id)

    def decrement_stock(self, sku_id: int) -> bool:
        if sku_id in self._stock and self._stock[sku_id] > 0:
            self._stock[sku_id] -= 1
            return True
        return False


seckill_manager = SeckillManager()
