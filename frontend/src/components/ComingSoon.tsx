interface Props { feature: string; description: string }

export function ComingSoon({ feature, description }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center px-8">
      <span className="text-xs font-mono tracking-widest text-gold uppercase mb-4">
        Coming soon
      </span>
      <h2 className="font-display text-2xl text-summit-ink mb-3">{feature}</h2>
      <p className="text-stone text-sm max-w-md leading-relaxed">{description}</p>
    </div>
  )
}
