"""In-memory TTLCache wrappers replacing Redis key patterns."""

from cachetools import TTLCache

# Cache namespaces
CACHE_SPU_DETAIL = "spu_detail"
CACHE_USER_PROFILE = "user_profile"
CACHE_HOT_RANKING = "hot_ranking"
CACHE_COLLABORATIVE = "collaborative"

# Create caches
_caches: dict[str, TTLCache] = {}


def _get_cache(namespace: str, maxsize: int = 256, ttl: int = 3600) -> TTLCache:
    """Get or create a TTLCache for a namespace."""
    if namespace not in _caches:
        _caches[namespace] = TTLCache(maxsize=maxsize, ttl=ttl)
    return _caches[namespace]


def cache_get(namespace: str, key: str):
    """Get a value from cache."""
    cache = _get_cache(namespace)
    return cache.get(key)


def cache_set(namespace: str, key: str, value, ttl: int | None = None):
    """Set a value in cache with optional TTL override."""
    if ttl is not None:
        cache = TTLCache(maxsize=256, ttl=ttl)
        # Copy existing items
        existing = _get_cache(namespace)
        for k, v in existing.items():
            if k != key:
                cache[k] = v
        _caches[namespace] = cache
        cache[key] = value
    else:
        cache = _get_cache(namespace)
        cache[key] = value


def cache_delete(namespace: str, key: str):
    """Delete a value from cache."""
    cache = _get_cache(namespace)
    if key in cache:
        del cache[key]


def cache_clear(namespace: str):
    """Clear an entire cache namespace."""
    if namespace in _caches:
        del _caches[namespace]
