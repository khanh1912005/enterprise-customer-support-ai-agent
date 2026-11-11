import {
  AlertTriangle,
  BookOpenCheck,
  BrainCircuit,
  CheckCircle2,
  Clock,
  Headphones,
  Loader2,
  PackageSearch,
  Plus,
  RefreshCw,
  ShoppingBag,
  Sparkles,
  Ticket as TicketIcon,
  Wrench,
  X,
} from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { extractErrorMessage, ticketApi } from '../services/api'
import type { TicketResponse, TicketStatus, UserResponse } from '../types'

interface RightInspectorPanelProps {
  user: UserResponse
  tickets: TicketResponse[]
  isLoadingTickets: boolean
  onRefreshTickets: () => Promise<void>
  onQuickPrompt: (prompt: string) => void
  isOpen: boolean
  onClose: () => void
}

function renderStatusBadge(status: TicketStatus) {
  switch (status) {
    case 'resolved':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
          <CheckCircle2 className="w-2.5 h-2.5" />
          Đã xử lý
        </span>
      )
    case 'in_progress':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-500/15 text-blue-300 border border-blue-500/30">
          <Clock className="w-2.5 h-2.5" />
          Đang xử lý
        </span>
      )
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
          <Clock className="w-2.5 h-2.5" />
          Chờ tiếp nhận
        </span>
      )
  }
}

