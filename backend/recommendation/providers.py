"""Normalized provider interfaces and the Amap implementation."""

import re
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from core.config import get_settings
from recommendation.amap_client import AmapClient, AmapRequestError


class ProviderNotConfigured(RuntimeError):
    pass


class ProviderRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class WeatherSnapshot:
    source_name: str
    safe_for_hiking: bool
    caution_notes: tuple[str, ...]
    mud_risk: str
    mud_risk_basis: str
    weather: str
    temperature_min_c: float | None
    temperature_max_c: float | None
    wind_power: str | None


@dataclass(frozen=True)
class MapContext:
    source_name: str
    adcode: str
    region_name: str
    city: str


@dataclass(frozen=True)
class TransportOption:
    mode: str
    distance_km: float | None
    duration_min: int | None
    summary: str
    steps: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupplyPoint:
    name: str
    category: str
    address: str | None
    distance_m: float | None
    location: str | None


@dataclass(frozen=True)
class HikingSpot:
    """高德 POI 发现的周边徒步地（非路线库路线，不含距离/爬升等路线参数）。"""

    name: str
    category: str
    address: str | None
    distance_m: float | None
    location: str | None


@dataclass(frozen=True)
class CityLocation:
    latitude: float
    longitude: float
    formatted_address: str


class WeatherProvider(Protocol):
    def get_forecast(self, adcode: str, travel_date: date) -> WeatherSnapshot: ...


class MapProvider(Protocol):
    def get_context(self, latitude: float, longitude: float, travel_date: date) -> MapContext: ...

    def get_transport_options(
        self, origin_latitude: float, origin_longitude: float, destination_latitude: float, destination_longitude: float, city: str
    ) -> list[TransportOption]: ...

    def get_supply_points(self, latitude: float, longitude: float) -> list[SupplyPoint]: ...

    def get_hiking_spots(self, latitude: float, longitude: float, city: str) -> list[HikingSpot]: ...

    def geocode_city(self, city: str) -> CityLocation: ...


class UnconfiguredWeatherProvider:
    def get_forecast(self, adcode: str, travel_date: date) -> WeatherSnapshot:
        raise ProviderNotConfigured("高德天气服务尚未配置 AMAP_API_KEY")


class UnconfiguredMapProvider:
    def get_context(self, latitude: float, longitude: float, travel_date: date) -> MapContext:
        raise ProviderNotConfigured("高德地图服务尚未配置 AMAP_API_KEY")

    def get_transport_options(self, *args) -> list[TransportOption]:
        raise ProviderNotConfigured("高德地图服务尚未配置 AMAP_API_KEY")

    def get_supply_points(self, *args) -> list[SupplyPoint]:
        raise ProviderNotConfigured("高德地图服务尚未配置 AMAP_API_KEY")

    def get_hiking_spots(self, *args) -> list[HikingSpot]:
        raise ProviderNotConfigured("高德地图服务尚未配置 AMAP_API_KEY")

    def geocode_city(self, *args) -> CityLocation:
        raise ProviderNotConfigured("高德地图服务尚未配置 AMAP_API_KEY")


class AmapMapProvider:
    def __init__(self, client: AmapClient):
        self.client = client

    def get_context(self, latitude: float, longitude: float, travel_date: date) -> MapContext:
        try:
            area = self.client.reverse_geocode(longitude, latitude)
        except AmapRequestError as exc:
            raise ProviderRequestError(str(exc)) from exc
        region = " ".join(part for part in (area.get("province"), area.get("city"), area.get("district")) if part)
        return MapContext(source_name="高德地图", adcode=area["adcode"], region_name=region, city=area.get("city") or area["adcode"])

    def get_transport_options(
        self, origin_latitude: float, origin_longitude: float, destination_latitude: float, destination_longitude: float, city: str
    ) -> list[TransportOption]:
        origin = f"{origin_longitude},{origin_latitude}"
        destination = f"{destination_longitude},{destination_latitude}"
        try:
            driving = self.client.driving_route(origin, destination)
            transit = self.client.transit_route(origin, destination, city)
        except AmapRequestError as exc:
            raise ProviderRequestError(str(exc)) from exc
        options: list[TransportOption] = []
        driving_path = (driving.get("route", {}).get("paths") or [{}])[0]
        options.append(_transport("驾车", driving_path, steps=_driving_steps(driving_path)))
        transit_path = (transit.get("route", {}).get("transits") or [{}])[0]
        options.append(_transport("公交/地铁", transit_path, steps=_transit_steps(transit_path)))
        return [option for option in options if option.distance_km is not None or option.duration_min is not None]

    def get_supply_points(self, latitude: float, longitude: float) -> list[SupplyPoint]:
        try:
            payload = self.client.nearby_pois(f"{longitude},{latitude}", "便利店|超市|停车场|公共厕所|游客中心")
        except AmapRequestError as exc:
            raise ProviderRequestError(str(exc)) from exc
        return [
            SupplyPoint(
                name=poi.get("name", ""),
                category=_text(poi.get("type")) or "补给/服务点",
                address=_text(poi.get("address")),
                distance_m=_number(poi.get("distance")),
                location=_text(poi.get("location")),
            )
            for poi in payload.get("pois", [])
            if poi.get("name")
        ]

    def get_hiking_spots(self, latitude: float, longitude: float, city: str) -> list[HikingSpot]:
        try:
            payload = self.client.hiking_spots(city)
        except AmapRequestError as exc:
            raise ProviderRequestError(str(exc)) from exc
        spots = [
            HikingSpot(
                name=poi.get("name", ""),
                category=poi.get("type", "徒步地"),
                address=poi.get("address") if isinstance(poi.get("address"), str) else None,
                # 文本搜索不返回距离，由推荐服务用起点坐标自行计算
                distance_m=None,
                location=poi.get("location"),
            )
            for poi in payload.get("pois", [])
            if poi.get("name")
        ]
        return [spot for spot in spots if _is_hiking_relevant(spot.name)]

    def geocode_city(self, city: str) -> CityLocation:
        try:
            result = self.client.geocode(city)
        except AmapRequestError as exc:
            raise ProviderRequestError(str(exc)) from exc
        return CityLocation(
            latitude=result["latitude"],
            longitude=result["longitude"],
            formatted_address=result["formatted_address"],
        )


