from dataclasses import dataclass

import httpx

from app.config import settings


@dataclass
class GeoResult:
    country: str
    city: str
    provider: str


class GeoProviderUnavailable(Exception):
    pass


def provider_a(ip_address: str) -> GeoResult:
    if settings.geo_provider_a_mode == "fail":
        raise GeoProviderUnavailable("Provider A unavailable")
    if settings.geo_provider_a_mode == "real":
        try:
            response = httpx.get(
                f"http://ip-api.com/json/{ip_address}",
                params={"fields": "status,message,country,city"},
                timeout=3,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "success":
                raise GeoProviderUnavailable(data.get("message", "Provider A failed"))
            return GeoResult(country=data["country"], city=data["city"], provider="provider_a")
        except (httpx.HTTPError, KeyError, ValueError) as error:
            raise GeoProviderUnavailable("Provider A unavailable") from error
    return GeoResult(country="Testland", city="Alpha City", provider="provider_a")


def provider_b(ip_address: str) -> GeoResult:
    if settings.geo_provider_b_mode == "fail":
        raise GeoProviderUnavailable("Provider B unavailable")
    if settings.geo_provider_b_mode == "real":
        try:
            response = httpx.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)
            response.raise_for_status()
            data = response.json()
            if data.get("error"):
                raise GeoProviderUnavailable(data.get("reason", "Provider B failed"))
            return GeoResult(
                country=data["country_name"],
                city=data["city"],
                provider="provider_b",
            )
        except (httpx.HTTPError, KeyError, ValueError) as error:
            raise GeoProviderUnavailable("Provider B unavailable") from error
    return GeoResult(country="Fallbackland", city="Beta City", provider="provider_b")


def enrich_ip(ip_address: str) -> GeoResult | None:
    for provider in (provider_a, provider_b):
        try:
            return provider(ip_address)
        except GeoProviderUnavailable:
            continue
    return None
