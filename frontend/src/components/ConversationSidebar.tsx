import {
  BookOpen,
  Clock,
  Loader2,
  LogOut,
  MessageSquare,
  MoreHorizontal,
  Plus,
  Search,
  Sparkles,
  Trash2,
  UserCircle2,
  X,
} from 'lucide-react'
import { useMemo, useState, type FormEvent } from 'react'
import { messageStorage } from '../services/messageStorage'
import type { ConversationResponse, UserResponse } from '../types'

interface ConversationSidebarProps {
  user: UserResponse
  conversations: ConversationResponse[]
  activeConversationId: string | null
  isLoadingConversations: boolean
  isCreatingConversation: boolean
  onSelectConversation: (conversationId: string) => void
  onCreateConversation: (title?: string) => Promise<void>
  onClearActiveConversationMessages: () => void
  onOpenProfile: () => void
  onOpenKnowledgeBase: () => void
  onLogout: () => void
  mobileOpen: boolean
  onCloseMobile: () => void
}

function formatRelativeDate(isoString: string): string {
  try {
    const date = new Date(isoString)
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}

function isToday(isoString: string): boolean {
  try {
    const d = new Date(isoString)
    const now = new Date()
    return (
      d.getDate() === now.getDate() &&
      d.getMonth() === now.getMonth() &&
      d.getFullYear() === now.getFullYear()
    )
  } catch {
    return false
  }
}

export function ConversationSidebar({
  user,
  conversations,
  activeConversationId,
  isLoadingConversations,
  isCreatingConversation,
  onSelectConversation,
  onCreateConversation,
  onClearActiveConversationMessages,
  onOpenProfile,
  onOpenKnowledgeBase,
  onLogout,
  mobileOpen,
  onCloseMobile,
}: ConversationSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showCustomTitleInput, setShowCustomTitleInput] = useState(false)
  const [customTitle, setCustomTitle] = useState('')

  const filteredConversations = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return conversations
    return conversations.filter(
      (c) => c.title.toLowerCase().includes(q) || c.id.toLowerCase().includes(q)
    )
  }, [conversations, searchQuery])

  const todayList = useMemo(
    () => filteredConversations.filter((c) => isToday(c.created_at)),
    [filteredConversations]
  )

  const earlierList = useMemo(
    () => filteredConversations.filter((c) => !isToday(c.created_at)),
    [filteredConversations]
  )

  const handleCustomCreate = async (e: FormEvent) => {
    e.preventDefault()
    const title = customTitle.trim() || 'Cuộc trò chuyện mới'
    setCustomTitle('')
    setShowCustomTitleInput(false)
    await onCreateConversation(title)
  }

  const sidebarContent = (
    <aside className="w-72 h-full bg-[#0e1016] border-r border-white/[0.07] flex flex-col select-none">
      {/* 1. Brand Header (Resolvo style) */}
      <div className="p-4 pb-3 border-b border-white/[0.06]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-600/25">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-white">Resolvo</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.06] border border-white/[0.08] text-slate-300">
                  v1.0-ai
                </span>
              </div>
              <p className="text-[11px] text-slate-400">AI-powered customer support</p>
            </div>
          </div>

          <button
            type="button"
            onClick={onCloseMobile}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Input */}
        <div className="mt-3.5 relative">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm kiếm hội thoại..."
            className="w-full pl-8 pr-7 py-2 rounded-lg bg-[#161922] border border-white/[0.07] text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500/60 transition"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* Primary "Ask Resolvo" / New Conversation Button */}
        <div className="mt-2.5 flex items-center gap-1.5">
          <button
            type="button"
            disabled={isCreatingConversation}
            onClick={() => void onCreateConversation('Cuộc trò chuyện mới')}
            className="flex-1 py-2.5 px-3.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white text-xs font-semibold flex items-center justify-between shadow-md shadow-blue-600/25 transition cursor-pointer"
          >
            <span className="flex items-center gap-2">
              {isCreatingConversation ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Plus className="w-3.5 h-3.5" />
              )}
              <span>Tạo hội thoại mới</span>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-700/70 text-blue-100">
              AI
            </span>
          </button>

          <button
            type="button"
            onClick={() => setShowCustomTitleInput((prev) => !prev)}
            title="Đặt tên cuộc hội thoại mới"
            className="p-2.5 rounded-lg bg-[#161922] hover:bg-[#1e2230] border border-white/[0.08] text-slate-300 transition cursor-pointer"
          >
            <MoreHorizontal className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Optional Custom Title Input */}
        {showCustomTitleInput && (
          <form onSubmit={handleCustomCreate} className="mt-2 flex items-center gap-1.5">
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="Nhập tiêu đề hội thoại..."
              maxLength={255}
              autoFocus
              className="flex-1 px-2.5 py-1.5 rounded-lg bg-[#161922] border border-blue-500/40 text-xs text-white placeholder:text-slate-500 focus:outline-none"
            />
            <button
              type="submit"
              className="px-2.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium cursor-pointer"
            >
              Tạo
            </button>
          </form>
        )}
      </div>

      {/* 2. Conversation List */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-5">
        {isLoadingConversations ? (
          <div className="py-10 flex flex-col items-center justify-center gap-2 text-slate-500 text-xs">
            <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
            <span>Đang tải danh sách hội thoại...</span>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="py-8 px-3 text-center rounded-xl bg-white/[0.02] border border-dashed border-white/[0.07]">
            <MessageSquare className="w-6 h-6 text-slate-500 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-300">
              {searchQuery ? 'Không tìm thấy hội thoại phù hợp' : 'Chưa có cuộc hội thoại nào'}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              Nhấn &ldquo;Tạo hội thoại mới&rdquo; hoặc gửi tin nhắn đầu tiên để bắt đầu.
            </p>
          </div>
        ) : (
          <>
            {todayList.length > 0 && (
              <div>
                <div className="px-2 mb-2 flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    Hôm nay
                  </span>
                  <span className="text-[10px] text-slate-600">{todayList.length}</span>
                </div>
                <div className="space-y-1">
                  {todayList.map((conv) => {
                    const active = conv.id === activeConversationId
                    const msgCount = messageStorage.getMessageCount(user.id, conv.id)
                    return (
                      <button
                        key={conv.id}
                        type="button"
                        onClick={() => {
                          onSelectConversation(conv.id)
                          onCloseMobile()
                        }}
                        className={`w-full text-left px-3 py-2.5 rounded-xl transition flex items-start gap-2.5 group cursor-pointer ${
                          active
                            ? 'bg-gradient-to-r from-blue-600/20 to-indigo-600/10 border border-blue-500/35 text-white shadow-sm'
                            : 'hover:bg-white/[0.04] border border-transparent text-slate-300'
                        }`}
                      >
                        <MessageSquare
                          className={`w-4 h-4 mt-0.5 shrink-0 ${
                            active ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-400'
                          }`}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium truncate">{conv.title}</div>
                          <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                            <span className="inline-flex items-center gap-1">
                              <Clock className="w-2.5 h-2.5" />
                              {formatRelativeDate(conv.created_at)}
                            </span>
                            {msgCount > 0 && (
                              <span className="px-1.5 py-0.2 rounded bg-white/[0.06] text-slate-300">
                                {msgCount} tin nhắn
                              </span>
                            )}
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {earlierList.length > 0 && (
              <div>
                <div className="px-2 mb-2 flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    Trước đó
                  </span>
                  <span className="text-[10px] text-slate-600">{earlierList.length}</span>
                </div>
                <div className="space-y-1">
                  {earlierList.map((conv) => {
                    const active = conv.id === activeConversationId
                    const msgCount = messageStorage.getMessageCount(user.id, conv.id)
                    return (
                      <button
                        key={conv.id}
                        type="button"
                        onClick={() => {
                          onSelectConversation(conv.id)
                          onCloseMobile()
                        }}
                        className={`w-full text-left px-3 py-2.5 rounded-xl transition flex items-start gap-2.5 group cursor-pointer ${
                          active
                            ? 'bg-gradient-to-r from-blue-600/20 to-indigo-600/10 border border-blue-500/35 text-white shadow-sm'
                            : 'hover:bg-white/[0.04] border border-transparent text-slate-300'
                        }`}
                      >
                        <MessageSquare
                          className={`w-4 h-4 mt-0.5 shrink-0 ${
                            active ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-400'
                          }`}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium truncate">{conv.title}</div>
                          <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                            <span>
                              {new Date(conv.created_at).toLocaleDateString('vi-VN', {
                                day: '2-digit',
                                month: '2-digit',
                              })}
                            </span>
                            {msgCount > 0 && (
                              <span className="px-1.5 py-0.2 rounded bg-white/[0.06] text-slate-300">
                                {msgCount} tin
                              </span>
                            )}
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* 3. Bottom Navigation & User Profile Footer (Resolvo style) */}
      <div className="p-3 border-t border-white/[0.07] space-y-1 bg-[#0b0d12]/60">
        <button
          type="button"
          onClick={onClearActiveConversationMessages}
          disabled={!activeConversationId}
          className="w-full px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] disabled:opacity-40 flex items-center gap-2.5 transition cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5 text-slate-500" />
          <span>Xóa lịch sử hiển thị</span>
        </button>

        <button
          type="button"
          onClick={onOpenKnowledgeBase}
          className="w-full px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] flex items-center gap-2.5 transition cursor-pointer"
        >
          <BookOpen className="w-3.5 h-3.5 text-slate-500" />
          <span>Tài liệu & Chính sách RAG</span>
        </button>

        <button
          type="button"
          onClick={onOpenProfile}
          className="w-full px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] flex items-center gap-2.5 transition cursor-pointer"
        >
          <UserCircle2 className="w-3.5 h-3.5 text-slate-500" />
          <span>Thông tin tài khoản (Profile)</span>
        </button>

        <button
          type="button"
          onClick={onLogout}
          className="w-full px-3 py-2 rounded-lg text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 flex items-center gap-2.5 transition cursor-pointer"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Đăng xuất (Logout)</span>
        </button>

        {/* User Card */}
        <div
          onClick={onOpenProfile}
          className="mt-2 pt-2.5 border-t border-white/[0.06] flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-white/[0.04] transition cursor-pointer"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {user.full_name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold text-white truncate">{user.full_name}</p>
            <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
          </div>
          <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-300 border border-emerald-500/25">
            {user.role}
          </span>
        </div>
      </div>
    </aside>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:block h-full shrink-0">{sidebarContent}</div>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-xs"
            onClick={onCloseMobile}
          />
          <div className="relative z-10 h-full">{sidebarContent}</div>
        </div>
      )}
    </>
  )
}
