import json
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session

from equipment.models import Equipment
from hiking_history.service import CapabilityProfile, get_capability_profile
from identity.models import HikingPreference
from recommendation.providers import (
    MapProvider,
    ProviderNotConfigured,
    ProviderRequestError,
    WeatherProvider,
    WeatherSnapshot,
)
from recommendation.schemas import (
    EquipmentSuggestion,
    HikingSpot,
    RecommendedRoute,
    RecommendationRequest,
    RecommendationResponse,
    SupplyPoint,
    TransportOption,
    WeatherAssessment,
)
from route_content.models import HikingRoute, RouteTag

# 路线起点距目的地超过该值时，视为"路线库在目的地附近没有路线"
NEARBY_ROUTE_KM = 100.0


def _effective_limit(request_value: float | int | None, preference_value: float | int | None) -> float | int | None:
    return request_value if request_value is not None else preference_value


def recommend(
    db: Session,
    user_id: str,
    request: RecommendationRequest,
    weather_provider: WeatherProvider,
    map_provider: MapProvider,
) -> RecommendationResponse:
    map_context = map_provider.get_context(request.latitude, request.longitude, request.travel_date)
    weather = weather_provider.get_forecast(map_context.adcode, request.travel_date)
    preference = db.get(HikingPreference, user_id)
    capability = get_capability_profile(db, user_id)
    weather_response = WeatherAssessment(
        weather=weather.weather,
        temperature_min_c=weather.temperature_min_c,
        temperature_max_c=weather.temperature_max_c,
        wind_power=weather.wind_power,
        mud_risk=weather.mud_risk,
        mud_risk_basis=weather.mud_risk_basis,
        caution_notes=list(weather.caution_notes),
    )
    sources = [weather.source_name, map_context.source_name]

    if not weather.safe_for_hiking:
        return RecommendationResponse(
            travel_date=request.travel_date,
            region_name=map_context.region_name,
            data_sources=sources,
            weather=weather_response,
            capability_samples=capability.samples,
            routes=[],
            notice="实时天气条件不适合徒步。请查看天气服务提供的风险说明后调整日期。",
        )

    distance_limit = _effective_limit(request.max_distance_km, preference.max_distance_km if preference else None)
    elevation_limit = _effective_limit(request.max_elevation_gain_m, preference.max_elevation_gain_m if preference else None)
    duration_limit = request.max_duration_min if request.max_duration_min is not None else (
        preference.preferred_duration_min if preference else None
    )
    candidates = db.scalars(select(HikingRoute)).all()
    route_by_id = {route.id: route for route in candidates}
    tags_by_route = {
        route.id: list(db.scalars(select(RouteTag).where(RouteTag.route_id == route.id))) for route in candidates
    }

    results: list[RecommendedRoute] = []
    nearest_route_km: float | None = None
    for route in candidates:
        if distance_limit is not None and route.distance_km > distance_limit:
            continue
        if elevation_limit is not None and route.elevation_gain_m > elevation_limit:
            continue
        if duration_limit is not None and route.estimated_duration_min > duration_limit:
            continue
        proximity_km = _haversine_km(request.latitude, request.longitude, route.start_latitude, route.start_longitude)
        nearest_route_km = proximity_km if nearest_route_km is None else min(nearest_route_km, proximity_km)
        score, reasons = _score_route(
            route=route,
            preference=preference,
            capability=capability,
            weather=weather,
            tags=tags_by_route[route.id],
            origin_latitude=request.latitude,
            origin_longitude=request.longitude,
        )
        results.append(
            RecommendedRoute(
                route_id=route.id,
                title=route.title,
                region=route.region,
                distance_km=route.distance_km,
                elevation_gain_m=route.elevation_gain_m,
                estimated_duration_min=route.estimated_duration_min,
                difficulty=route.difficulty,
                scene_tags=[tag.name for tag in tags_by_route[route.id]],
                score=score,
                reasons=reasons + list(weather.caution_notes),
                risk_notes=_risk_notes(tags_by_route[route.id], weather),
            )
        )

    results.sort(key=lambda result: result.score, reverse=True)
    top_results = results[:5]
    alternates = results[5:]
    equipment = _equipment_suggestions(db, top_results, tags_by_route, request.budget_cny, set(request.owned_equipment_ids))
    for result in top_results:
        route = route_by_id[result.route_id]
        try:
            result.transport_options = [
                TransportOption(
                    mode=option.mode,
                    distance_km=option.distance_km,
                    duration_min=option.duration_min,
                    summary=option.summary,
                )
                for option in map_provider.get_transport_options(
                    request.latitude,
                    request.longitude,
                    route.start_latitude,
                    route.start_longitude,
                    map_context.city,
                )
            ]
            result.supply_points = [
                SupplyPoint(
                    name=point.name,
                    category=point.category,
                    address=point.address,
                    distance_m=point.distance_m,
                    location=point.location,
                )
                for point in map_provider.get_supply_points(route.start_latitude, route.start_longitude)
            ]
        except ProviderRequestError as exc:
            result.reasons.append(f"交通或补给点查询暂不可用：{exc}")
        result.equipment_suggestions = equipment.get(result.route_id, [])

    notice = None if results else "没有满足当前限制的已发布路线。可调整距离、爬升或耗时限制，或先补充路线内容。"

    # 目的地附近（100km 内）路线库没有路线时，用高德 POI 补充真实周边徒步地
    hiking_spots: list[HikingSpot] = []
    if nearest_route_km is None or nearest_route_km > NEARBY_ROUTE_KM:
        try:
            raw_spots = map_provider.get_hiking_spots(request.latitude, request.longitude, map_context.city)
        except (ProviderNotConfigured, ProviderRequestError):
            raw_spots = []
        hiking_spots = [
            HikingSpot(
                name=spot.name,
                category=spot.category,
                address=spot.address,
                distance_m=_spot_distance_m(request.latitude, request.longitude, spot.location),
                location=spot.location,
            )
            for spot in raw_spots[:8]
        ]
        if hiking_spots:
            notice = _append_notice(
                notice, "路线库暂无目的地附近的路线，以下周边徒步地来自高德地图（仅含位置信息，无路线参数）。"
            )

    if not capability.samples:
        notice = _append_notice(notice, "暂无历史徒步记录，本次使用静态偏好和路线数据进行匹配。")
    if request.group_size > 1:
        notice = _append_notice(notice, "多人同行，请按队伍中经验最少的成员评估难度与节奏。")

    return RecommendationResponse(
        travel_date=request.travel_date,
        region_name=map_context.region_name,
        data_sources=sources,
        weather=weather_response,
        capability_samples=capability.samples,
        routes=top_results,
        alternates=alternates,
        hiking_spots=hiking_spots,
        notice=notice,
    )


