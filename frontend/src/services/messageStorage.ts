import type { ChatMessage } from '../types'

const STORAGE_PREFIX = 'enterprise_ai_chat_messages_v1'

function getStorageKey(userId: number, conversationId: string): string {
  return `${STORAGE_PREFIX}_${userId}_${conversationId}`
}

export const messageStorage = {
  getMessages(userId: number, conversationId: string): ChatMessage[] {
    try {
      const raw = localStorage.getItem(getStorageKey(userId, conversationId))
      if (!raw) return []
      const parsed = JSON.parse(raw)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
  },

  saveMessages(userId: number, conversationId: string, messages: ChatMessage[]): void {
    try {
      localStorage.setItem(getStorageKey(userId, conversationId), JSON.stringify(messages))
    } catch {
      // Ignore storage quota errors
    }
  },

  clearMessages(userId: number, conversationId: string): void {
    try {
      localStorage.removeItem(getStorageKey(userId, conversationId))
    } catch {
      // Ignore errors
    }
  },

  getMessageCount(userId: number, conversationId: string): number {
    return this.getMessages(userId, conversationId).length
  },
}
