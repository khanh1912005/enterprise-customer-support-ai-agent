import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Database,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  Mail,
  ShieldCheck,
  Sparkles,
  User as UserIcon,
} from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { extractErrorMessage, systemApi } from '../services/api'

interface AuthPageProps {
  mode: 'login' | 'register'
}

export function AuthPage({ mode }: AuthPageProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, registerAndLogin } = useAuth()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)

  // Reset lỗi khi đổi giữa /login và /register
  useEffect(() => {
    setError(null)
  }, [mode, location.pathname])

  // Kiểm tra kết nối tới FastAPI /health
  useEffect(() => {
    let mounted = true
    systemApi
      .health()
      .then((res) => {
        if (mounted) setBackendOnline(res.status === 'ok')
      })
      .catch(() => {
        if (mounted) setBackendOnline(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    const cleanEmail = email.trim().toLowerCase()
    if (!cleanEmail) {
      setError('Vui lòng nhập địa chỉ email của bạn.')
      return
    }

    if (password.length < 8) {
      setError('Mật khẩu phải có ít nhất 8 ký tự (theo quy định bảo mật của Backend).')
      return
    }

    if (mode === 'register') {
      const cleanName = fullName.trim()
      if (cleanName.length < 2) {
        setError('Họ và tên phải có ít nhất 2 ký tự.')
        return
      }
      if (password !== confirmPassword) {
        setError('Mật khẩu xác nhận không khớp.')
        return
      }
    }

    setSubmitting(true)
    try {
      if (mode === 'login') {
        await login(cleanEmail, password)
      } else {
        await registerAndLogin({
          full_name: fullName.trim(),
          email: cleanEmail,
          password,
        })
      }
      navigate('/chat', { replace: true })
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#090b10] text-slate-100 flex items-center justify-center p-4 sm:p-6 lg:p-10 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="pointer-events-none absolute -top-40 left-1/4 w-[520px] h-[520px] rounded-full bg-indigo-600/15 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-40 right-1/4 w-[520px] h-[520px] rounded-full bg-cyan-500/10 blur-[130px]" />

      {/* Main SaaS Card (AISTA-inspired split layout) */}
      <div className="w-full max-w-5xl rounded-3xl bg-[#11131a]/95 border border-white/[0.08] shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] backdrop-blur-xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 relative z-10">
        {/* Left Panel: 3D-style AI Bot Illustration & System Architecture */}
        <div className="lg:col-span-5 bg-gradient-to-b from-[#161924] to-[#0e1017] p-8 sm:p-10 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-white/[0.06] relative overflow-hidden">
          <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full bg-cyan-500/10 blur-3xl" />

          {/* Top status bar */}
          <div className="flex items-center justify-between relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.05] border border-white/[0.08] text-xs font-medium text-slate-300">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Enterprise AI Support</span>
            </div>

            <div
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
                backendOnline === true
                  ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/25'
                  : backendOnline === false
                    ? 'bg-amber-500/10 text-amber-300 border-amber-500/25'
                    : 'bg-slate-800/70 text-slate-400 border-white/10'
              }`}
              title="Trạng thái kết nối FastAPI Backend (/health)"
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  backendOnline === true
                    ? 'bg-emerald-400 animate-pulse'
                    : backendOnline === false
                      ? 'bg-amber-400'
                      : 'bg-slate-400'
                }`}
              />
              {backendOnline === true
                ? 'API Online'
                : backendOnline === false
                  ? 'API Offline'
                  : 'Checking API...'}
            </div>
          </div>

          {/* Center 3D-style AI Assistant Robot SVG (inspired by AISTA login artwork) */}
          <div className="my-6 flex flex-col items-center justify-center relative z-10">
            <div className="relative w-52 h-56 flex items-center justify-center">
              {/* Glowing floor shadow */}
              <div className="absolute bottom-2 w-32 h-5 rounded-full bg-cyan-400/20 blur-xl" />

              <svg
                viewBox="0 0 240 260"
                className="w-full h-full drop-shadow-[0_18px_35px_rgba(6,182,212,0.18)]"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <defs>
                  <linearGradient id="botBody" x1="60" y1="30" x2="185" y2="230" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor="#f8fafc" />
                    <stop offset="55%" stopColor="#cbd5e1" />
                    <stop offset="100%" stopColor="#64748b" />
                  </linearGradient>
                  <linearGradient id="botScreen" x1="70" y1="55" x2="170" y2="125" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor="#0f172a" />
                    <stop offset="100%" stopColor="#020617" />
                  </linearGradient>
                  <linearGradient id="eyeGlow" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#38bdf8" />
                    <stop offset="100%" stopColor="#6366f1" />
                  </linearGradient>
                </defs>

                {/* Left & Right Cat/Bot Ears */}
                <path
                  d="M72 52 L56 26 Q52 18 62 20 L92 34 Z"
                  fill="url(#botBody)"
                />
                <path
                  d="M168 52 L184 26 Q188 18 178 20 L148 34 Z"
                  fill="url(#botBody)"
                />

                {/* Robot Head Outer Shell */}
                <rect
                  x="52"
                  y="32"
                  width="136"
                  height="98"
                  rx="36"
                  fill="url(#botBody)"
                  stroke="#ffffff"
                  strokeOpacity="0.5"
                  strokeWidth="1.5"
                />

                {/* Visor Screen */}
                <rect
                  x="68"
                  y="48"
                  width="104"
                  height="66"
                  rx="22"
                  fill="url(#botScreen)"
                  stroke="#38bdf8"
                  strokeOpacity="0.35"
                  strokeWidth="1.5"
                />

                {/* Glowing Cyan Eyes */}
                <rect
                  x="86"
                  y="72"
                  width="24"
                  height="16"
                  rx="6"
                  fill="url(#eyeGlow)"
                />
                <rect
                  x="130"
                  y="72"
                  width="24"
                  height="16"
                  rx="6"
                  fill="url(#eyeGlow)"
                />
                {/* Eye shine */}
                <circle cx="93" cy="77" r="2.5" fill="#e0f2fe" />
                <circle cx="137" cy="77" r="2.5" fill="#e0f2fe" />

                {/* Subtle happy smile arc */}
                <path
                  d="M112 97 Q120 103 128 97"
                  stroke="#38bdf8"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />

                {/* Robot Torso */}
                <path
                  d="M78 136 C78 130 162 130 162 136 L172 204 C174 220 156 232 120 232 C84 232 66 220 68 204 Z"
                  fill="url(#botBody)"
                />

                {/* Left Arm */}
                <rect
                  x="44"
                  y="142"
                  width="26"
                  height="54"
                  rx="13"
                  transform="rotate(14 57 169)"
                  fill="url(#botBody)"
                />

                {/* Right Waving Arm */}
                <rect
                  x="170"
                  y="118"
                  width="26"
                  height="56"
                  rx="13"
                  transform="rotate(-28 183 146)"
                  fill="url(#botBody)"
                />

                {/* Power Emblem on Chest */}
                <circle
                  cx="120"
                  cy="182"
                  r="14"
                  fill="#0f172a"
                  stroke="#38bdf8"
                  strokeOpacity="0.5"
                  strokeWidth="1.5"
                />
                <path
                  d="M120 174 V182 M114.5 177.5 A7 7 0 1 0 125.5 177.5"
                  stroke="#38bdf8"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <p className="text-center text-sm text-slate-300 font-medium mt-1">
              Trợ lý AI Hỗ trợ Khách hàng Doanh nghiệp
            </p>
            <p className="text-center text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
              Tra cứu đơn hàng, tìm kiếm sản phẩm, hỏi đáp chính sách RAG và gửi yêu cầu hỗ trợ tự động 24/7.
            </p>
          </div>

          {/* Bottom Tech Stack Pills */}
          <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300 relative z-10">
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <Cpu className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              <span className="truncate">LangGraph + Multi-Tool</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <Database className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="truncate">PostgreSQL + Chroma RAG</span>
            </div>
          </div>
        </div>

        {/* Right Panel: Login / Register Form */}
        <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-center bg-[#11131a]">
          <div className="max-w-md w-full mx-auto">
            {/* Spaced Brand Header like A I S T A */}
            <div className="mb-8">
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <span className="text-lg font-bold tracking-[0.28em] text-white uppercase">
                  R E S O L V O
                </span>
              </div>

              <div className="flex items-baseline justify-between gap-4 flex-wrap">
                <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                  {mode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản'}
                </h1>

                {mode === 'login' ? (
                  <div className="text-xs text-slate-400 flex items-center gap-2">
                    <span>Chưa có tài khoản?</span>
                    <Link
                      to="/register"
                      className="px-2.5 py-1 rounded-md bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 text-slate-200 font-medium transition"
                    >
                      Đăng ký
                    </Link>
                  </div>
                ) : (
                  <div className="text-xs text-slate-400 flex items-center gap-2">
                    <span>Đã có tài khoản?</span>
                    <Link
                      to="/login"
                      className="px-2.5 py-1 rounded-md bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 text-slate-200 font-medium transition"
                    >
                      Đăng nhập
                    </Link>
                  </div>
                )}
              </div>
              <p className="text-sm text-slate-400 mt-1.5">
                {mode === 'login'
                  ? 'Đăng nhập để trò chuyện trực tiếp với AI Agent hỗ trợ khách hàng.'
                  : 'Đăng ký tài khoản khách hàng mới để sử dụng đầy đủ tính năng hỗ trợ AI.'}
              </p>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 text-xs sm:text-sm flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="leading-relaxed">{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">
                    Họ và tên khách hàng
                  </label>
                  <div className="relative">
                    <UserIcon className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      required
                      minLength={2}
                      maxLength={100}
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Nhập họ và tên (VD: Nguyễn Văn A)"
                      className="w-full pl-10 pr-4 py-3 rounded-xl bg-[#181b24] border border-white/[0.08] text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Địa chỉ Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Nhập email của bạn (VD: customer@example.com)"
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-[#181b24] border border-white/[0.08] text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Mật khẩu
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={8}
                    maxLength={128}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Nhập mật khẩu (tối thiểu 8 ký tự)"
                    className="w-full pl-10 pr-11 py-3 rounded-xl bg-[#181b24] border border-white/[0.08] text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 p-1"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {mode === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">
                    Xác nhận mật khẩu
                  </label>
                  <div className="relative">
                    <ShieldCheck className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      minLength={8}
                      maxLength={128}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Nhập lại mật khẩu"
                      className="w-full pl-10 pr-4 py-3 rounded-xl bg-[#181b24] border border-white/[0.08] text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
                    />
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full mt-2 py-3 px-5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 disabled:opacity-60 text-white font-semibold text-sm shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 transition cursor-pointer"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>{mode === 'login' ? 'Đang đăng nhập...' : 'Đang tạo tài khoản...'}</span>
                  </>
                ) : (
                  <>
                    <span>{mode === 'login' ? 'Đăng nhập vào hệ thống' : 'Đăng ký & Bắt đầu trò chuyện'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Security & JWT info footer */}
            <div className="mt-7 pt-5 border-t border-white/[0.06] flex items-center justify-between text-xs text-slate-500">
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Xác thực bảo mật JWT Bearer
              </span>
              <span>FastAPI + React TS</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
