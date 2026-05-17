/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        slate: {
          deep: '#F5F2EC',
          surface: '#EDEAE2',
          card: '#F5F2EC',
          border: '#D5CFC4',
          line: '#E2DDD4',
        },
        lilac: {
          DEFAULT: '#C84B2F',
          soft: '#A53D25',
          dim: '#E8A020',
          muted: '#FAE5E0',
        },
        ink: {
          DEFAULT: '#1A1410',
          muted: '#6B5F52',
          dim: '#8A7F72',
          soft: '#A89B8C',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
