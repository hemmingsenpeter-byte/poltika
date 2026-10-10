import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { expectNoAxeViolations } from "./axe";

describe("expectNoAxeViolations", () => {
  it("fails on a real violation, so a pass elsewhere means something", async () => {
    const { container } = render(<div role="img" />);
    await expect(expectNoAxeViolations(container)).rejects.toThrow();
  });
});
