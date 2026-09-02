import { test, expect } from "@playwright/test";

const routes = ["/#/","/#/case","/#/economics","/#/debt","/#/portfolio","/#/risk","/#/model","/#/evidence"];

for (const width of [390, 430, 768, 1024, 1440]) {
  for (const route of routes) {
    test("route "+route+" at "+width+"px", async ({ page }) => {
      const errors = [];
      page.on("pageerror", e => errors.push(String(e)));
      page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
      await page.setViewportSize({ width, height: 900 });
      await page.goto("http://127.0.0.1:8765"+route, { waitUntil: "networkidle" });
      await expect(page.locator("main#app")).not.toBeEmpty();
      expect(errors, route+" console errors").toEqual([]);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBeTruthy();
    });
  }
}

test("mobile navigation is keyboard accessible", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("http://127.0.0.1:8765/#/", { waitUntil: "networkidle" });
  const menu=page.locator(".mobile-menu");
  await expect(menu).toBeVisible();
  await menu.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".main-nav")).toHaveClass(/open/);
});

test("project selectors change route state", async ({ page }) => {
  await page.goto("http://127.0.0.1:8765/#/economics", { waitUntil: "networkidle" });
  await page.locator("#econ-project-select").selectOption({ index: 1 });
  await expect(page).toHaveURL(/project=/);
  await page.goto("http://127.0.0.1:8765/#/debt", { waitUntil: "networkidle" });
  await page.locator("#debt-project-select").selectOption({ index: 1 });
  await expect(page).toHaveURL(/debt\?project=/);
  await page.goto("http://127.0.0.1:8765/#/risk", { waitUntil: "networkidle" });
  await page.locator("#risk-project-select").selectOption({ index: 1 });
  await expect(page).toHaveURL(/risk\?project=/);
});
