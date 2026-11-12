/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#0B1A2E",
        teal: {
          DEFAULT: "#00897B",
          light: "#33A095"
        },
        cyan: "#00BCD4",
        coral: "#E2725B",
        offwhite: "#F7FAFA",
        "severity-normal": "#10B981",
        "severity-mild": "#F59E0B",
        "severity-moderate": "#E2725B",
        "severity-severe": "#EF4444",
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%)',
      }
    },
  },
  plugins: [],
}
