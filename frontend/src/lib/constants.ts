export const KNOWN_CLIENTS_KEY = 'achalara_known_clients'

export function loadKnownClients(): { id: string; name: string; email: string }[] {
  try {
    return JSON.parse(localStorage.getItem(KNOWN_CLIENTS_KEY) ?? '[]')
  } catch {
    return []
  }
}

export function saveKnownClient(client: { id: string; name: string; email: string }) {
  const existing = loadKnownClients()
  if (!existing.find((c) => c.id === client.id)) {
    localStorage.setItem(KNOWN_CLIENTS_KEY, JSON.stringify([...existing, client]))
  }
}
