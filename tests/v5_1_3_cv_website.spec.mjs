import { test, expect } from "@playwright/test";

const base = "http://127.0.0.1:4173/";
const routes = [
  ["", ["From Public Solar Data to Project Finance Decisions.", "129.853 MW", "INDETERMINATE"]],
  ["#/projects", ["20 selected projects", "441", "FPEL Arisudhana"]],
  ["#/energy", ["auditable 8,760 operating profile", "P90 generation", "166,440"]],
  ["#/economics", ["negotiation frontier", "EMPTY_NEGOTIATION_ZONE", "3,460"]],
  ["#/debt", ["Debt sized from CFADS", "1.35x", "1.377x"]],
  ["#/risk", ["Nine scenarios", "1.350x", "0.990x"]],
  ["#/diligence", ["diligence shortlist", "19", "CAPITAL ALLOCATION DISABLED"]],
  ["#/model", ["numbers can be traced", "V5.1.3", "26 Regression tests"]]
];

for (const [route, words] of routes) {
  test("route " + (route || "/") + " renders governed content", async ({ page }) => {
    const errors = [];
    page.on("console", msg => { if (msg.type() === "error") errors.push(msg.text()); });
    await page.goto(base + route, { waitUntil: "networkidle" });
    for (const word of words) await expect(page.getByText(word, { exact: false }).first()).toBeVisible();
    expect(errors).toEqual([]);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    expect(overflow).toBeFalsy();
  });
}
test("mobile navigation is keyboard accessible", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(base, { waitUntil: "networkidle" });
  const menu = page.getByRole("button", { name: /navigation/i });
  await expect(menu).toHaveAttribute("aria-expanded", "false");
  await menu.focus();
  await page.keyboard.press("Enter");
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await expect(page.getByRole("link", { name: "Projects" })).toBeVisible();
});
