import { test, expect } from "@playwright/test";

const base = "http://127.0.0.1:4173";

async function json(page: any, path: string) {
  return page.evaluate(async (p: string) => fetch(p).then(r => r.json()), path);
}
async function visit(page: any, path: string) {
  await page.goto(\`\${base}/#\${path}\`);
  await expect(page.locator(".hero")).toHaveCount(1);
  await expect(page.locator(".hero-image")).toHaveAttribute("src", /assets/);
}
test("all eight routes render from the frozen payload layer", async ({ page }) => {
  for (const path of ["/", "/projects", "/energy", "/economics", "/debt", "/risk", "/diligence", "/model"]) {
    await visit(page, path);
    await expect(page.locator("body")).not.toContainText("Presentation data unavailable");
  }
});
test("entity, physical, economics and scenario reconciliation is visible", async ({ page }) => {
  const projects = await json(page, "data/projects.json");
  const risk = await json(page, "data/risk.json");
  const economics = await json(page, "data/economics.json");
  expect(projects.projects).toHaveLength(20);
  expect(economics.projects).toHaveLength(19);
  expect(risk.rows).toHaveLength(171);
  expect(Object.keys(risk.heatmap)).toHaveLength(19);
  expect(Object.values(projects.projects).filter((p: any) => p.physicalStatus === "LOW_YIELD_REVIEW")).toHaveLength(4);
  expect(projects.projects.find((p: any) => p.projectId === "IN-FPEL-ARISUDHANA").p50Gwh).toBeNull();
  await visit(page, "/projects");
  await expect(page.locator("tbody tr")).toHaveCount(20);
  await visit(page, "/risk");
  await expect(page.locator(".heatmap tbody tr")).toHaveCount(19);
});
test("energy chart is a real SVG line chart with exact 24-hour series", async ({ page }) => {
  const energy = await json(page, "data/energy.json");
  const featured = energy.projects[energy.featuredProjectId];
  expect(featured.representativeDay.loadKwh).toHaveLength(24);
  expect(featured.representativeDay.solarKwh).toHaveLength(24);
  await visit(page, "/energy");
  await expect(page.locator("svg polyline")).toHaveCount(4);
  const naturalWidth = await page.locator(".hero-image").evaluate((img: HTMLImageElement) => img.naturalWidth);\n  expect(naturalWidth).toBeGreaterThan(0);
});
test("model page exposes exact workbook map and source boundary", async ({ page }) => {
  const model = await json(page, "data/model.json");
  expect(model.workbookSheets).toHaveLength(28);
  expect(model.modelSha).toBe("ff69e15d211ff1abc88200574242ed2f1db49074");
  await visit(page, "/model");
  await expect(page.locator(".sheet")).toHaveCount(28);
  await expect(page.locator("body")).toContainText("PPA_FRONTIER_ONLY");
});
test("responsive screenshot baselines are captured for every target route", async ({ page }, testInfo) => {
  for (const path of ["/", "/projects", "/energy", "/economics", "/debt", "/risk", "/diligence", "/model"]) {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(\`\${base}/#\${path}\`);
    await page.screenshot({ path: testInfo.outputPath(\`\${path.slice(1) || "overview"}-1440.png\`), fullPage: true });
  }
  for (const path of ["/", "/economics", "/risk"]) {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(\`\${base}/#\${path}\`);
    await page.screenshot({ path: testInfo.outputPath(\`\${path.slice(1) || "overview"}-390.png\`), fullPage: true });
  }
});
