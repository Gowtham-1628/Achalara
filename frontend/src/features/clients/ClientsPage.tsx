import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useLoginClient, useCreateClient } from '@/hooks/useClients'
import { loadKnownClients, saveKnownClient } from '@/lib/constants'
import { useScope } from '@/context/ScopeContext'
import type { ClientResponse } from '@/api/types'

// CONTRACT: no list-all-clients endpoint — track known clients in localStorage (BACKEND_GAPS.md)
function useKnownClients() {
  const [clients, setClients] = useState<ClientResponse[]>(
    () => loadKnownClients() as ClientResponse[]
  )
  const add = (c: ClientResponse) => {
    saveKnownClient(c)
    setClients((prev) => [...prev.filter((x) => x.id !== c.id), c])
  }
  return { clients, add }
}

type Mode = 'list' | 'login' | 'create'

export function ClientsPage() {
  const navigate = useNavigate()
  const { setClient } = useScope()
  const { clients, add } = useKnownClients()
  const loginClient = useLoginClient()
  const createClient = useCreateClient()

  const [mode, setMode] = useState<Mode>(clients.length === 0 ? 'login' : 'list')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [createEmail, setCreateEmail] = useState('')
  const [error, setError] = useState('')

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const client = await loginClient.mutateAsync({ email, password })
      add(client)
      setEmail('')
      setPassword('')
      setMode('list')
    } catch (err) {
      setError(String(err))
    }
  }

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const client = await createClient.mutateAsync({ name, email: createEmail })
      add(client)
      setName('')
      setCreateEmail('')
      setMode('list')
    } catch (err) {
      setError(String(err))
    }
  }

  const selectClient = (client: ClientResponse) => {
    setClient(client.id, client.name)
    navigate('/app/performance')
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-summit-ink">Clients</h1>
          <p className="text-stone text-sm mt-1">
            Sign in to an existing client account or create a new one.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setMode('login'); setError('') }}
            className={`px-3 py-1.5 text-sm rounded-btn border transition-colors ${
              mode === 'login'
                ? 'border-pine bg-pine text-paper'
                : 'border-stone/30 text-stone hover:border-pine hover:text-pine'
            }`}
          >
            Sign in
          </button>
          <button
            onClick={() => { setMode('create'); setError('') }}
            className={`px-3 py-1.5 text-sm rounded-btn border transition-colors ${
              mode === 'create'
                ? 'border-gold bg-gold text-summit-ink'
                : 'border-stone/30 text-stone hover:border-gold hover:text-summit-ink'
            }`}
          >
            + New client
          </button>
        </div>
      </div>

      {/* Login form */}
      {mode === 'login' && (
        <form
          onSubmit={handleLogin}
          className="mb-6 border border-stone/20 rounded-card p-6 bg-mist/30"
        >
          <h2 className="font-medium text-summit-ink mb-1">Sign in to a client account</h2>
          <p className="text-xs text-stone mb-4">
            Enter the client's email and the platform password.
          </p>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-stone block mb-1">Client email</label>
              <input
                required
                autoFocus
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="contact@acme.com"
                className="w-full border border-stone/30 rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-pine"
              />
            </div>
            <div>
              <label className="text-xs text-stone block mb-1">Password</label>
              <input
                required
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Platform password"
                className="w-full border border-stone/30 rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-pine"
              />
            </div>
          </div>
          {error && <p className="text-loss text-xs mt-3">{error}</p>}
          <div className="flex items-center gap-3 mt-4">
            <button
              type="submit"
              disabled={loginClient.isPending}
              className="px-4 py-2 bg-pine text-paper text-sm rounded-btn hover:bg-pine-deep transition-colors disabled:opacity-50"
            >
              {loginClient.isPending ? 'Signing in…' : 'Sign in'}
            </button>
            {clients.length > 0 && (
              <button
                type="button"
                onClick={() => { setMode('list'); setError('') }}
                className="text-sm text-stone hover:text-summit-ink transition-colors"
              >
                Back to list
              </button>
            )}
            <button
              type="button"
              onClick={() => { setMode('create'); setError('') }}
              className="text-sm text-stone hover:text-summit-ink transition-colors ml-auto"
            >
              Create a new client instead →
            </button>
          </div>
        </form>
      )}

      {/* Create form */}
      {mode === 'create' && (
        <form
          onSubmit={handleCreate}
          className="mb-6 border border-stone/20 rounded-card p-6 bg-mist/30"
        >
          <h2 className="font-medium text-summit-ink mb-1">Create a new client</h2>
          <p className="text-xs text-stone mb-4">
            Use the platform password to sign back in later.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-stone block mb-1">Client name</label>
              <input
                required
                autoFocus
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Acme Corp"
                className="w-full border border-stone/30 rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-pine"
              />
            </div>
            <div>
              <label className="text-xs text-stone block mb-1">Email</label>
              <input
                required
                type="email"
                value={createEmail}
                onChange={(e) => setCreateEmail(e.target.value)}
                placeholder="contact@acme.com"
                className="w-full border border-stone/30 rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-pine"
              />
            </div>
          </div>
          {error && <p className="text-loss text-xs mt-3">{error}</p>}
          <div className="flex items-center gap-3 mt-4">
            <button
              type="submit"
              disabled={createClient.isPending}
              className="px-4 py-2 bg-gold text-summit-ink text-sm rounded-btn hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {createClient.isPending ? 'Creating…' : 'Create client'}
            </button>
            <button
              type="button"
              onClick={() => { setMode(clients.length ? 'list' : 'login'); setError('') }}
              className="text-sm text-stone hover:text-summit-ink transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Client list */}
      {clients.length > 0 && mode === 'list' && (
        <div className="divide-y divide-stone/10 border border-stone/20 rounded-card overflow-hidden">
          {clients.map((client) => (
            <div
              key={client.id}
              className="flex items-center justify-between px-6 py-4 hover:bg-mist/40 transition-colors"
            >
              <div>
                <p className="font-medium text-summit-ink">{client.name}</p>
                <p className="text-xs text-stone font-mono">{client.email}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => selectClient(client)}
                  className="px-3 py-1.5 text-xs border border-pine text-pine rounded-btn hover:bg-pine hover:text-paper transition-colors"
                >
                  View performance
                </button>
                <Link
                  to={`/app/clients/${client.id}`}
                  className="px-3 py-1.5 text-xs border border-stone/30 text-stone rounded-btn hover:border-summit-ink hover:text-summit-ink transition-colors"
                >
                  Manage
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty list with no form shown */}
      {clients.length === 0 && mode === 'list' && (
        <p className="text-center py-16 text-stone text-sm">
          No clients in this session.{' '}
          <button onClick={() => setMode('login')} className="text-pine underline underline-offset-2">
            Sign in
          </button>{' '}
          or{' '}
          <button onClick={() => setMode('create')} className="text-pine underline underline-offset-2">
            create one
          </button>.
        </p>
      )}
    </div>
  )
}
