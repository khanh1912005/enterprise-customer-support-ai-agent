import {
  CheckCircle2,
  LogOut,
  Mail,
  MessageSquare,
  Shield,
  Ticket as TicketIcon,
  User as UserIcon,
  X,
} from 'lucide-react'
import type { UserResponse } from '../types'

interface ProfileModalProps {
  isOpen: boolean
  onClose: () => void
  user: UserResponse
  conversationCount: number
  ticketCount: number
  onLogout: () => void
}

export function ProfileModal({
  isOpen,
  onClose,
  user,
  conversationCount,
  ticketCount,
  onLogout,
}: ProfileModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-black/75 backdrop-blur-xs"
        onClick={onClose}
      />

      <div className="relative z-10 w-full max-w-md rounded-3xl bg-[#12151f] border border-white/[0.1] shadow-2xl overflow-hidden">
        {/* Top Banner */}
        <div className="h-24 bg-gradient-to-r from-indigo-600/40 via-blue-600/30 to-cyan-500/30 relative">
          <button
            type="button"
            onClick={onClose}
            className="absolute top-3.5 right-3.5 p-1.5 rounded-full bg-black/40 hover:bg-black/60 text-slate-300 hover:text-white transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="absolute -bottom-8 left-6 w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-400 border-4 border-[#12151f] flex items-center justify-center text-xl font-bold text-white shadow-lg">
            {user.full_name.charAt(0).toUpperCase()}
          </div>
        </div>

        {/* Body */}
        <div className="pt-11 px-6 pb-6 space-y-5">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h2 className="text-lg font-bold text-white">{user.full_name}</h2>
              <p className="text-xs text-slate-400">{user.email}</p>
            </div>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {user.is_active ? 'Đang hoạt động' : 'Tạm khóa'}
            </span>
          </div>

          {/* Account Details */}
          <div className="space-y-2.5 rounded-2xl bg-[#171b26] border border-white/[0.07] p-4 text-xs">
            <div className="flex items-center justify-between py-1.5 border-b border-white/[0.05]">
              <span className="text-slate-400 flex items-center gap-2">
                <UserIcon className="w-3.5 h-3.5 text-indigo-400" />
                Mã định danh (User ID)
              </span>
              <span className="font-mono font-semibold text-white">#{user.id}</span>
            </div>

            <div className="flex items-center justify-between py-1.5 border-b border-white/[0.05]">
              <span className="text-slate-400 flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-cyan-400" />
                Địa chỉ Email
              </span>
              <span className="font-medium text-slate-200">{user.email}</span>
            </div>

            <div className="flex items-center justify-between py-1.5">
              <span className="text-slate-400 flex items-center gap-2">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                Phân quyền (Role)
              </span>
              <span className="uppercase font-semibold text-indigo-300">{user.role}</span>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#171b26] border border-white/[0.07] flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-blue-500/15 text-blue-400">
                <MessageSquare className="w-4 h-4" />
              </div>
              <div>
                <span className="text-base font-bold text-white block">{conversationCount}</span>
                <span className="text-[11px] text-slate-400">Cuộc hội thoại</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#171b26] border border-white/[0.07] flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-purple-500/15 text-purple-400">
                <TicketIcon className="w-4 h-4" />
              </div>
              <div>
                <span className="text-base font-bold text-white block">{ticketCount}</span>
                <span className="text-[11px] text-slate-400">Phiếu hỗ trợ</span>
              </div>
            </div>
          </div>

          {/* Footer actions */}
          <div className="pt-2 flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-xs font-medium text-slate-200 transition cursor-pointer"
            >
              Đóng
            </button>
            <button
              type="button"
              onClick={() => {
                onClose()
                onLogout()
              }}
              className="px-4 py-2 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-xs font-semibold text-rose-300 flex items-center gap-1.5 transition cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Đăng xuất</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