export function RightInspectorPanel({
  user,
  tickets,
  isLoadingTickets,
  onRefreshTickets,
  onQuickPrompt,
  isOpen,
  onClose,
}: RightInspectorPanelProps) {
  const [activeTab, setActiveTab] = useState<'customer' | 'tools'>('customer')
  const [showCreateTicket, setShowCreateTicket] = useState(false)
  const [issueText, setIssueText] = useState('')
  const [creatingTicket, setCreatingTicket] = useState(false)
  const [ticketError, setTicketError] = useState<string | null>(null)
  const [ticketSuccess, setTicketSuccess] = useState<string | null>(null)

  if (!isOpen) return null

  const handleCreateTicket = async (e: FormEvent) => {
    e.preventDefault()
    setTicketError(null)
    setTicketSuccess(null)

    const cleanIssue = issueText.trim()
    if (cleanIssue.length < 5) {
      setTicketError('Nội dung vấn đề cần tối thiểu 5 ký tự.')
      return
    }

    setCreatingTicket(true)
    try {
      const created = await ticketApi.create({
        customer_name: user.full_name,
        email: user.email,
        issue: cleanIssue,
      })
      setIssueText('')
      setShowCreateTicket(false)
      setTicketSuccess(`Đã tạo Ticket #${created.id} thành công!`)
      await onRefreshTickets()
      setTimeout(() => setTicketSuccess(null), 3500)
    } catch (err) {
      setTicketError(extractErrorMessage(err))
    } finally {
      setCreatingTicket(false)
    }
  }

  const agentTools = [
    {
      id: 'get_order_status',
      name: 'Tra cứu đơn hàng (Order Tool)',
      badge: 'get_order_status',
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/25',
      description: 'Kiểm tra trạng thái giao hàng, đơn vị vận chuyển và ngày dự kiến giao theo mã đơn.',
      samplePrompt: 'Kiểm tra giúp tôi trạng thái đơn hàng mã DH004',
      icon: PackageSearch,
    },
    {
      id: 'get_product_info',
      name: 'Tìm kiếm sản phẩm (Product Tool)',
      badge: 'get_product_info',
      color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
      description: 'Tra cứu tên sản phẩm, mã SKU, danh mục, giá bán và tình trạng tồn kho.',
      samplePrompt: 'Cho tôi xem thông tin, giá bán và tình trạng còn hàng của iPhone 16 Pro',
      icon: ShoppingBag,
    },
    {
      id: 'search_knowledge_base',
      name: 'Tra cứu Chính sách RAG (ChromaDB)',
      badge: 'search_knowledge_base',
      color: 'text-amber-400 bg-amber-500/10 border-amber-500/25',
      description: 'Tìm kiếm chính sách đổi trả, điều kiện sản phẩm và quy trình hỗ trợ từ tài liệu.',
      samplePrompt: 'Chính sách đổi trả sản phẩm khi bị lỗi kỹ thuật quy định những điều kiện và bước xử lý nào?',
      icon: BookOpenCheck,
    },
    {
      id: 'create_support_ticket',
      name: 'Tạo Phiếu hỗ trợ (Ticket Tool)',
      badge: 'create_support_ticket',
      color: 'text-purple-400 bg-purple-500/10 border-purple-500/25',
      description: 'Tự động ghi nhận yêu cầu hỗ trợ / khiếu nại của khách hàng vào PostgreSQL.',
      samplePrompt: 'Tôi muốn tạo yêu cầu hỗ trợ: Sản phẩm tôi nhận được bị trầy xước màn hình và thiếu cáp sạc.',
      icon: Headphones,
    },
    {
      id: 'conversation_memory',
      name: 'Bộ nhớ Hội thoại (PostgresSaver)',
      badge: 'LangGraph Memory',
      color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/25',
      description: 'Lưu ngữ cảnh theo từng cuộc hội thoại để trả lời câu hỏi tiếp nối thông minh.',
      samplePrompt: 'Còn thời hạn đổi trả cụ thể trong trường hợp đó thì sao?',
      icon: BrainCircuit,
    },
  ]

  return (
    <aside className="w-80 h-full bg-[#0e1016] border-l border-white/[0.07] flex flex-col shrink-0">
      {/* Top Tabs Header (Tools / Customer Profile) */}
      <div className="p-3.5 border-b border-white/[0.06] flex items-center justify-between gap-2">
        <div className="flex-1 grid grid-cols-2 p-1 rounded-xl bg-[#151822] border border-white/[0.06]">
          <button
            type="button"
            onClick={() => setActiveTab('customer')}
            className={`py-1.5 px-2 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeTab === 'customer'
                ? 'bg-white text-slate-950 shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Hồ sơ & Ticket
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('tools')}
            className={`py-1.5 px-2 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeTab === 'tools'
                ? 'bg-white text-slate-950 shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Công cụ AI
          </button>
        </div>

        <button
          type="button"
          onClick={onClose}
          title="Đóng bảng thông tin"
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-4">
        {activeTab === 'customer' ? (
          <>
            {/* Customer Profile Card (inspired by top-right Dribbble reference) */}
            <div className="rounded-2xl bg-[#141720] border border-white/[0.07] overflow-hidden">
              <div className="h-16 bg-gradient-to-r from-indigo-600/30 via-blue-600/20 to-cyan-500/20 relative">
                <div className="absolute -bottom-6 left-4 w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-400 border-2 border-[#141720] flex items-center justify-center text-base font-bold text-white shadow-md">
                  {user.full_name.charAt(0).toUpperCase()}
                </div>
              </div>

              <div className="pt-8 px-4 pb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">{user.full_name}</h3>
                    <p className="text-xs text-slate-400">{user.email}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-[10px] font-semibold text-emerald-300 uppercase">
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="mt-3.5 pt-3 border-t border-white/[0.06] grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                    <span className="text-[10px] text-slate-500 block">Mã khách hàng</span>
                    <span className="font-mono font-semibold text-slate-200">USR-#{user.id}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                    <span className="text-[10px] text-slate-500 block">Vai trò hệ thống</span>
                    <span className="font-semibold text-indigo-300 capitalize">{user.role}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Support Tickets Section (/support-ticket) */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <TicketIcon className="w-3.5 h-3.5 text-indigo-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    Yêu cầu hỗ trợ ({tickets.length})
                  </h4>
                </div>

                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => void onRefreshTickets()}
                    title="Làm mới danh sách Ticket"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition cursor-pointer"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isLoadingTickets ? 'animate-spin' : ''}`} />
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateTicket((prev) => !prev)}
                    className="px-2 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-[11px] font-medium text-indigo-200 flex items-center gap-1 transition cursor-pointer"
                  >
                    <Plus className="w-3 h-3" />
                    <span>Gửi Ticket</span>
                  </button>
                </div>
              </div>

              {ticketSuccess && (
                <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs">
                  {ticketSuccess}
                </div>
              )}

              {showCreateTicket && (
                <form
                  onSubmit={handleCreateTicket}
                  className="p-3 rounded-xl bg-[#151822] border border-indigo-500/30 space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">Tạo phiếu hỗ trợ mới</span>
                    <button
                      type="button"
                      onClick={() => setShowCreateTicket(false)}
                      className="text-slate-500 hover:text-slate-300"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {ticketError && (
                    <p className="text-[11px] text-rose-300 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
                      {ticketError}
                    </p>
                  )}

                  <textarea
                    rows={3}
                    required
                    minLength={5}
                    maxLength={2000}
                    value={issueText}
                    onChange={(e) => setIssueText(e.target.value)}
                    placeholder="Mô tả chi tiết vấn đề cần hỗ trợ (tối thiểu 5 ký tự)..."
                    className="w-full p-2.5 rounded-lg bg-[#0e1016] border border-white/10 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                  />

                  <button
                    type="submit"
                    disabled={creatingTicket}
                    className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    {creatingTicket ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Đang gửi...</span>
                      </>
                    ) : (
                      <span>Gửi yêu cầu hỗ trợ</span>
                    )}
                  </button>
                </form>
              )}

              {/* Ticket List */}
              {isLoadingTickets ? (
                <div className="py-8 flex flex-col items-center justify-center gap-2 text-slate-500 text-xs">
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  <span>Đang tải danh sách Ticket...</span>
                </div>
              ) : tickets.length === 0 ? (
                <div className="p-4 rounded-xl bg-[#141720] border border-white/[0.06] text-center">
                  <p className="text-xs text-slate-300 font-medium">Chưa có yêu cầu hỗ trợ nào</p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Bạn có thể nhờ AI Agent tạo giúp trong khung chat hoặc nhấn &ldquo;Gửi Ticket&rdquo;.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {tickets.map((ticket) => (
                    <div
                      key={ticket.id}
                      className="p-3 rounded-xl bg-[#141720] border border-white/[0.07] hover:border-white/[0.14] transition space-y-1.5"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-mono font-bold text-indigo-300">
                          Ticket #{ticket.id}
                        </span>
                        {renderStatusBadge(ticket.status)}
                      </div>
                      <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                        {ticket.issue}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            {/* Amber Tool Notice Banner (Resolvo style) */}
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200/90 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Multi-Tool Agent Engine</span>
              </div>
              <p className="text-[11px] leading-relaxed text-amber-100/80">
                AI Agent tự động phân tích ý định và gọi tối đa 3 vòng công cụ (Order, Product, RAG, Ticket) trên mỗi lượt hỏi.
              </p>
            </div>

            {/* Tool Cards */}
            <div className="space-y-2.5">
              {agentTools.map((tool) => {
                const Icon = tool.icon
                return (
                  <div
                    key={tool.id}
                    className="p-3.5 rounded-2xl bg-[#141720] border border-white/[0.07] hover:border-white/[0.16] transition flex flex-col gap-2"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className={`p-2 rounded-xl border ${tool.color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <button
                        type="button"
                        onClick={() => onQuickPrompt(tool.samplePrompt)}
                        className="px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/[0.12] border border-white/10 text-[11px] font-medium text-slate-200 flex items-center gap-1 transition cursor-pointer"
                      >
                        <Sparkles className="w-3 h-3 text-blue-400" />
                        <span>Thử ngay</span>
                      </button>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-white">{tool.name}</h4>
                      <span className="inline-block mt-0.5 text-[10px] font-mono text-slate-400">
                        {tool.badge}
                      </span>
                      <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                        {tool.description}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06] flex items-center gap-2 text-[11px] text-slate-400">
              <Wrench className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span>Nhấn &ldquo;Thử ngay&rdquo; trên bất kỳ công cụ nào để điền nhanh câu hỏi mẫu.</span>
            </div>
          </>
        )}
      </div>
    </aside>
  )
}
