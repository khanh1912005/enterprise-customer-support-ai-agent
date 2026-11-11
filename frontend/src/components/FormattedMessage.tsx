import { Check, Copy } from 'lucide-react'
import { useState, type ReactNode } from 'react'

interface FormattedMessageProps {
  content: string
  role: 'user' | 'assistant'
}

// Hàm định dạng inline (**bold**, `code`, mã đơn DHxxx)
function renderInline(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\bDH\d+\b)/g)
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={idx} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      )
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code
          key={idx}
          className="px-1.5 py-0.5 rounded bg-indigo-500/15 border border-indigo-500/30 text-indigo-200 text-xs font-mono"
        >
          {part.slice(1, -1)}
        </code>
      )
    }
    if (/^DH\d+$/.test(part)) {
      return (
        <span
          key={idx}
          className="px-1.5 py-0.5 rounded bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-semibold"
        >
          {part}
        </span>
      )
    }
    return part
  })
}

export function FormattedMessage({ content, role }: FormattedMessageProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      // ignore
    }
  }

  const lines = content.split('\n')

  return (
    <div className="group relative">
      <div className="space-y-1.5 text-sm leading-relaxed">
        {lines.map((rawLine, index) => {
          const line = rawLine.trim()
          if (!line) {
            return <div key={index} className="h-1.5" />
          }

          // Heading markdown
          if (line.startsWith('### ')) {
            return (
              <h4 key={index} className="font-semibold text-white pt-1">
                {renderInline(line.slice(4))}
              </h4>
            )
          }
          if (line.startsWith('## ')) {
            return (
              <h3 key={index} className="font-bold text-white text-base pt-1">
                {renderInline(line.slice(3))}
              </h3>
            )
          }

          // Bullet points
          if (line.startsWith('- ') || line.startsWith('* ') || line.startsWith('• ')) {
            return (
              <div key={index} className="flex items-start gap-2 pl-1">
                <span className="text-cyan-400 mt-1.5 text-[10px]">●</span>
                <span className="flex-1">{renderInline(line.slice(2))}</span>
              </div>
            )
          }

          // Numbered list
          const numberedMatch = line.match(/^(\d+)\.\s+(.*)$/)
          if (numberedMatch) {
            return (
              <div key={index} className="flex items-start gap-2 pl-1">
                <span className="text-indigo-300 font-semibold min-w-[1.25rem]">
                  {numberedMatch[1]}.
                </span>
                <span className="flex-1">{renderInline(numberedMatch[2])}</span>
              </div>
            )
          }

          return <p key={index}>{renderInline(rawLine)}</p>
        })}
      </div>

      {role === 'assistant' && (
        <button
          type="button"
          onClick={handleCopy}
          title="Sao chép câu trả lời"
          className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-2 -right-2 p-1.5 rounded-lg bg-[#1c202c] border border-white/10 text-slate-400 hover:text-white shadow-md cursor-pointer"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      )}
    </div>
  )
}
