/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        academic: {
          50: '#f0f5ff',
          100: '#e0ecff',
          200: '#c5dcff',
          300: '#9bc4ff',
          400: '#69a0ff',
          500: '#3b78f6',
          600: '#255beb',
          700: '#1d45d8',
          800: '#1e38af',
          900: '#1e328a',
          950: '#0b132b',
        },
        navy: {
          800: '#151e2e',
          850: '#0f172a',
          900: '#0a0f1d',
          950: '#060913',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Merriweather', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
