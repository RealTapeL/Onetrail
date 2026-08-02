/**
 * 评分面板数据（S3 桌面详情 / M5 移动详情共用）
 * 从评价列表计算平均分、星级与 5~1 星分布，纯展示计算，不涉及接口。
 */
export function buildRatingPanel(reviews) {
  if (!reviews?.length) return null
  const total = reviews.length
  const avg = reviews.reduce((sum, r) => sum + r.rating, 0) / total
  return {
    avg: avg.toFixed(1),
    fullStars: Math.round(avg),
    total,
    dist: [5, 4, 3, 2, 1].map((star) => {
      const count = reviews.filter((r) => r.rating === star).length
      return { star, count, percent: Math.round((count / total) * 100) }
    })
  }
}
