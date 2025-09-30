import { useEffect, useState, useRef } from "react";
import MessageBubble from "./MessageBubble";
import { useNavigate } from "react-router-dom";

export default function ChatView({ chat, token }: any) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const API = import.meta.env.VITE_API_URL || "http://0.0.0.0:8000";
  const navigate = useNavigate();

  const assistantIndexRef = useRef<number | null>(null);

  useEffect(() => {
    if (chat) fetchMessages();
  }, [chat]);

  async function apiFetch(url: string, options: RequestInit = {}) {
    const res = await fetch(url, options);

    if (res.status === 401) {
      // Token expired → redirect to login
      localStorage.removeItem("token");
      navigate("/login");
      throw new Error("Unauthorized: Token expired");
    }

    return res;
  }

  async function fetchMessages() {
    try {
      const r = await apiFetch(`${API}/chats/${chat.id}/messages`, {
        headers: { Authorization: "Bearer " + token },
      });
      const j = await r.json();
      setMessages(j);
    } catch (e) {
      console.error("Fetch messages failed:", e);
    }
  }

  async function send() {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await apiFetch(`${API}/chats/${chat.id}/messages/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify(userMsg),
      });

      if (!response.body) throw new Error("ReadableStream not supported.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let assistantMessage = "";

      setMessages((prev) => {
        assistantIndexRef.current = prev.length;
        return [...prev, { role: "assistant", content: "" }];
      });

      let buffer = "";

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";

          for (const part of parts) {
            const lines = part.split("\n");
            for (const line of lines) {
              const trimmed = line.trim();
              if (!trimmed) continue;

              if (trimmed.startsWith("data: ")) {
                const dataStr = trimmed.slice("data: ".length);

                if (dataStr === "[DONE]") {
                  done = true;
                  break;
                }

                try {
                  const parsed = JSON.parse(dataStr);
                  const content = parsed.content || "";

                  assistantMessage += content;

                  setMessages((prev) => {
                    if (assistantIndexRef.current === null) return prev;
                    const newMessages = [...prev];
                    newMessages[assistantIndexRef.current] = {
                      role: "assistant",
                      content: assistantMessage,
                    };
                    return newMessages;
                  });
                } catch (e) {
                  console.error("Error parsing JSON chunk:", e);
                }
              }
            }
          }
        }
      }
    } catch (e) {
      console.error("Send failed:", e);
    } finally {
      setLoading(false);
    }
  }

  async function uploadFile(file: File) {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const r = await apiFetch(`${API}/chats/${chat.id}/files`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
        },
        body: formData,
      });

      if (!r.ok) {
        const err = await r.text();
        console.error("File upload failed:", err);
        return;
      }

      const uploaded = await r.json();
      console.log("Uploaded file:", uploaded);

      setMessages((prev) => [
        ...prev,
        { role: "system", content: `📎 Uploaded file: ${uploaded.file.filename}` },
      ]);
    } catch (e) {
      console.error("Upload failed:", e);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="chatview">
      <h2>{chat.title}</h2>
      <div className="messages">
        {messages.map((m: any, i: number) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
        {loading && (
          <div className="message assistant">
            <span className="dots">...</span>
          </div>
        )}
      </div>
      <div className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          disabled={loading || uploading}
        />
        <input
          type="file"
          onChange={(e) => {
            if (e.target.files?.[0]) {
              uploadFile(e.target.files[0]);
              e.target.value = "";
            }
          }}
          disabled={uploading || loading}
        />
        <button onClick={send} disabled={loading || uploading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
