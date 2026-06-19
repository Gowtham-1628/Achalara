import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/AppShell'
import { PerformancePage } from '@/features/performance/PerformancePage'
import { ClientsPage } from '@/features/clients/ClientsPage'
import { ClientDetailPage } from '@/features/clients/ClientDetailPage'
import { AccountDetailPage } from '@/features/accounts/AccountDetailPage'
import { SleeveDetailPage } from '@/features/sleeves/SleeveDetailPage'
import { StrategiesPage } from '@/features/strategies/StrategiesPage'
import { ImportsPage } from '@/features/imports/ImportsPage'
import { SettingsPage } from '@/features/SettingsPage'
import { PortfolioPage } from '@/features/PortfolioPage'
import { RiskPage } from '@/features/RiskPage'
import { GrowPage } from '@/features/GrowPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/app/performance" replace />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Navigate to="performance" replace />} />
        <Route path="performance" element={<PerformancePage />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="clients/:clientId" element={<ClientDetailPage />} />
        <Route path="clients/:clientId/accounts/:accountId" element={<AccountDetailPage />} />
        <Route path="clients/:clientId/accounts/:accountId/sleeves/:sleeveId" element={<SleeveDetailPage />} />
        <Route path="strategies" element={<StrategiesPage />} />
        <Route path="imports" element={<ImportsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="portfolio" element={<PortfolioPage />} />
        <Route path="risk" element={<RiskPage />} />
        <Route path="grow" element={<GrowPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/app/performance" replace />} />
    </Routes>
  )
}
