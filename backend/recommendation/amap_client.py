"""Small, dependency-free client for the Amap Web Service API.

Only this file knows Amap's response shape. Provider classes convert responses
into the application's normalized domain objects before the recommender sees them.
"""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class AmapRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class AmapClient:
    base_url: str
    api_key: str
    timeout_seconds: float = 8.0

    def request(self, path: str, **params: str) -> dict:
        query = urlencode({"key": self.api_key, "output": "JSON", **params})
        request = Request(f"{self.base_url.rstrip('/')}/{path.lstrip('/')}?{query}", method="GET")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise AmapRequestError(f"高德 API 请求失败：{exc}") from exc

        if payload.get("status") != "1" or payload.get("infocode") not in (None, "10000"):
            raise AmapRequestError(
                f"高德 API 返回错误：{payload.get('infocode', 'UNKNOWN')} {payload.get('info', '未知错误')}"
            )
        return payload

    def reverse_geocode(self, longitude: float, latitude: float) -> dict:
        payload = self.request("v3/geocode/regeo", location=f"{longitude},{latitude}")
        address = payload.get("regeocode", {}).get("addressComponent", {})
        adcode = address.get("adcode")
        if not adcode:
            raise AmapRequestError("高德逆地理编码未返回 adcode")
        return {
            "adcode": adcode,
            "province": address.get("province"),
            "city": address.get("city") or address.get("province"),
            "district": address.get("district"),
        }

    def forecast(self, adcode: str) -> dict:
        return self.request("v3/weather/weatherInfo", city=adcode, extensions="all")

    def driving_route(self, origin: str, destination: str) -> dict:
        return self.request("v3/direction/driving", origin=origin, destination=destination, strategy="0")

    def transit_route(self, origin: str, destination: str, city: str) -> dict:
        return self.request("v3/direction/transit/integrated", origin=origin, destination=destination, city=city)

    def nearby_pois(self, location: str, keywords: str) -> dict:
        return self.request(
            "v3/place/around",
            location=location,
            keywords=keywords,
            radius="3000",
            sortrule="distance",
            offset="10",
            page="1",
        )
