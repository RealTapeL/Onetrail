/**
 * 完成徒步 · 打卡（S4 桌面执行 / M3 移动行程共用）
 * 读取当前选中路线的真实数据提交 /history，反哺推荐能力画像。
 */
import { ref } from 'vue'
import { postActivity, state } from '../api/index'

export function useCheckin() {
  const checkinRating = ref(5)
  const checkinSubmitting = ref(false)
  const checkinMsg = ref('')

  const checkin = async () => {
    const raw = state.planByRouteId[state.selectedRouteId]
    if (!raw || checkinSubmitting.value) return
    checkinSubmitting.value = true
    checkinMsg.value = ''
    try {
      await postActivity({
        routeId: state.selectedRouteId,
        distanceKm: raw.distance_km,
        elevationGainM: raw.elevation_gain_m,
        durationMin: raw.estimated_duration_min,
        rating: checkinRating.value
      })
      checkinMsg.value = '打卡成功，已计入能力画像'
    } catch (err) {
      checkinMsg.value = err.message || '打卡失败，请稍后重试'
    } finally {
      checkinSubmitting.value = false
    }
  }

  return { checkinRating, checkinSubmitting, checkinMsg, checkin }
}
