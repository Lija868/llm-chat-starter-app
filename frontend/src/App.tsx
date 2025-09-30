import { useState, useEffect } from 'react'
import { useNavigate } from "react-router-dom";

import AuthForm from './components/AuthForm'
import ChatList from './components/ChatList'
import ChatView from './components/ChatView'

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [userEmail, setUserEmail] = useState<string | null>(localStorage.getItem('email'))
  const [chats, setChats] = useState<any[]>([])
  const [selectedChat, setSelectedChat] = useState<any | null>(null)
  const API = import.meta.env.VITE_API_URL || 'http://0.0.0.0:8000'
  const navigate = useNavigate();

  async function apiFetch(url: string, options: RequestInit = {}) {
    const res = await fetch(url, options);

    if (res.status === 401) {
      // Token expired → redirect to login
      localStorage.removeItem("token");
      localStorage.removeItem("email");
      setToken(null);
      setUserEmail(null);
      navigate("/login");
      throw new Error("Unauthorized: Token expired");
    }

    return res;
  }

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      if (userEmail) localStorage.setItem('email', userEmail)
      fetchChats()
    }
  }, [token])

  async function fetchChats() {
    if (!token) return
    try {
      const r = await apiFetch(API + '/chats', {
        headers: { Authorization: 'Bearer ' + token },
      })
      const data = await r.json()
      setChats(data)

      // if no chat selected → select first one
      if (data.length > 0 && !selectedChat) {
        setSelectedChat(data[0])
      }
    } catch (err) {
      console.error("Failed to fetch chats:", err)
    }
  }

  async function createChat() {
    if (!token) return
    try {
      const r = await apiFetch(API + '/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + token,
        },
        body: JSON.stringify({ title: 'New Chat' }),
      })
      if (r.ok) {
        await fetchChats()
      }
    } catch (err) {
      console.error("Failed to create chat:", err)
    }
  }

  async function renameChat(id: number, title: string) {
    if (!token) return
    try {
      await apiFetch(API + `/chats/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + token,
        },
        body: JSON.stringify({ title }),
      })
      fetchChats()
    } catch (err) {
      console.error("Failed to rename chat:", err)
    }
  }

  async function deleteChat(id: number) {
    if (!token) return
    try {
      await apiFetch(API + `/chats/${id}`, {
        method: 'DELETE',
        headers: { Authorization: 'Bearer ' + token },
      })
      fetchChats()

      // if deleted chat was selected → clear selection
      if (selectedChat?.id === id) {
        setSelectedChat(null)
      }
    } catch (err) {
      console.error("Failed to delete chat:", err)
    }
  }

  async function uploadFile(file: File, chatId: number, setMessages: any) {
    if (!token) return
    const formData = new FormData()
    formData.append("file", file)

    try {
      const r = await apiFetch(`${API}/chats/${chatId}/files`, {
        method: "POST",
        headers: { Authorization: "Bearer " + token },
        body: formData,
      })
      const data = await r.json()
      setMessages((prev: any) => [
        ...prev,
        { role: "assistant", content: `✅ File uploaded: ${data.file.filename}` },
      ])
    } catch (err) {
      console.error("Upload failed:", err)
      setMessages((prev: any) => [
        ...prev,
        { role: "assistant", content: "❌ File upload failed." },
      ])
    }
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    setToken(null)
    setUserEmail(null)
    setChats([])
    setSelectedChat(null)
  }

  if (!token)
    return (
      <AuthForm
        onLoggedIn={(t: string, e: string) => {
          setToken(t)
          setUserEmail(e)
        }}
      />
    )

  return (
    <div className="app">
      <aside className="sidebar">
        <h3>Chats</h3>
        <button onClick={createChat}>New Chat</button>

        <ChatList
          chats={chats}
          activeChatId={selectedChat?.id || null}
          onSelect={setSelectedChat}
          onRename={renameChat}
          onDelete={deleteChat}
          token={token}
          refreshChats={fetchChats}
        />

        <div className="user-info">
          <span className="user-email">{userEmail}</span>
          <button onClick={logout} className="btn btn-logout">
            Logout
          </button>
        </div>
      </aside>

      <main className="main">
        {selectedChat ? (
          <ChatView chat={selectedChat} token={token} />
        ) : (
          <div className="placeholder">Select or create a chat</div>
        )}
      </main>
    </div>
  )
}