def _score_route(
    route: HikingRoute,
    preference: HikingPreference | None,
    capability: CapabilityProfile,
    weather,
    tags: list[RouteTag],
    origin_latitude: float,
    origin_longitude: float,
) -> tuple[float, list[str]]:
    """Return a weighted score and human-readable evidence for every material factor."""

    components: list[tuple[str, float, float]] = []
    reasons: list[str] = []
    terrain_names = {tag.name for tag in tags if tag.category in {"terrain", "safety"}}
    interest_names = {interest.strip() for interest in json.loads(preference.interests or "[]")} if preference else set()

    distance_reference = preference.max_distance_km if preference and preference.max_distance_km else capability.typical_distance_km
    if distance_reference:
        fit = _capacity_fit(route.distance_km, distance_reference, 1.25)
        components.append(("距离", fit, 15))
        reasons.append(_fit_reason("距离", route.distance_km, "km", fit, f"参考上限/典型值 {distance_reference:g}km"))

    elevation_reference = preference.max_elevation_gain_m if preference and preference.max_elevation_gain_m is not None else capability.typical_elevation_gain_m
    if elevation_reference is not None:
        fit = _capacity_fit(route.elevation_gain_m, elevation_reference, 1.25)
        components.append(("爬升", fit, 15))
        reasons.append(_fit_reason("爬升", route.elevation_gain_m, "m", fit, f"参考上限/典型值 {elevation_reference:g}m"))

    duration_reference = preference.preferred_duration_min if preference and preference.preferred_duration_min else capability.typical_duration_min
    if duration_reference:
        fit = _capacity_fit(route.estimated_duration_min, duration_reference, 1.35)
        components.append(("耗时", fit, 15))
        reasons.append(_fit_reason("预计耗时", route.estimated_duration_min, "分钟", fit, f"参考时长 {duration_reference:g}分钟"))

    if preference and preference.difficulty_preference:
        difficulty_fit = _difficulty_fit(route.difficulty, preference.difficulty_preference)
        components.append(("难度", difficulty_fit, 15))
        reasons.append(
            "难度符合个人偏好" if difficulty_fit == 1 else f"路线难度为 {route.difficulty}，个人偏好为 {preference.difficulty_preference}"
        )

    temperature_fit, temperature_reason = _temperature_fit(weather.temperature_min_c, weather.temperature_max_c)
    components.append(("天气", temperature_fit, 20))
    reasons.append(temperature_reason)

    mud_fit = 1.0
    if weather.mud_risk == "high":
        mud_fit = 0.35 if terrain_names.intersection({"溪谷", "涉水", "碎石坡", "泥泞"}) else 0.6
        reasons.append("降雨预期较高，路面泥泞风险上升")
        if mud_fit < 0.5:
            reasons.append("路线地形标签与湿滑风险叠加")
    else:
        reasons.append("高德预报未返回降雨信号；实际泥泞状态仍需现场确认")
    components.append(("泥泞风险", mud_fit, 10))

    if interest_names:
        matched = interest_names.intersection({tag.name for tag in tags})
        interest_fit = len(matched) / len(interest_names)
        components.append(("兴趣", interest_fit, 10))
        reasons.append(f"匹配兴趣标签：{'、'.join(sorted(matched))}" if matched else "未匹配到用户兴趣标签")

    proximity_km = _haversine_km(origin_latitude, origin_longitude, route.start_latitude, route.start_longitude)
    proximity_fit = max(0.0, min(1.0, 1 - proximity_km / 300))
    components.append(("位置", proximity_fit, 10))
    reasons.append(f"路线起点直线距离约 {proximity_km:.1f}km")

    total_weight = sum(weight for _, _, weight in components)
    score = round(sum(value * weight for _, value, weight in components) / total_weight * 100, 1)
    if capability.samples:
        reasons.append(f"基于 {capability.samples} 条历史徒步记录建立能力参考")
    return max(0.0, min(100.0, score)), reasons


