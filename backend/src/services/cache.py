import time
import hashlib


class SimpleCache:
    def __init__(self, ttl=1800):
        self._cache = {}
        self._cache_timestamps = {}
        self.ttl = ttl

    def _generate_key(self, *args, **kwargs):
        key_data = str(args) + str(kwargs)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key):
        if key in self._cache and (time.time() - self._cache_timestamps[key] < self.ttl):
            return self._cache[key]
        return None

    def set(self, key, value):
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()

    def clear(self):
        self._cache.clear()
        self._cache_timestamps.clear()

    def get_stats(self):
        """Get cache statistics"""
        current_time = time.time()
        valid_entries = sum(1 for ts in self._cache_timestamps.values()
                            if current_time - ts < self.ttl)
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "cache_size_mb": sum(len(str(v)) for v in self._cache.values()) / (1024 * 1024)
        }
