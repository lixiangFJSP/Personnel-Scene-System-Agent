"""LLM service -- sends requests to the configured domestic LLM provider."""
import json
import httpx
from config import resolve_config, load_config
from services.analysis_prompts import build_analysis_prompt


async def analyze_data(module: str, data) -> dict:
    cfg = load_config()
    resolved = resolve_config(cfg)

    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    if len(data_json) > 20000:
        data_json = data_json[:20000]

    prompt = build_analysis_prompt(module, data_json)

    headers = {
        "Authorization": f"Bearer {resolved['api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": resolved["model"],
        "messages": [
            {"role": "system", "content": "你是一个专业的制造业数据分析助手。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": resolved["temperature"],
        "max_tokens": resolved["max_tokens"],
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{resolved['base_url']}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "analysis": content}
    except httpx.HTTPStatusError as e:
        detail = e.response.text
        return {"success": False, "error": f"LLM request failed: {detail}"}
    except Exception as e:
        return {"success": False, "error": f"Request error: {str(e)}"}


async def test_connection() -> dict:
    cfg = load_config()
    resolved = resolve_config(cfg)

    headers = {
        "Authorization": f"Bearer {resolved['api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": resolved["model"],
        "messages": [{"role": "user", "content": "回复：连接正常"}],
        "max_tokens": 20,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{resolved['base_url']}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            return {"success": True, "reply": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
