import { loadKnownClients } from '@/lib/constants'

export function SettingsPage() {
  const clients = loadKnownClients()

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-2xl text-summit-ink">Settings</h1>
        <p className="text-stone text-sm mt-1">Platform configuration.</p>
      </div>

      <section className="border border-stone/20 rounded-card p-6">
        <h2 className="text-sm font-mono uppercase tracking-wide text-stone mb-4">Known clients</h2>
        <p className="text-xs text-stone mb-3">
          Clients you've created in this browser session. Locally cached until a list-all endpoint is available.
        </p>
        {clients.length ? (
          <ul className="space-y-2">
            {clients.map((c) => (
              <li key={c.id} className="text-sm font-mono text-stone">
                <span className="text-summit-ink">{c.name}</span> — {c.id}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-stone text-sm">No clients cached.</p>
        )}
      </section>

      <section className="border border-stone/20 rounded-card p-6 opacity-60">
        <h2 className="text-sm font-mono uppercase tracking-wide text-stone mb-2">Authentication</h2>
        <p className="text-sm text-stone">
          Single-user mode. Auth configuration will appear here when multi-user login is available.
          {/* BACKEND_GAP: auth — see BACKEND_GAPS.md */}
        </p>
      </section>
    </div>
  )
}
