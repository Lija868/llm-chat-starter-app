import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

export default function MessageBubble({ role, content }: any) {
  return (
    <div className={`message ${role}`}>
      {role === "assistant" ? (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      ) : (
        <span>{content}</span>
      )}
    </div>
  )
}
