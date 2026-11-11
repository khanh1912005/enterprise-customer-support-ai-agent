// ==========================================
// 1. AUTH & USER SCHEMAS (app/schemas/user.py)
// ==========================================

export interface UserRegister {
  full_name: string
  email: string
  password: string
}

export interface UserResponse {
  id: number
  full_name: string
  email: string
  role: string
  is_active: boolean
}

export interface Token {
  access_token: string
  token_type: string
}

// ==========================================
// 2. CONVERSATION SCHEMAS (app/schemas/conversation.py)
// ==========================================

export interface ConversationCreate {
  title: string
}

export interface ConversationResponse {
  id: string
  title: string
  created_at: string
}

// ==========================================
// 3. CHAT SCHEMAS (app/schemas/chat.py)
// ==========================================

export interface ChatRequest {
  conversation_id: string
  message: string
}

export interface ChatResponse {
  reply: string
}

export interface ChatMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  status?: 'sending' | 'sent' | 'error'
}

// ==========================================
// 4. SUPPORT TICKET SCHEMAS (app/schemas/ticket.py)
// ==========================================

export type TicketStatus = 'pending' | 'in_progress' | 'resolved'

export interface TicketCreate {
  customer_name: string
  email: string
  issue: string
}

export interface TicketResponse {
  id: number
  customer_name: string
  email: string
  issue: string
  status: TicketStatus
}

// ==========================================
// 5. SYSTEM INFO SCHEMAS (app/main.py)
// ==========================================

export interface HealthResponse {
  status: string
}

export interface AboutResponse {
  project: string
  version: string
  developer: string
}
