export default {
    content: ["./index.html", "./src/**/*.{ts,tsx}"],
    theme: {
        extend: {
            colors: {
                ink: "#0f1728",
                mist: "#eef3f7",
                cloud: "#f8fbfd",
                accent: "#0b7285",
                accentSoft: "#dff5f8",
                warning: "#c2410c",
            },
            fontFamily: {
                sans: ["Manrope", "Segoe UI", "sans-serif"],
                display: ["Fraunces", "Georgia", "serif"],
            },
            boxShadow: {
                panel: "0 24px 80px rgba(15, 23, 40, 0.12)",
            },
            backgroundImage: {
                "app-gradient": "radial-gradient(circle at top left, rgba(11,114,133,0.16), transparent 30%), radial-gradient(circle at top right, rgba(58,130,113,0.12), transparent 24%), linear-gradient(180deg, #f8fbfd 0%, #edf4f7 100%)",
            },
        },
    },
    plugins: [],
};
