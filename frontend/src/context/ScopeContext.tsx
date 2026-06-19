import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

export type ScopeLevel = 'client' | 'account' | 'sleeve' | 'strategy'

export interface Scope {
  level: ScopeLevel | null
  clientId: string | null
  accountId: string | null
  sleeveId: string | null
  strategyId: string | null
  clientName: string | null
  accountName: string | null
  sleeveName: string | null
  strategyName: string | null
}

interface ScopeCtx {
  scope: Scope
  setClient: (id: string, name: string) => void
  setAccount: (id: string, name: string) => void
  setSleeve: (id: string, name: string) => void
  setStrategy: (id: string, name: string) => void
  clearScope: () => void
}

const empty: Scope = {
  level: null, clientId: null, accountId: null, sleeveId: null, strategyId: null,
  clientName: null, accountName: null, sleeveName: null, strategyName: null,
}

const STORAGE_KEY = 'achalara.scope'

function loadScope(): Scope {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as Scope
  } catch {}
  return empty
}

const ScopeContext = createContext<ScopeCtx | null>(null)

export function ScopeProvider({ children }: { children: ReactNode }) {
  const [scope, setScope] = useState<Scope>(loadScope)

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(scope))
  }, [scope])

  const setClient = (id: string, name: string) =>
    setScope({ ...empty, level: 'client', clientId: id, clientName: name })

  const setAccount = (id: string, name: string) =>
    setScope((s) => ({ ...s, level: 'account', accountId: id, accountName: name, sleeveId: null, sleeveName: null }))

  const setSleeve = (id: string, name: string) =>
    setScope((s) => ({ ...s, level: 'sleeve', sleeveId: id, sleeveName: name }))

  const setStrategy = (id: string, name: string) =>
    setScope({ ...empty, level: 'strategy', strategyId: id, strategyName: name })

  const clearScope = () => setScope(empty)

  return (
    <ScopeContext.Provider value={{ scope, setClient, setAccount, setSleeve, setStrategy, clearScope }}>
      {children}
    </ScopeContext.Provider>
  )
}

export function useScope() {
  const ctx = useContext(ScopeContext)
  if (!ctx) throw new Error('useScope must be used within ScopeProvider')
  return ctx
}
