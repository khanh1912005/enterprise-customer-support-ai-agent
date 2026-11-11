import {
  AlertCircle,
  BookOpen,
  Bot,
  Headphones,
  Loader2,
  Menu,
  PackageSearch,
  PanelRightClose,
  PanelRightOpen,
  Plus,
  RotateCcw,
  Send,
  ShoppingBag,
  Sparkles,
  User as UserIcon,
  X,
} from 'lucide-react'
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
} from 'react'
import { ConversationSidebar } from '../components/ConversationSidebar'
import { FormattedMessage } from '../components/FormattedMessage'
import { KnowledgeBaseModal } from '../components/KnowledgeBaseModal'
import { ProfileModal } from '../components/ProfileModal'
import { RightInspectorPanel } from '../components/RightInspectorPanel'
import { useAuth } from '../context/AuthContext'
import {
  chatApi,
  conversationApi,
  extractErrorMessage,
  systemApi,
  ticketApi,
} from '../services/api'
import { messageStorage } from '../services/messageStorage'
import type {
  ChatMessage,
  ConversationResponse,
  TicketResponse,
} from '../types'

export function ChatDashboard() {
  const { user, logout } = useAuth()

  const [conversations, setConversations] = useState<ConversationResponse[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])

  const [isLoadingConversations, setIsLoadingConversations] = useState(true)
  const [isCreatingConversation, setIsCreatingConversation] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [chatError, setChatError] = useState<string | null>(null)

  const [inputMessage, setInputMessage] = useState('')
  const [tickets, setTickets] = useState<TicketResponse[]>([])
  const [isLoadingTickets, setIsLoadingTickets] = useState(false)
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null)

  // UI Drawers & Modals
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [rightPanelOpen, setRightPanelOpen] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth >= 1280 : true
  )
  const [profileModalOpen, setProfileModalOpen] = useState(false)
  const [kbModalOpen, setKbModalOpen] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  const activeConversation = conversations.find((c) => c.id === activeConversationId) || null

  // Tự động cuộn xuống tin nhắn mới nhất
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isSending, scrollToBottom])

  // Kiểm tra sức khỏe Backend (/health)
  useEffect(() => {
    let mounted = true
    systemApi
      .health()
      .then((res) => {
        if (mounted) setBackendHealthy(res.status === 'ok')
      })
      .catch(() => {
        if (mounted) setBackendHealthy(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  // Tải danh sách Ticket hỗ trợ của khách hàng (/support-ticket)
  const loadTickets = useCallback(async () => {
    if (!user) return
    setIsLoadingTickets(true)
    try {
      const list = await ticketApi.list()
      setTickets(list)
    } catch {
      // Không chặn giao diện nếu lỗi tải ticket
    } finally {
      setIsLoadingTickets(false)
    }
  }, [user])

  // Tải danh sách Conversation (/conversations)
  const loadConversations = useCallback(async () => {
    if (!user) return
    setIsLoadingConversations(true)
    try {
      const list = await conversationApi.list()
      setConversations(list)
      if (list.length > 0) {
        setActiveConversationId((prev) => prev ?? list[0].id)
      }
    } catch (err) {
      setChatError(extractErrorMessage(err))
    } finally {
      setIsLoadingConversations(false)
    }
  }, [user])

  useEffect(() => {
    void loadConversations()
    void loadTickets()
  }, [loadConversations, loadTickets])

  // Khi chuyển activeConversationId, nạp lịch sử tin nhắn đã lưu của cuộc hội thoại đó
  useEffect(() => {
    if (!user || !activeConversationId) {
      setMessages([])
      return
    }
    const stored = messageStorage.getMessages(user.id, activeConversationId)
    setMessages(stored)
    setChatError(null)
  }, [user, activeConversationId])

  // Tạo cuộc hội thoại mới (POST /conversations)
  const handleCreateConversation = async (customTitle?: string): Promise<ConversationResponse | null> => {
    if (!user) return null
    setIsCreatingConversation(true)
    setChatError(null)
    try {
      const title = (customTitle || 'Cuộc trò chuyện mới').trim().slice(0, 255)
      const created = await conversationApi.create({ title })
      setConversations((prev) => [created, ...prev])
      setActiveConversationId(created.id)
      setMessages([])
      return created
    } catch (err) {
      setChatError(extractErrorMessage(err))
      return null
    } finally {
      setIsCreatingConversation(false)
    }
  }

  // Gửi tin nhắn tới AI Agent (POST /chat)
  const sendMessageToAgent = async (rawText: string) => {
    if (!user) return
    const text = rawText.trim()
    if (!text || isSending) return

    if (text.length > 2000) {
      setChatError('Tin nhắn không được vượt quá 2000 ký tự.')
      return
    }

    setChatError(null)
    setInputMessage('')

    let targetConversationId = activeConversationId

    // Nếu chưa có cuộc hội thoại nào, tự động tạo mới với tiêu đề thông minh từ câu hỏi đầu tiên
    if (!targetConversationId) {
      const smartTitle = text.length > 52 ? `${text.slice(0, 52)}...` : text
      const created = await handleCreateConversation(smartTitle)
      if (!created) return
      targetConversationId = created.id
    }

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      conversation_id: targetConversationId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
      status: 'sent',
    }

    const currentHistory = messageStorage.getMessages(user.id, targetConversationId)
    const updatedWithUser = [...currentHistory, userMsg]
    setMessages(updatedWithUser)
    messageStorage.saveMessages(user.id, targetConversationId, updatedWithUser)

    setIsSending(true)
    try {
      const response = await chatApi.sendMessage({
        conversation_id: targetConversationId,
        message: text,
      })

      const assistantMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        conversation_id: targetConversationId,
        role: 'assistant',
        content: response.reply,
        created_at: new Date().toISOString(),
        status: 'sent',
      }

      const finalMessages = [...updatedWithUser, assistantMsg]
      setMessages(finalMessages)
      messageStorage.saveMessages(user.id, targetConversationId, finalMessages)

      // Làm mới danh sách Ticket phòng trường hợp AI Agent vừa gọi create_support_ticket
      void loadTickets()
    } catch (err) {
      const errText = extractErrorMessage(err)
      setChatError(errText)
    } finally {
      setIsSending(false)
    }
  }

  const handleFormSubmit = async (e: FormEvent) => {
    e.preventDefault()
    await sendMessageToAgent(inputMessage)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void sendMessageToAgent(inputMessage)
    }
  }

  const handleClearActiveMessages = () => {
    if (!user || !activeConversationId) return
    messageStorage.clearMessages(user.id, activeConversationId)
    setMessages([])
  }

  const handleQuickPrompt = (promptText: string, sendImmediately = true) => {
    if (sendImmediately) {
      void sendMessageToAgent(promptText)
    } else {
      setInputMessage(promptText)
      textareaRef.current?.focus()
    }
  }

  if (!user) return null

  // 4 Card tính năng chính ở màn hình chào mừng (giống thiết kế Resolvo trong ảnh mẫu)
  const featureCards = [
    {
      title: 'Tra cứu trạng thái đơn hàng',
      subtitle: 'Kiểm tra tiến độ giao hàng & đơn vị vận chuyển',
      badge: 'Order Tool',
      icon: PackageSearch,
      iconBg: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
      prompt: 'Kiểm tra giúp tôi trạng thái đơn hàng mã DH004',
    },
    {
      title: 'Tìm kiếm thông tin sản phẩm',
      subtitle: 'Xem giá bán, mã SKU, danh mục & tồn kho',
      badge: 'Product Tool',
      icon: ShoppingBag,
      iconBg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
      prompt: 'Cho tôi xem thông tin, giá bán và tình trạng còn hàng của iPhone 16 Pro',
    },
    {
      title: 'Hỏi chính sách đổi trả & RAG',
      subtitle: 'Trích xuất chính xác từ tài liệu doanh nghiệp',
      badge: 'ChromaDB RAG',
      icon: BookOpen,
      iconBg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      prompt: 'Chính sách đổi trả sản phẩm khi bị lỗi kỹ thuật như thế nào?',
    },
    {
      title: 'Gửi yêu cầu hỗ trợ / Khiếu nại',
      subtitle: 'Tạo Ticket tự động chuyển tới bộ phận CSKH',
      badge: 'Ticket Tool',
      icon: Headphones,
      iconBg: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
      prompt: 'Tôi muốn tạo yêu cầu hỗ trợ vì sản phẩm nhận được bị lỗi màn hình.',
    },
  ]

  // Các gợi ý câu hỏi tiếp nối (Conversation Memory chips) nằm ngay trên thanh nhập chat
  const memoryFollowUpChips = [
    'Đơn hàng mã DH004 hiện đang ở trạng thái nào?',
    'Còn thời hạn đổi trả cụ thể trong chính sách thì sao?',
    'Tìm sản phẩm thuộc danh mục điện thoại hoặc phụ kiện',
    'Tạo phiếu hỗ trợ cho vấn đề của tôi',
  ]

  return (
    <div className="h-screen w-screen overflow-hidden bg-[#0b0d12] text-slate-100 flex">
      {/* 1. LEFT CONVERSATION SIDEBAR */}
      <ConversationSidebar
        user={user}
        conversations={conversations}
        activeConversationId={activeConversationId}
        isLoadingConversations={isLoadingConversations}
        isCreatingConversation={isCreatingConversation}
        onSelectConversation={(id) => setActiveConversationId(id)}
        onCreateConversation={async (title) => {
          await handleCreateConversation(title)
        }}
        onClearActiveConversationMessages={handleClearActiveMessages}
        onOpenProfile={() => setProfileModalOpen(true)}
        onOpenKnowledgeBase={() => setKbModalOpen(true)}
        onLogout={logout}
        mobileOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* 2. CENTER AI CHAT WORKSPACE */}
      <main className="flex-1 h-full flex flex-col min-w-0 bg-[#11131a] relative">
        {/* Top Workspace Header */}
        <header className="h-14 px-4 sm:px-6 border-b border-white/[0.06] bg-[#0e1016]/80 backdrop-blur-md flex items-center justify-between gap-3 shrink-0 z-10">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => setMobileSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-semibold text-white truncate">
                  {activeConversation ? activeConversation.title : 'Trợ lý AI Hỗ trợ Khách hàng'}
                </h1>
                {activeConversation && (
                  <span
                    className="hidden sm:inline-block text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.05] border border-white/[0.08] text-slate-400"
                    title={`Conversation ID: ${activeConversation.id}`}
                  >
                    #{activeConversation.id.slice(0, 8)}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400 truncate">
                LangGraph Multi-Tool Agent • Ghi nhớ ngữ cảnh theo từng cuộc hội thoại
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {/* Live Backend Status */}
            <div
              className={`hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
                backendHealthy === true
                  ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/25'
                  : backendHealthy === false
                    ? 'bg-rose-500/10 text-rose-300 border-rose-500/25'
                    : 'bg-white/5 text-slate-400 border-white/10'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  backendHealthy === true
                    ? 'bg-emerald-400 animate-pulse'
                    : backendHealthy === false
                      ? 'bg-rose-400'
                      : 'bg-slate-400'
                }`}
              />
              <span>{backendHealthy === false ? 'FastAPI Offline' : 'FastAPI Connected'}</span>
            </div>

            <button
              type="button"
              onClick={() => void handleCreateConversation('Cuộc trò chuyện mới')}
              disabled={isCreatingConversation}
              className="px-3 py-1.5 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 text-xs font-medium text-slate-200 flex items-center gap-1.5 transition cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5 text-blue-400" />
              <span className="hidden sm:inline">Hội thoại mới</span>
            </button>

            <button
              type="button"
              onClick={() => setRightPanelOpen((prev) => !prev)}
              title={rightPanelOpen ? 'Ẩn bảng thông tin bên phải' : 'Hiện bảng Hồ sơ & Công cụ AI'}
              className="p-2 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.08] text-slate-300 hover:text-white transition cursor-pointer"
            >
              {rightPanelOpen ? (
                <PanelRightClose className="w-4 h-4" />
              ) : (
                <PanelRightOpen className="w-4 h-4" />
              )}
            </button>
          </div>
        </header>

        {/* Center Scrollable Area: Either Welcome Hero (Resolvo style) or Active Chat Stream */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
          {messages.length === 0 ? (
            /* RESOLVO-STYLE WELCOME HERO */
            <div className="max-w-3xl mx-auto min-h-full flex flex-col items-center justify-center py-6">
              {/* Glowing AI Emblem */}
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-b from-blue-500/25 to-indigo-600/20 border border-blue-400/30 shadow-[0_0_50px_-5px_rgba(59,130,246,0.45)] flex items-center justify-center mb-5">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-inner">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              </div>

              {/* Greeting */}
              <p className="text-xs sm:text-sm text-slate-400 mb-1">
                Xin chào, <span className="text-slate-200 font-semibold">{user.full_name}</span>
              </p>
              <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight text-center">
                Hôm nay tôi có thể giúp gì cho bạn?
              </h2>

              {/* Capability Pills (matching Resolvo pills below greeting) */}
              <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => setKbModalOpen(true)}
                  className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181c26] hover:bg-[#1f2432] border border-white/[0.08] text-xs text-slate-300 transition cursor-pointer"
                >
                  <BookOpen className="w-3.5 h-3.5 text-amber-400" />
                  <span>Xem tài liệu Knowledge Base</span>
                </button>

                <button
                  type="button"
                  onClick={() => setProfileModalOpen(true)}
                  className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181c26] hover:bg-[#1f2432] border border-white/[0.08] text-xs text-slate-300 transition cursor-pointer"
                >
                  <UserIcon className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Hồ sơ khách hàng #{user.id}</span>
                </button>

                <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181c26] border border-white/[0.08] text-xs text-slate-300">
                  <RotateCcw className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Bộ nhớ hội thoại thông minh</span>
                </span>
              </div>

              {/* 4 Feature Action Cards (matching the 4 cards in Resolvo screenshot) */}
              <div className="mt-8 w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
                {featureCards.map((card, index) => {
                  const Icon = card.icon
                  return (
                    <button
                      key={index}
                      type="button"
                      onClick={() => handleQuickPrompt(card.prompt, true)}
                      className="text-left p-4 rounded-2xl bg-[#161923] hover:bg-[#1c202d] border border-white/[0.07] hover:border-blue-500/40 transition-all duration-200 flex flex-col justify-between min-h-[148px] group shadow-md hover:shadow-blue-950/20 cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div className={`p-2.5 rounded-xl border ${card.iconBg}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <span className="text-[10px] font-mono text-slate-500 group-hover:text-slate-300 transition">
                          {card.badge}
                        </span>
                      </div>

                      <div className="mt-4">
                        <h3 className="text-xs font-bold text-slate-100 group-hover:text-white leading-snug">
                          {card.title}
                        </h3>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                          {card.subtitle}
                        </p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          ) : (
            /* ACTIVE CONVERSATION MESSAGE STREAM */
            <div className="max-w-3xl mx-auto space-y-5 pb-4">
              {messages.map((msg) => {
                const isUser = msg.role === 'user'
                return (
                  <div
                    key={msg.id}
                    className={`flex items-start gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    {!isUser && (
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md shadow-blue-600/20 mt-0.5">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}

                    <div
                      className={`max-w-[82%] sm:max-w-[75%] rounded-2xl px-4 py-3 ${
                        isUser
                          ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-xs shadow-lg shadow-blue-600/15'
                          : 'bg-[#171b26] border border-white/[0.08] text-slate-100 rounded-bl-xs shadow-md'
                      }`}
                    >
                      <FormattedMessage content={msg.content} role={msg.role} />

                      <div
                        className={`mt-2 flex items-center justify-end gap-2 text-[10px] ${
                          isUser ? 'text-blue-100/80' : 'text-slate-500'
                        }`}
                      >
                        <span>
                          {new Date(msg.created_at).toLocaleTimeString('vi-VN', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                    </div>

                    {isUser && (
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center text-xs font-bold text-white shrink-0 mt-0.5">
                        {user.full_name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                )
              })}

              {/* AI Thinking / Tool Calling Indicator */}
              {isSending && (
                <div className="flex items-start gap-3.5 justify-start">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md shadow-blue-600/20">
                    <Loader2 className="w-4 h-4 text-white animate-spin" />
                  </div>
                  <div className="rounded-2xl rounded-bl-xs bg-[#171b26] border border-white/[0.08] px-4 py-3 text-xs text-slate-300 flex items-center gap-2.5">
                    <span className="flex gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" />
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce [animation-delay:150ms]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:300ms]" />
                    </span>
                    <span>
                      AI Agent đang phân tích câu hỏi & gọi công cụ (Order / Product / RAG / Ticket)...
                    </span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Floating Chat Input Area (matching Resolvo bottom bar) */}
        <div className="px-4 sm:px-8 pb-5 pt-2 bg-gradient-to-t from-[#11131a] via-[#11131a] to-transparent shrink-0">
          <div className="max-w-3xl mx-auto space-y-2.5">
            {/* Error Banner if any */}
            {chatError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 text-xs flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{chatError}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setChatError(null)}
                  className="text-rose-300 hover:text-white"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Quick Prompt Suggestion Chips above Input Bar */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
              {memoryFollowUpChips.map((chip, idx) => (
                <button
                  key={idx}
                  type="button"
                  disabled={isSending}
                  onClick={() => handleQuickPrompt(chip, false)}
                  className="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#171b26] hover:bg-[#1f2535] border border-white/[0.08] text-[11px] text-slate-300 hover:text-white transition cursor-pointer"
                >
                  <span>{chip}</span>
                  <span className="text-slate-500">↗</span>
                </button>
              ))}
            </div>

            {/* Main Input Box */}
            <form
              onSubmit={handleFormSubmit}
              className="rounded-2xl bg-[#171a24] border border-white/[0.1] focus-within:border-blue-500/60 focus-within:ring-2 focus-within:ring-blue-500/15 shadow-xl px-3.5 py-2.5 flex items-end gap-2.5 transition"
            >
              <button
                type="button"
                onClick={() => setKbModalOpen(true)}
                title="Mở tài liệu chính sách RAG"
                className="p-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.1] text-slate-400 hover:text-amber-300 transition shrink-0 cursor-pointer"
              >
                <BookOpen className="w-4 h-4" />
              </button>

              <textarea
                ref={textareaRef}
                rows={1}
                maxLength={2000}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isSending}
                placeholder="Nhập câu hỏi của bạn (VD: Kiểm tra đơn hàng DH004, tìm sản phẩm iPhone 16 Pro, hỏi chính sách đổi trả...)"
                className="flex-1 max-h-36 bg-transparent text-sm text-white placeholder:text-slate-500 focus:outline-none resize-none py-1.5 leading-relaxed"
              />

              <div className="flex items-center gap-2 shrink-0">
                <span className="hidden sm:inline text-[10px] font-mono text-slate-500">
                  {inputMessage.length}/2000
                </span>

                <button
                  type="submit"
                  disabled={isSending || !inputMessage.trim()}
                  className="w-9 h-9 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white flex items-center justify-center shadow-md shadow-blue-600/30 transition cursor-pointer"
                  title="Gửi tin nhắn (Enter)"
                >
                  {isSending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </form>

            {/* Footer note */}
            <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
              <span>
                AI Agent sử dụng dữ liệu thực từ PostgreSQL & ChromaDB Knowledge Base.
              </span>
              <span className="hidden sm:inline">Nhấn Enter để gửi • Shift + Enter để xuống dòng</span>
            </div>
          </div>
        </div>
      </main>

      {/* 3. RIGHT INSPECTOR PANEL (Customer Profile, Support Tickets & AI Tools) */}
      {rightPanelOpen && (
        <>
          <div className="hidden xl:block h-full">
            <RightInspectorPanel
              user={user}
              tickets={tickets}
              isLoadingTickets={isLoadingTickets}
              onRefreshTickets={loadTickets}
              onQuickPrompt={(prompt) => handleQuickPrompt(prompt, false)}
              isOpen={rightPanelOpen}
              onClose={() => setRightPanelOpen(false)}
            />
          </div>

          <div className="fixed inset-0 z-40 xl:hidden flex justify-end">
            <div
              className="fixed inset-0 bg-black/60 backdrop-blur-xs"
              onClick={() => setRightPanelOpen(false)}
            />
            <div className="relative z-10 h-full">
              <RightInspectorPanel
                user={user}
                tickets={tickets}
                isLoadingTickets={isLoadingTickets}
                onRefreshTickets={loadTickets}
                onQuickPrompt={(prompt) => {
                  handleQuickPrompt(prompt, false)
                  setRightPanelOpen(false)
                }}
                isOpen={rightPanelOpen}
                onClose={() => setRightPanelOpen(false)}
              />
            </div>
          </div>
        </>
      )}

      {/* Modals */}
      <ProfileModal
        isOpen={profileModalOpen}
        onClose={() => setProfileModalOpen(false)}
        user={user}
        conversationCount={conversations.length}
        ticketCount={tickets.length}
        onLogout={logout}
      />

      <KnowledgeBaseModal
        isOpen={kbModalOpen}
        onClose={() => setKbModalOpen(false)}
        onAskQuestion={(q) => handleQuickPrompt(q, true)}
      />
    </div>
  )
}
