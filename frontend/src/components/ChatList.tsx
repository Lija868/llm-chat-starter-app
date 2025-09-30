import { useState } from "react"
import { useNavigate } from "react-router-dom";

export default function ChatList({
  chats,
  onSelect,
  activeChatId,
  token,
  refreshChats,
}: any) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newTitle, setNewTitle] = useState("")
  const API = import.meta.env.VITE_API_URL || "http://0.0.0.0:8000"
  const navigate = useNavigate();

async function renameChat(chatId: number, title: string) {
  if (!title.trim()) return;
  try {
    const res = await fetch(`${API}/chats/${chatId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({ title }),
    });

    if (res.status === 401) {
      // Token expired → redirect to login
      localStorage.removeItem("token");
      navigate("/login");
      return;
    }

    if (!res.ok) {
      const text = await res.text();
      console.error("Rename failed:", text);
      return;
    }

    if (refreshChats) refreshChats(); // reload chat list after rename
  } catch (err) {
    console.error("Rename failed:", err);
  }
}

  function handleDoubleClick(chat: any) {
    setEditingId(chat.id)
    setNewTitle(chat.title)
  }

  function handleBlur(chatId: number) {
    renameChat(chatId, newTitle)
    setEditingId(null)
  }

  return (
    <div className="chat-list">
      {chats.map((c: any) => (
        <div
          key={c.id}
          className={"chat-item" + (activeChatId === c.id ? " active" : "")}
          onClick={() => onSelect(c)}
          onDoubleClick={() => handleDoubleClick(c)}
        >
          {editingId === c.id ? (
            <input
              autoFocus
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              onBlur={() => handleBlur(c.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleBlur(c.id)
                if (e.key === "Escape") setEditingId(null)
              }}
            />
          ) : (
            c.title
          )}
        </div>
      ))}
    </div>
  )
}
