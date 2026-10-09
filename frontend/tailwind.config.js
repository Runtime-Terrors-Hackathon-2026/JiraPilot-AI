/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: 'var(--jp-canvas)',
        surface: 'var(--jp-surface)',
        'surface-2': 'var(--jp-surface-2)',
        line: 'var(--jp-line)',
        ink: 'var(--jp-ink)',
        muted: 'var(--jp-muted)',
        accent: 'var(--jp-accent)',
        'accent-soft': 'var(--jp-accent-soft)',
        teal: 'var(--jp-teal)',
        'teal-soft': 'var(--jp-teal-soft)',
        amber: 'var(--jp-amber)',
        'amber-soft': 'var(--jp-amber-soft)',
        danger: 'var(--jp-danger)',
        'danger-soft': 'var(--jp-danger-soft)',
        log: 'var(--jp-log)',
        'log-ink': 'var(--jp-log-ink)',
      },
      boxShadow: {
        panel: 'var(--jp-shadow)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'ui-monospace', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 180ms ease-out',
        'pulse-soft': 'pulseSoft 1.8s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.45' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
