import { defineEventHandler, createError } from 'h3'
import { getOrSetCache } from '../../../utils/cache'

export default defineEventHandler(async (event) => {
  const id = event.context.params?.id
  if (!id) throw createError({ statusCode: 400, statusMessage: 'Missing board id' })

  const boardData = await getOrSetCache(`board:${id}`, async () => {
    const res = await fetch(`https://your-api.com/board/${id}`)
    if (!res.ok) throw createError({ statusCode: res.status, statusMessage: 'Failed to fetch board data' })
    return await res.json()
  })

  return boardData
})