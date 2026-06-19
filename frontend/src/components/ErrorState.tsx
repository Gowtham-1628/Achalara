interface Props { message: string; onRetry?: () => void }

export function ErrorState({ message, onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <p className="text-loss font-medium mb-2">Something went wrong</p>
      <p className="text-stone text-sm max-w-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 border border-stone text-stone text-sm rounded-btn hover:border-summit-ink hover:text-summit-ink transition-colors"
        >
          Try again
        </button>
      )}
    </div>
  )
}
