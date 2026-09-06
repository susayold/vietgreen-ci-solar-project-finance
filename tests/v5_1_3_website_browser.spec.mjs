import { test, expect } from '@playwright/test';

const routes = [
  '/',
  '/projects',
  '/energy',
  '/economics',
  '/debt',
  '/risk',
  '/diligence',
  '/model-evidence',
];

for (const width of [390, 768, 1440]) {
  for (const route of routes) {
    test(`current route ${route} at ${width}px`, async ({ page }) => {
      const errors = [];
      page.on('pageerror', (error) => errors.push(String(error)));
      page.on('console', (message) => {
        if (message.type() === 'error') errors.push(message.text());
      });
      await page.setViewportSize({ width, height: 900 });
      await page.goto(`http://127.0.0.1:8765${route}`, {
        waitUntil: 'networkidle',
      });
      await expect(page.locator('main')).not.toBeEmpty();
      expect(errors, `${route} console errors`).toEqual([]);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth + 1,
        ),
      ).toBeTruthy();
    });
  }
}

test('project selectors change query-string state', async ({ page }) => {
  await page.goto('http://127.0.0.1:8765/economics', { waitUntil: 'networkidle' });
  await page.locator('#economics-project').selectOption({ index: 1 });
  await expect(page).toHaveURL(/project=/);
  await page.goto('http://127.0.0.1:8765/debt', { waitUntil: 'networkidle' });
  await page.locator('#debt-project').selectOption({ index: 1 });
  await expect(page).toHaveURL(/debt\?project=/);
  await page.goto('http://127.0.0.1:8765/risk', { waitUntil: 'networkidle' });
  await page.locator('#risk-project').selectOption({ index: 1 });
  await expect(page).toHaveURL(/risk\?project=/);
});
