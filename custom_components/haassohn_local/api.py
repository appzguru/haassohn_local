"""Minimal client for the local HTTP API of the Haas+Sohn Wi-Fi module.

Protocol (same as the ioBroker/openHAB/Homey implementations):
- GET  http://<host>/status.cgi  -> full JSON status, no auth needed.
  The status contains meta.nonce, which changes after every accepted write.
- POST http://<host>/status.cgi  with a JSON body such as {"sp_temp": 19}
  and header X-HS-PIN = md5(nonce + md5(pin)). The response is the new
  full status (with a fresh nonce).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=10)


class HaasSohnError(Exception):
    """Communication error."""


class HaasSohnAuthError(HaasSohnError):
    """The stove rejected the PIN."""


def _md5(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()  # noqa: S324 - protocol requirement


class HaasSohnClient:
    """Talks to one stove."""

    def __init__(self, session: aiohttp.ClientSession, host: str, pin: str) -> None:
        self._session = session
        self._host = host
        self._hpin = _md5(str(pin))
        self._lock = asyncio.Lock()

    @property
    def url(self) -> str:
        return f"http://{self._host}/status.cgi"

    async def get_status(self) -> dict[str, Any]:
        try:
            async with self._session.get(self.url, timeout=TIMEOUT) as resp:
                resp.raise_for_status()
                data = json.loads(await resp.text())
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise HaasSohnError(f"Status ophalen mislukt: {err}") from err
        if "meta" not in data:
            raise HaasSohnError("Onverwacht antwoord van de kachel")
        return data

    async def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a write command. Returns the new status reported by the stove."""
        async with self._lock:
            # Always fetch a fresh nonce: the phone app also rotates it.
            status = await self.get_status()
            nonce = status["meta"]["nonce"]
            body = json.dumps(payload, separators=(",", ":"))
            headers = {
                "Content-Type": "application/json",
                "X-HS-PIN": _md5(nonce + self._hpin),
                "X-BACKEND-IP": "https://app.haassohn.com",
                "token": "32bytes",
                "User-Agent": "ios",
            }
            try:
                async with self._session.post(
                    self.url, data=body, headers=headers, timeout=TIMEOUT
                ) as resp:
                    text = await resp.text()
                    if resp.status in (401, 403):
                        raise HaasSohnAuthError("PIN geweigerd door de kachel")
                    resp.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                raise HaasSohnError(f"Opdracht versturen mislukt: {err}") from err
            try:
                new_status = json.loads(text)
            except ValueError as err:
                raise HaasSohnAuthError(
                    "Kachel gaf geen geldige status terug (PIN fout?)"
                ) from err
            if "meta" not in new_status:
                raise HaasSohnAuthError("Kachel gaf geen status terug (PIN fout?)")
            return new_status


def number(value: float) -> int | float:
    """Send 19 instead of 19.0, like the official app does."""
    return int(value) if float(value).is_integer() else float(value)
