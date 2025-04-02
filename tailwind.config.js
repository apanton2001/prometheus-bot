/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          "50":"#f0fdfa",
          "100":"#ccfbf1",
          "200":"#99f6e4",
          "300":"#5eead4",
          "400":"#2dd4bf",
          "500":"#14b8a6",
          "600":"#0d9488",
          "700":"#0f766e",
          "800":"#115e59",
          "900":"#134e4a",
          "950":"#042f2e"
        },
        secondary: {
          "50":"#fffbeb",
          "100":"#fef3c7",
          "200":"#fde68a",
          "300":"#fcd34d",
          "400":"#fbbf24",
          "500":"#f59e0b",
          "600":"#d97706",
          "700":"#b45309",
          "800":"#92400e",
          "900":"#78350f",
          "950":"#451a03"
        },
      },
    },
  },
  plugins: [],
} 