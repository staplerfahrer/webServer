import json
from typing import Any


cached = False
config_cache: dict[str, Any] = {}


def config(name: str) -> Any:
	global cached, config_cache

	if not cached:
		with open('config.json', 'r') as f:
			config_cache = json.load(f)
		cached = True

	return config_cache[name]
