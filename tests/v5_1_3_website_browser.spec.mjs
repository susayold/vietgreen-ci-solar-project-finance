import { test, expect } from '@playwright/test';

const base = process.env.TEST_BASE_URL || 'http://127.0.0.1:8765/vietgreen-ci-solar-project-finance';
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

test('shared menu connects all eight pages and Projects onward', async ({page}) => {
 test.setTimeout(120000);
 await page.setViewportSize({width:1440,height:900});
 await page.goto(base+'/');
 for(const route of [...routes.slice(1),'/',...routes.slice(2)]){
  const nav=page.getByRole('navigation',{name:'Primary navigation'});
  await expect(nav.getByRole('link')).toHaveCount(8);
  const target=base+route;
  await nav.locator(`a[href="${new URL(target).pathname}"]`).click();
  await expect(page).toHaveURL(new RegExp(new URL(target).pathname.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'/?(?:\\?.*)?$'));
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('.vg-header')).not.toContainText('Frozen Model');
  if(route!=='/') await page.screenshot({path:`test-results/recruiter-${route.slice(1)}.png`,fullPage:true});
 }
 await page.goto(base+'/');
 await page.screenshot({path:'test-results/recruiter-overview.png',fullPage:true});
});

for (const width of [390, 768, 1440]) {
  for (const route of routes) {
    test(`current route ${route} at ${width}px`, async ({ page }) => {
      const errors = [];
      page.on('pageerror', (error) => errors.push(String(error)));
      page.on('console', (message) => {
        if (message.type() === 'error') errors.push(message.text());
      });
      await page.setViewportSize({ width, height: 900 });
      await page.goto(`${base}${route}`, {
        waitUntil: 'networkidle',
      });
      await expect(page.locator('h1')).toBeVisible();
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
  await page.goto(`${base}/economics`, { waitUntil: 'networkidle' });
  await page.locator('#economics-project').selectOption({ index: 1 });
  await expect(page).toHaveURL(/project=/);
  await page.goto(`${base}/debt`, { waitUntil: 'networkidle' });
  await page.locator('#debt-project').selectOption({ index: 1 });
  await expect(page).toHaveURL(/debt\?project=/);
  await page.goto(`${base}/risk`, { waitUntil: 'networkidle' });
  await page.locator('#risk-project').selectOption({ index: 1 });
  await expect(page).toHaveURL(/risk\?project=/);
});

test('non-default project survives handoff and reload', async ({page}) => {
  await page.goto(`${base}/economics`,{waitUntil:'networkidle'});
  await page.locator('#economics-project').selectOption({index:1});
  const id = await page.locator('#economics-project').inputValue();
  await page.getByRole('link',{name:'Continue to Debt & Credit'}).click();
  await expect(page.locator('#debt-project')).toHaveValue(id);
  await page.reload({waitUntil:'networkidle'});
  await expect(page.locator('#debt-project')).toHaveValue(id);
  await page.getByRole('link',{name:'Continue to Risk & Scenarios'}).click();
  await expect(page.locator('#risk-project')).toHaveValue(id);
});

test('all economic selections render without missing source data', async ({page}) => {
  await page.goto(`${base}/economics`,{waitUntil:'networkidle'});
  const selector=page.locator('#economics-project');
  const ids=await selector.locator('option').evaluateAll(options=>options.map(o=>o.value));
  expect(ids).toHaveLength(19);
  for (const id of ids) {
    await selector.selectOption(id);
    await expect(page.locator('.economics-kpi').first()).not.toContainText('NOT AVAILABLE');
    await expect(page.locator('h1')).toBeVisible();
  }
});
