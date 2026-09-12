import { test, expect } from '@playwright/test';

const base = process.env.TEST_BASE_URL || 'http://127.0.0.1:8765/vietgreen-ci-solar-project-finance';

test('Excel model shortcut opens the recruiter workbook showcase', async ({ page, request }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`${base}/`, { waitUntil: 'domcontentloaded' });
  const shortcut = page.getByRole('link', { name: 'Excel Model' });
  await expect(shortcut).toBeVisible();
  await shortcut.click();
  await expect(page).toHaveURL(/\/excel-model\/?$/);
  await expect(page.locator('h1')).toContainText('Open the Workbook');
  await expect(page.locator('#workbook-viewer iframe')).toHaveAttribute('src', /view\.officeapps\.live\.com/);
  await expect(page.getByRole('link', { name: /Download Excel/i })).toHaveAttribute(
    'href',
    /\/downloads\/vietgreen_core_model\.xlsx(?:\?v=[0-9a-f]{40})?$/,
  );

  const workbook = await request.get(`${base}/downloads/vietgreen_core_model.xlsx`);
  expect(workbook.ok()).toBeTruthy();
  expect((await workbook.body()).byteLength).toBeGreaterThan(100_000);
});

test('Excel model walkthrough reconciles to current V5.1.3 economics and debt data', async ({ page, request }) => {
  const economics = await (await request.get(`${base}/data/economics.json`)).json();
  const debt = await (await request.get(`${base}/data/debt.json`)).json();
  const goEcon = economics.rows.find((row) => row.projectId === 'VN-GY-GOMALL');
  const goDebt = debt.rows.find((row) => row.projectId === 'VN-GY-GOMALL');

  await page.goto(`${base}/excel-model`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#excel-project')).toBeEnabled();
  await expect(page.locator('.excel-kpis')).toContainText(`$${(goEcon.capexUsd / 1_000_000).toFixed(3)}m`);
  await expect(page.locator('.excel-kpis')).toContainText(`$${(goDebt.debtCapacityUsd / 1_000_000).toFixed(3)}m`);
  await expect(page.locator('.excel-kpis')).toContainText(`${goDebt.minimumDscr.toFixed(3)}x`);

  await page.getByRole('button', { name: 'Debt Sizing' }).click();
  await expect(page.locator('.excel-formula-card')).toContainText('Debt_final = MIN');
  await expect(page.locator('.excel-formula-card')).toContainText('independent credit constraints');

  await page.getByRole('button', { name: 'Debt Schedule' }).click();
  const activeSchedule = goDebt.schedule.filter((row) => row.openingDebt !== 0 || row.debtService !== 0 || row.closingDebt !== 0);
  await expect(page.locator('.excel-sheet-body tbody tr')).toHaveCount(activeSchedule.length);
});

test('Excel model project selector and learning section are recruiter-ready', async ({ page }) => {
  await page.goto(`${base}/excel-model`, { waitUntil: 'domcontentloaded' });
  const selector = page.locator('#excel-project');
  await expect(selector).toBeEnabled();
  const options = await selector.locator('option').count();
  expect(options).toBe(19);
  await selector.selectOption({ index: 1 });
  await expect(page).toHaveURL(/excel-model\?project=/);
  await expect(page.locator('.excel-skills-grid')).toContainText('Financial Modeling');
  await expect(page.locator('.excel-skills-grid')).toContainText('Debt Sizing & Sculpting');
  await expect(page.locator('.excel-learning-section')).toContainText('What I learned');
  await expect(page.locator('.excel-learning-section')).toContainText('What I can contribute');
});

test('Excel model page contains no viewport overflow at recruiter breakpoints', async ({ page }) => {
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`${base}/excel-model`, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('h1')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBeTruthy();
  }
});
