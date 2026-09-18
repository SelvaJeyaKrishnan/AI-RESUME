/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#181A2A',
          soft: '#2B2E45',
        },
        paper: {
          DEFAULT: '#F6F5F1',
          dim: '#EDEBE3',
        },
        brand: {
          50: '#EEF0F8',
          100: '#D7DBEE',
          300: '#8B95C9',
          500: '#3E4A8A',
          600: '#333F79',
          700: '#293264',
          900: '#181D3D',
        },
        amber: {
          400: '#E5A23F',
          500: '#D98E22',
          600: '#B8721A',
        },
        sage: {
          100: '#DEEBE1',
          500: '#3F8A5C',
          600: '#33714B',
        },
        rose: {
          100: '#F3DEDD',
          500: '#B8524E',
          600: '#9C433F',
        },
        line: '#E2E0D6',
        lineDark: '#3A3D55',
      },
      fontFamily: {
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
        sans: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '6px',
        md: '8px',
        lg: '12px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(24,26,42,0.06)',
        pop: '0 8px 24px rgba(24,26,42,0.12)',
      },
    },
  },
  plugins: [],
}
