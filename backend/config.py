"""LLM configuration management -- persists to a local JSON file."""
import json
import os
from pydantic import BaseModel

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "llm_config.json")


class LLMConfig(BaseModel):
    provider: str = "deepseek"
    api_key: str = ""
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4096


_DEFAULTS = {
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "qwen": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo"},
    "zhipu": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4-flash"},
    "custom": {"base_url": "", "model": ""},
}


def load_config() -> LLMConfig:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return LLMConfig(**json.load(f))
    return LLMConfig()


def save_config(cfg: LLMConfig) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg.model_dump(), f, ensure_ascii=False, indent=2)


def resolve_config(cfg: LLMConfig) -> dict:
    d = _DEFAULTS.get(cfg.provider, _DEFAULTS["custom"])
    return {
        "api_key": cfg.api_key,
        "base_url": cfg.base_url or d["base_url"],
        "model": cfg.model or d["model"],
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
    }
