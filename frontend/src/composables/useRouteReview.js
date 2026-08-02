/**
 * 写评价 / 气质投票（S3 桌面详情 / M5 移动详情共用）
 * getRouteId: () => 当前路线 id；onSubmitted: 提交成功后回调（通常是重新加载详情）
 */
import { ref } from 'vue'
import { postRouteReview } from '../api/index'

export function useRouteReview(getRouteId, { onSubmitted, successText = '评价已提交' } = {}) {
  const reviewRating = ref(5)
  const reviewTags = ref([])
  const reviewContent = ref('')
  const reviewSubmitting = ref(false)
  const reviewMsg = ref('')

  const toggleTag = (tag) => {
    const i = reviewTags.value.indexOf(tag)
    i >= 0 ? reviewTags.value.splice(i, 1) : reviewTags.value.push(tag)
  }

  const submitReview = async () => {
    if (reviewSubmitting.value) return
    reviewSubmitting.value = true
    reviewMsg.value = ''
    try {
      await postRouteReview(getRouteId(), {
        rating: reviewRating.value,
        content: reviewContent.value.trim(),
        impressionTags: reviewTags.value
      })
      reviewContent.value = ''
      reviewTags.value = []
      reviewMsg.value = successText
      await onSubmitted?.()
    } catch (err) {
      reviewMsg.value = err.message || '提交失败，请稍后重试'
    } finally {
      reviewSubmitting.value = false
    }
  }

  return { reviewRating, reviewTags, reviewContent, reviewSubmitting, reviewMsg, toggleTag, submitReview }
}
