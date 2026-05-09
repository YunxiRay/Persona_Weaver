/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // 护眼暖色调主题
        cream: {
          50: "#FFFDF7",
          100: "#FFF9E6",
          200: "#FFF3CC",
          300: "#FFE8A3",
          400: "#FFDA70",
          500: "#FFC83D",
          600: "#F0A825",
          700: "#CC8A1A",
          800: "#A66E14",
          900: "#805410",
        },
        sage: {
          50: "#F7F8F4",
          100: "#EDEFE6",
          200: "#DADDCC",
          300: "#C0C4A8",
          400: "#A3A884",
          500: "#888D66",
          600: "#6B704F",
          700: "#53573D",
          800: "#3C3F2D",
          900: "#282A1E",
        },
        warm: {
          50: "#FDF8F5",
          100: "#FAEEE8",
          200: "#F4D9CC",
          300: "#E8BFA8",
          400: "#D99F7E",
          500: "#C48059",
          600: "#A86542",
          700: "#884D30",
          800: "#6B3922",
          900: "#4F2817",
        },
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', '"PingFang SC"', '"Microsoft YaHei"', "sans-serif"],
        serif: ['"Noto Serif SC"', '"Source Han Serif SC"', "serif"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
