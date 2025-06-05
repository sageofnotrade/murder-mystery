// utils/cache.ts
import client from '../services/redisClient'

export async function getOrSetCache<T>(key: string, fetchFn: () => Promise<T>, ttl = 3600): Promise<T> {
  const cached = await client.get(key)
  if (cached) return JSON.parse(cached)

  const fresh = await fetchFn()
  await client.set(key, JSON.stringify(fresh), { EX: ttl }) // expire after 1 hour
  return fresh
}