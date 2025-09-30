import { useState } from 'react'

export default function AuthForm({
  onLoggedIn,
}: {
  onLoggedIn: (token: string, email: string) => void
}) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const API = import.meta.env.VITE_API_URL || 'http://0.0.0.0:8000'

  async function register() {
    try {
      const r = await fetch(API + '/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!r.ok) {
        const err = await r.json()
        alert(err.detail || 'Registration failed')
        return
      }

      // ✅ Auto-login after successful registration
      await login(true)
    } catch (err) {
      console.error(err)
      alert('Something went wrong during registration')
    }
  }

  async function login(isAuto = false) {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    try {
      const r = await fetch(API + '/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString(),
      })

      const j = await r.json()
      if (j.access_token) {
        // ✅ store email + token
        localStorage.setItem('token', j.access_token)
        localStorage.setItem('email', email)
        onLoggedIn(j.access_token, email)

        if (!isAuto) alert('Login successful')
      } else {
        alert('Login failed')
      }
    } catch (err) {
      console.error(err)
      alert('Something went wrong during login')
    }
  }

  return (
    <div className="auth-root">
      <div className="auth-card">
        <h2>Welcome</h2>
        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <div className="auth-actions">
          <button onClick={register} className="btn btn-primary">
            Register
          </button>
          <button onClick={() => login()} className="btn btn-accent">
            Login
          </button>
        </div>
      </div>
    </div>
  )
}