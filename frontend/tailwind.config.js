/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Booking.com-style palette: тёмно-синий (навигация/хедер), яркий синий (CTA/акценты).
        brand: {
          50: '#eef6ff',
          100: '#dbeafe',
          200: '#a7cff8',
          400: '#2e97e6',
          500: '#0071c2', // основной CTA-синий
          600: '#005999',
          700: '#003b95', // акцентный "фирменный" синий
          800: '#00285f',
          900: '#00224f', // тёмно-навy для хедера/хиро-секции
        },
        accent: {
          500: '#febb02', // жёлтый акцент а-ля "Deal"/badge, используется точечно
          600: '#e0a400',
        },
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,0.08), 0 1px 6px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08)',
      },
      borderRadius: {
        xl2: '0.5rem', // более "квадратный", строгий стиль вместо прошлых закруглённых карточек
      },
    },
  },
  plugins: [],
};
