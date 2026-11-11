import { BookOpen, Database, Sparkles, X } from 'lucide-react'

interface KnowledgeBaseModalProps {
  isOpen: boolean
  onClose: () => void
  onAskQuestion: (question: string) => void
}

export function KnowledgeBaseModal({
  isOpen,
  onClose,
  onAskQuestion,
}: KnowledgeBaseModalProps) {
  if (!isOpen) return null

  const sampleQuestions = [
    'Khách hàng có thể gửi yêu cầu đổi trả sản phẩm trong những trường hợp nào?',
    'Khi yêu cầu đổi trả sản phẩm, khách hàng cần cung cấp những thông tin gì?',
    'Quy trình xử lý đổi trả sản phẩm gồm mấy bước?',
    'Chính sách hiện tại có quy định thời hạn đổi trả hoặc mức phí cụ thể không?',
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-black/75 backdrop-blur-xs"
        onClick={onClose}
      />

      <div className="relative z-10 w-full max-w-2xl rounded-3xl bg-[#12151f] border border-white/[0.1] shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-white/[0.08] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">
                Knowledge Base & Chính sách Doanh nghiệp (RAG)
              </h2>
              <p className="text-xs text-slate-400">
                Dữ liệu được nhúng vào ChromaDB và truy xuất tự động qua công cụ{' '}
                <code className="text-amber-300">search_knowledge_base</code>
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-5 text-xs leading-relaxed text-slate-300">
          <div className="p-4 rounded-2xl bg-[#171b26] border border-white/[0.07] space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-white">
                CHÍNH SÁCH ĐỔI TRẢ SẢN PHẨM (return_policy.md)
              </span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-cyan-500/15 text-cyan-300 text-[10px] font-mono">
                <Database className="w-3 h-3" />
                category=&quot;policies&quot;
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                <h4 className="font-semibold text-white mb-1">1. Điều kiện đổi trả</h4>
                <ul className="space-y-1 text-slate-400 list-disc list-inside">
                  <li>Sản phẩm bị lỗi kỹ thuật.</li>
                  <li>Sản phẩm bị hư hỏng trong quá trình vận chuyển.</li>
                  <li>Sản phẩm được giao không đúng với đơn đặt hàng.</li>
                </ul>
              </div>

              <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                <h4 className="font-semibold text-white mb-1">2. Điều kiện sản phẩm</h4>
                <ul className="space-y-1 text-slate-400 list-disc list-inside">
                  <li>Cung cấp mã đơn hàng.</li>
                  <li>Mô tả tình trạng sản phẩm.</li>
                  <li>Hình ảnh hoặc video thể hiện lỗi nếu có.</li>
                </ul>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <h4 className="font-semibold text-white mb-1">3. Quy trình xử lý 4 bước</h4>
              <p className="text-slate-400">
                Bước 1: Khách hàng gửi yêu cầu hỗ trợ → Bước 2: Bộ phận CSKH tiếp nhận → Bước 3:
                Nhân viên kiểm tra thông tin đơn hàng và tình trạng sản phẩm → Bước 4: Nhân viên
                thông báo phương án xử lý cho khách hàng.
              </p>
            </div>
          </div>

          {/* Sample RAG Prompts */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">
              Chọn câu hỏi mẫu để thử nghiệm RAG ngay
            </h4>
            <div className="space-y-2">
              {sampleQuestions.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    onClose()
                    onAskQuestion(q)
                  }}
                  className="w-full text-left p-3 rounded-xl bg-[#171b26] hover:bg-[#1e2332] border border-white/[0.07] hover:border-amber-500/40 transition flex items-center justify-between gap-3 group cursor-pointer"
                >
                  <span className="text-slate-200 group-hover:text-white">{q}</span>
                  <span className="shrink-0 inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/15 text-amber-300 text-[11px] font-medium">
                    <Sparkles className="w-3 h-3" />
                    Hỏi AI
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
