import axios, { AxiosError } from 'axios'
import type {
  AboutResponse,
  ChatRequest,
  ChatResponse,
  ConversationCreate,
  ConversationResponse,
  HealthResponse,
  TicketCreate,
  TicketResponse,
  Token,
  UserRegister,
  UserResponse,
} from '../types'

const TOKEN_STORAGE_KEY = 'enterprise_ai_access_token'

// Mặc định sử dụng '/api' (được Vite proxy sang http://127.0.0.1:8000 để tránh lỗi CORS mà không cần sửa code Backend).
// Khi deploy lên Vercel/Render có thể đặt biến môi trường VITE_API_BASE_URL=https://your-backend.onrender.com
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Tự động đính kèm JWT Bearer Token vào mọi request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const tokenStorage = {
  get: (): string | null => localStorage.getItem(TOKEN_STORAGE_KEY),
  set: (token: string): void => localStorage.setItem(TOKEN_STORAGE_KEY, token),
  clear: (): void => localStorage.removeItem(TOKEN_STORAGE_KEY),
}

// Hàm trích xuất thông báo lỗi thân thiện từ FastAPI HTTPException / Validation Error
export function extractErrorMessage(error: unknown, fallback = 'Đã xảy ra lỗi kết nối máy chủ.'): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ detail?: string | Array<{ msg?: string; loc?: Array<string | number> }> }>

    if (!axiosErr.response) {
      return 'Không thể kết nối tới Backend FastAPI (http://127.0.0.1:8000). Hãy kiểm tra xem server FastAPI đã khởi động chưa.'
    }

    const detail = axiosErr.response.data?.detail
    if (typeof detail === 'string') {
      // Dịch một số thông báo phổ biến sang tiếng Việt rõ ràng nhưng vẫn giữ ngữ cảnh
      const translations: Record<string, string> = {
        'Email already registered': 'Email này đã được đăng ký. Vui lòng đăng nhập hoặc dùng email khác.',
        'Incorrect email or password': 'Email hoặc mật khẩu không chính xác.',
        'Account is inactive': 'Tài khoản của bạn hiện đang bị khóa.',
        'Conversation not found': 'Không tìm thấy cuộc hội thoại này.',
        'Conversation title cannot be empty': 'Tiêu đề cuộc hội thoại không được để trống.',
        'LLM API is not configured': 'Backend chưa cấu hình khóa OPENAI_API_KEY trong file .env.',
        'AI service is unavailable': 'Dịch vụ AI (OpenAI API) hiện không phản hồi.',
        'Internal AI Agent error': 'AI Agent gặp lỗi nội bộ khi xử lý yêu cầu.',
      }
      return translations[detail] || detail
    }

    if (Array.isArray(detail) && detail.length > 0) {
      return detail
        .map((item) => {
          const field = item.loc?.[item.loc.length - 1]
          return field ? `${String(field)}: ${item.msg}` : item.msg
        })
        .join(' | ')
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  return fallback
}

// ==========================================
// 1. AUTHENTICATION API (/auth)
// ==========================================

export const authApi = {
  register: async (payload: UserRegister): Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>('/auth/register', payload)
    return response.data
  },

  // FastAPI sử dụng OAuth2PasswordRequestForm nên cần gửi dạng application/x-www-form-urlencoded
  login: async (email: string, password: string): Promise<Token> => {
    const formData = new URLSearchParams()
    formData.append('username', email.trim())
    formData.append('password', password)

    const response = await apiClient.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },
}

// ==========================================
// 2. USER PROFILE API (/users)
// ==========================================

export const userApi = {
  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>('/users/me')
    return response.data
  },
}

// ==========================================
// 3. CONVERSATIONS API (/conversations)
// ==========================================

export const conversationApi = {
  list: async (): Promise<ConversationResponse[]> => {
    const response = await apiClient.get<ConversationResponse[]>('/conversations')
    return response.data
  },

  create: async (payload: ConversationCreate): Promise<ConversationResponse> => {
    const response = await apiClient.post<ConversationResponse>('/conversations', payload)
    return response.data
  },

  getById: async (conversationId: string): Promise<ConversationResponse> => {
    const response = await apiClient.get<ConversationResponse>(`/conversations/${conversationId}`)
    return response.data
  },
}

// ==========================================
// 4. AI CHAT API (/chat)
// ==========================================

export const chatApi = {
  sendMessage: async (payload: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chat', payload)
    return response.data
  },
}

// ==========================================
// 5. SUPPORT TICKET API (/support-ticket)
// ==========================================

export const ticketApi = {
  list: async (): Promise<TicketResponse[]> => {
    const response = await apiClient.get<TicketResponse[]>('/support-ticket')
    return response.data
  },

  create: async (payload: TicketCreate): Promise<TicketResponse> => {
    const response = await apiClient.post<TicketResponse>('/support-ticket', payload)
    return response.data
  },
}

// ==========================================
// 6. SYSTEM HEALTH & INFO API (/health, /about)
// ==========================================

export const systemApi = {
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health', { timeout: 5000 })
    return response.data
  },

  about: async (): Promise<AboutResponse> => {
    const response = await apiClient.get<AboutResponse>('/about', { timeout: 5000 })
    return response.data
  },
}
