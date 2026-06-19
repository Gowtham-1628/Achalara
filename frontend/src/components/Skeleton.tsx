export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-mist rounded ${className}`} />
  )
}

export function SkeletonCard() {
  return (
    <div className="border border-stone/20 rounded-card p-6 space-y-3">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-8 w-40" />
      <Skeleton className="h-3 w-32" />
    </div>
  )
}
