import jsxA11y from "eslint-plugin-jsx-a11y";
import { FlatCompat } from "@eslint/eslintrc";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const compat = new FlatCompat({ baseDirectory: dirname(fileURLToPath(import.meta.url)) });

const config = [
  { ignores: [".next/**", "out/**", "src/api/schema.gen.ts"] },
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    // The full jsx-a11y recommended set (B0.1.6); next/core-web-vitals only
    // enables a few of its rules. The plugin is already registered by
    // eslint-config-next, so only the rules are added.
    files: ["src/**/*.{ts,tsx}"],
    rules: jsxA11y.flatConfigs.recommended.rules,
  },
  {
    // Components reach the API only through services (ADR-0023).
    files: ["src/components/**", "src/features/**", "src/app/**"],
    rules: {
      "no-restricted-globals": ["error", { name: "fetch", message: "Call a service in src/api/services." }],
    },
  },
];

export default config;