# 名称中含这些词才视为徒步相关；含 "-" 的多为景点内部的子点位，排除
_HIKING_NAME_KEYWORDS = ("森林", "郊野", "湿地", "山", "峰", "湖", "峡谷", "古道", "登山", "徒步", "风景")


def _is_hiking_relevant(name: str) -> bool:
    return "-" not in name and any(keyword in name for keyword in _HIKING_NAME_KEYWORDS)


class AmapWeatherProvider:
    def __init__(self, client: AmapClient):
        self.client = client

    def get_forecast(self, adcode: str, travel_date: date) -> WeatherSnapshot:
        try:
            payload = self.client.forecast(adcode)
        except AmapRequestError as exc:
            raise ProviderRequestError(str(exc)) from exc

        forecast = payload.get("forecasts", [{}])[0]
        cast = next((item for item in forecast.get("casts", []) if item.get("date") == travel_date.isoformat()), None)
        if cast is None:
            raise ProviderRequestError("高德天气未返回目标日期的预报，请将日期调整到可预报范围内")

        weather = f"{cast.get('dayweather', '')}/{cast.get('nightweather', '')}".strip("/")
        caution_notes = _caution_notes(weather, cast.get("daypower"), cast.get("nightpower"))
        rain_expected = any(word in weather for word in ("雨", "雪", "暴", "雷"))
        safe = not any(word in weather for word in ("暴雨", "大暴雨", "特大暴雨", "暴雪", "台风", "雷暴"))
        return WeatherSnapshot(
            source_name="高德天气",
            safe_for_hiking=safe,
            caution_notes=tuple(caution_notes),
            mud_risk="high" if rain_expected else "unknown",
            mud_risk_basis=(
                "根据高德目标日期预报中的雨/雪/雷天气推断；未接入降雨量、土壤和现场传感器数据"
                if rain_expected
                else "高德天气未返回降雨信号；没有土壤和现场传感器数据，无法确认实际路面状态"
            ),
            weather=weather,
            temperature_min_c=_number(cast.get("nighttemp")),
            temperature_max_c=_number(cast.get("daytemp")),
            wind_power=cast.get("daypower") or cast.get("nightpower"),
        )


def _text(value) -> str | None:
    """高德空字段会返回空数组 [] 而非空字符串，统一归一为 None。"""
    return value if isinstance(value, str) and value else None


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None


def _transport(mode: str, path: dict, steps: list[str] | None = None) -> TransportOption:
    distance = _number(path.get("distance"))
    duration = _number(path.get("duration"))
    duration_min = round(duration / 60) if duration is not None else None
    return TransportOption(
        mode=mode,
        distance_km=round(distance / 1000, 2) if distance is not None else None,
        duration_min=duration_min,
        summary=f"高德{mode}方案" + (f"，约 {duration_min} 分钟" if duration_min is not None else ""),
        steps=tuple(steps or []),
    )


def _transit_steps(transit: dict) -> list[str]:
    """高德公交方案 segments → 可读换乘步骤（步行 + 公交/地铁线路、上下车站）。"""
    steps: list[str] = []
    for segment in transit.get("segments") or []:
        walking = segment.get("walking") or {}
        walk_m = _number(walking.get("distance"))
        if walk_m and walk_m >= 50:
            steps.append(f"步行 {round(walk_m)}M")
        for line in ((segment.get("bus") or {}).get("buslines") or [])[:1]:
            name = (line.get("name") or "").split("(")[0] or "公交"
            dep = (line.get("departure_stop") or {}).get("name")
            arr = (line.get("arrival_stop") or {}).get("name")
            via = _number(line.get("via_num"))
            stop_text = f"{dep} → {arr}" if dep and arr else ""
            via_text = f"，{int(via)} 站" if via else ""
            steps.append(f"乘 {name}{f'（{stop_text}{via_text}）' if stop_text else ''}")
    return steps[:8]


def _driving_steps(path: dict) -> list[str]:
    """高德驾车方案前几条真实导航指令。"""
    instructions = [
        step.get("instruction")
        for step in (path.get("steps") or [])
        if step.get("instruction")
    ]
    return instructions[:3]


def _caution_notes(weather: str, day_power: str | None, night_power: str | None) -> list[str]:
    notes: list[str] = []
    if any(word in weather for word in ("雨", "雪", "雷")):
        notes.append(f"预报天气：{weather}，请关注湿滑和能见度")
    wind = day_power or night_power
    if _number(wind) is not None and _number(wind) >= 5:
        notes.append(f"预报风力：{wind}级，注意山脊和开阔地带")
    return notes


def _client() -> AmapClient | None:
    settings = get_settings()
    if not settings.amap_api_key:
        return None
    return AmapClient(settings.amap_api_base_url, settings.amap_api_key)


def get_weather_provider() -> WeatherProvider:
    client = _client()
    return AmapWeatherProvider(client) if client else UnconfiguredWeatherProvider()


def get_map_provider() -> MapProvider:
    client = _client()
    return AmapMapProvider(client) if client else UnconfiguredMapProvider()


def integration_status() -> tuple[bool, bool]:
    configured = _client() is not None
    return configured, configured
