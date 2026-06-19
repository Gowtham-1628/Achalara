import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'summit-ink': '#14201C',
        'pine-deep': '#1E3A2F',
        'pine': '#2F5D4A',
        'mist': '#EAF0EC',
        'paper': '#FBFCFB',
        'stone': '#8A968F',
        'gain': '#2E8B6B',
        'loss': '#C2703D',
        'gold': '#C9A24B',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'Menlo', 'monospace'],
      },
      borderRadius: {
        card: '10px',
        btn: '8px',
      },
      spacing: {
        '4': '4px',
        '8': '8px',
        '12': '12px',
        '16': '16px',
        '24': '24px',
        '32': '32px',
        '48': '48px',
        '64': '64px',
        '96': '96px',
      },
    },
  },
  plugins: [],
} satisfies Config
