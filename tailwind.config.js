/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                serif: ['Georgia', 'Cambria', '"Times New Roman"', 'serif'],
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            colors: {
                museum: {
                    bg: '#fcfbf7',
                    darkBg: '#0f0f11',
                    surface: '#ffffff',
                    darkSurface: '#18181c',
                    accent: '#b85d19',
                    gold: '#c29b38'
                }
            }
        },
    },
    plugins: [],
};