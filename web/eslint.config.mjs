import { FlatCompat } from "@eslint/eslintrc";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const compat = new FlatCompat({ baseDirectory: dirname(fileURLToPath(import.meta.url)) });

const config = [
  { ignores: [".next/**", "out/**", "src/api/schema.gen.ts"] },
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    // Components reach the API only through services (ADR-0023).
    files: ["src/components/**", "src/features/**", "src/app/**"],
    rules: {
      "no-restricted-globals": ["error", { name: "fetch", message: "Call a service in src/api/services." }],
    },
  },
];

export default config;
