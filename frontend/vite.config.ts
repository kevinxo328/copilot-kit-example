import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite-plus";

// https://vite.dev/config/
export default defineConfig({
  fmt: {
    singleQuote: true,
    semi: true,
    sortImports: true,
  },
  lint: { options: { typeAware: true, typeCheck: true } },
  plugins: [react(), tailwindcss()],
});
