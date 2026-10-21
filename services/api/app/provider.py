"""Optional extraction adapter. Only allowlisted travel tokens leave this service."""

import json
import os
import re
import httpx
from httpx import Client as ProviderClient
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class Extracted(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=80)
    max_price: float | None = Field(default=None, gt=0, le=100000)
    min_seats: int | None = Field(default=None, ge=1, le=20)
    occasion: Literal["business", "family", "celebration", "leisure"] | None = None


SAFE_WORDS = set(
    "in for under below maximum budget daily per day days week trip seats passengers people adults family business celebration leisure luxury suv sports supercar electric convertible economy aed usd navigation bluetooth leather panoramic climate control automatic manual one two three four five six seven eight nine ten eleven twelve".split()
)


def travel_tokens(message, cities):
    # Never forward free text: names, contacts, credentials and unknown tokens are discarded.
    scrubbed = re.sub(
        r"\S+@\S+|https?://\S+|\b(?:password|token|secret|key|authorization)\s*[:=]?\s*\S+",
        " ",
        message.lower(),
    )
    scrubbed = re.sub(r"(?:\+?\d[\d ()-]{7,}\d)", " ", scrubbed)
    allowed = SAFE_WORDS | {word for city in cities for word in city.lower().split()}
    return " ".join(
        token
        for token in re.findall(r"[a-z]+|\d+(?:\.\d+)?", scrubbed)
        if token in allowed
        or (token.replace(".", "", 1).isdigit() and float(token) <= 100000)
    )[:1000]


def extract(message, cities, categories):
    key, model = os.getenv("AI_API_KEY"), os.getenv("AI_MODEL")
    if not key or not model:
        return None
    base = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    if not base.startswith("https://"):
        return None
    safe = travel_tokens(message, cities)
    try:
        with ProviderClient(timeout=8.0, follow_redirects=False) as client:
            response = client.post(
                base + "/chat/completions",
                headers={"Authorization": "Bearer " + key},
                json={
                    "model": model,
                    "temperature": 0,
                    "max_tokens": 250,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "system",
                            "content": "Extract travel constraints as JSON only. Keys city, category, max_price, min_seats, occasion. Omit unknown values. Never choose inventory. Cities: "
                            + json.dumps(cities)
                            + ". Categories: "
                            + json.dumps(categories),
                        },
                        {"role": "user", "content": safe},
                    ],
                },
            )
            response.raise_for_status()
            result = Extracted.model_validate_json(
                response.json()["choices"][0]["message"]["content"]
            )
        if (
            result.city
            and result.city not in cities
            or result.category
            and result.category not in categories
        ):
            return None
        return result
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        return None
