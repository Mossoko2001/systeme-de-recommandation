/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class', // Active le mode sombre basé sur une classe
  theme: {
    extend: {
      colors: {
        dark: '#1a202c', // Couleur de fond sombre
        blueAccent: '#3b82f6', // Accent bleu
        lightGray: '#f7fafc', // Couleur claire pour le mode clair
      },
    },
  },
  plugins: [],
};