def _capacity_fit(value: float, reference: float, tolerance: float) -> float:
    if value <= reference:
        return 1.0
    return max(0.0, 1 - (value / reference - 1) / tolerance)


def _difficulty_fit(actual: str, preferred: str) -> float:
    order = {"easy": 0, "moderate": 1, "hard": 2, "expert": 3}
    difference = abs(order.get(actual, 1) - order.get(preferred, 1))
    return 1.0 if difference == 0 else 0.55 if difference == 1 else 0.2


def _temperature_fit(minimum: float | None, maximum: float | None) -> tuple[float, str]:
    if minimum is None or maximum is None:
        return 0.5, "天气服务未返回完整温度，无法判断舒适度"
    if minimum >= 10 and maximum <= 28:
        return 1.0, f"预报温度 {minimum:g}～{maximum:g}℃，处于较适宜范围"
    if minimum >= 5 and maximum <= 32:
        return 0.65, f"预报温度 {minimum:g}～{maximum:g}℃，基本适宜但需注意体感"
    return 0.25, f"预报温度 {minimum:g}～{maximum:g}℃，偏离常规舒适范围"


def _fit_reason(name: str, value: float, unit: str, fit: float, reference: str) -> str:
    if fit >= 0.8:
        return f"{name} {value:g}{unit}，符合{reference}"
    if fit >= 0.5:
        return f"{name} {value:g}{unit}，接近{reference}"
    return f"{name} {value:g}{unit}，明显高于{reference}"


def _risk_notes(tags: list[RouteTag], weather: WeatherSnapshot) -> list[str]:
    notes = [tag.safety_note for tag in tags if tag.category == "safety" and tag.safety_note]
    if weather.mud_risk == "high":
        notes.append("预报有降水，泥泞与湿滑风险升高，请谨慎评估涉水、碎石坡等路段。")
    return notes


def _haversine_km(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    earth_radius_km = 6371.0
    lat_delta = radians(latitude_b - latitude_a)
    lon_delta = radians(longitude_b - longitude_a)
    value = sin(lat_delta / 2) ** 2 + cos(radians(latitude_a)) * cos(radians(latitude_b)) * sin(lon_delta / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(value))


def _spot_distance_m(origin_latitude: float, origin_longitude: float, location: str | None) -> float | None:
    """高德 POI 的 location 为 "经度,纬度" 文本，计算与目的地的直线距离（米）。"""
    if not location or "," not in location:
        return None
    try:
        longitude, latitude = (float(part) for part in location.split(",", 1))
    except ValueError:
        return None
    return round(_haversine_km(origin_latitude, origin_longitude, latitude, longitude) * 1000, 1)


def _equipment_suggestions(
    db: Session,
    results: list[RecommendedRoute],
    tags_by_route: dict[str, list[RouteTag]],
    budget_cny: float | None,
    owned_equipment_ids: set[str],
) -> dict[str, list[EquipmentSuggestion]]:
    if not results:
        return {}
    items = db.scalars(select(Equipment).order_by(Equipment.created_at.desc())).all()
    suggestions: dict[str, list[EquipmentSuggestion]] = {}
    for result in results:
        route_tags = {tag.name for tag in tags_by_route[result.route_id]}
        allowed_categories = {"backpack", "footwear"}
        if route_tags.intersection({"露营", "过夜"}):
            allowed_categories.update({"tent", "sleeping_bag"})
        selected: list[EquipmentSuggestion] = []
        owned_matches = 0
        for item in items:
            if item.category not in allowed_categories:
                continue
            if budget_cny is not None and item.price_cny is not None and item.price_cny > budget_cny:
                continue
            if item.id in owned_equipment_ids:
                owned_matches += 1
                continue
            scenarios = set(json.loads(item.suitable_scenarios or "[]"))
            reason = "根据路线距离、爬升和难度提供参考"
            if scenarios.intersection(route_tags):
                reason = f"装备适用场景匹配路线标签：{'、'.join(sorted(scenarios.intersection(route_tags)))}"
            elif route_tags.intersection({"溪谷", "涉水", "碎石坡"}) and item.category == "footwear":
                reason = "路线包含复杂地形，请优先查看防滑与防护参数"
            selected.append(EquipmentSuggestion(equipment_id=item.id, name=item.name, category=item.category, reason=reason))
            if len(selected) >= 10:
                break
        if not selected and owned_matches:
            result.reasons.append("你已有该路线所需的推荐装备。")
        suggestions[result.route_id] = selected
    return suggestions


def _append_notice(current: str | None, addition: str) -> str:
    return f"{current} {addition}" if current else addition

