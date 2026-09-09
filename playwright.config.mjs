import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests', testMatch:['v5_1_3_website_browser.spec.mjs','excel_model_browser.spec.mjs'], workers:1,
 webServer: process.env.TEST_BASE_URL ? undefined : {command:'node scripts/serve-static-test.mjs',url:'http://127.0.0.1:8765/vietgreen-ci-solar-project-finance/',reuseExistingServer:true},
});
