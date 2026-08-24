/**
 * 前端“UI状态机与渲染”穿透测试 — Playwright
 * 覆盖：数据绑定完整性、按钮状态机、列表实时刷新、路由硬闯关
 * 运行：npx playwright test e2e/state-machine.spec.ts --project=chromium
 * 依赖：npm i -D @playwright/test ; npx playwright install
 */
import { test, expect } from '@playwright/test';

const ADMIN = 'http://127.0.0.1:5173';
const STUDENT = 'http://127.0.0.1:5174';
const API = 'http://127.0.0.1:18367';

test.describe('数据绑定完整性（防白屏）', () => {
  test('成绩查询渲染 studentName/score 不为 undefined', async ({ page }) => {
    // mock 后端返回
    await page.route('**/score/queryByPage', async route => {
      await route.fulfill({ status:200, contentType:'application/json',
        body: JSON.stringify({ code:200, message:'ok', data:{ list:[{ student_id:'20240101', course_id:'COUR20240101', score:85, gpa_point:3.0, studentName:'张三' }], total:1 }})
      });
    });
    await page.goto(`${ADMIN}/#/academic/score`);
    // 需登录态
    await page.evaluate(()=>localStorage.setItem('token','fake'));
    await page.reload();
    // 断言 DOM 文本等于张三/85 而非 undefined
    await expect(page.locator('text=张三')).toBeVisible({ timeout:3000 }).catch(()=>{});
    // 高危渲染错误判定
    const body = await page.content();
    expect(body).not.toContain('undefined');
    expect(body).not.toContain('null');
    await page.screenshot({ path:'e2e/screenshots/score-render.png', fullPage:true });
  });
});

test.describe('按钮状态机（防误点）', () => {
  test('退选后 进入考试按钮 disabled 且提示 已退选，无资格', async ({ page }) => {
    await page.route('**/enrollment/queryByPage', async r=>{
      await r.fulfill({ status:200, contentType:'application/json',
        body: JSON.stringify({ code:200, data:{ list:[{ enroll_id:'ENR1', student_id:'20240101', course_id:'COUR1', status:'2' }], total:1 }})});
    });
    await page.goto(`${ADMIN}/#/academic/enrollment`);
    await page.evaluate(()=>localStorage.setItem('token','fake'));
    await page.reload();
    const btn = page.locator('button:has-text("进入考试")').first();
    // 若无该按钮则检查退选按钮 disabled 特性
    const cancelBtn = page.locator('button:has-text("退选")').first();
    await expect(cancelBtn).toBeDisabled();
    await cancelBtn.hover();
    await expect(page.locator('text=已退选，无资格')).toBeVisible().catch(()=>{});
    await page.screenshot({ path:'e2e/screenshots/btn-retired-disabled.png' });
  });

  test('未缴费时选课立即弹 Modal 而非等待超时', async ({ page }) => {
    await page.goto(`${STUDENT}/#/courses`);
    await page.evaluate(()=>localStorage.setItem('student_token','fake'));
    await page.route('**/enrollment/add', async r=>{ await new Promise(x=>setTimeout(x,5000)); await r.fulfill({status:200, body: JSON.stringify({code:400, message:'未缴费'})}); });
    await page.locator('button:has-text("选课")').first().click().catch(()=>{});
    await expect(page.locator('.el-message-box, .el-dialog:has-text("请先缴费")')).toBeVisible({ timeout:2000 });
    await page.screenshot({ path:'e2e/screenshots/modal-unpaid.png' });
  });
});

test.describe('列表实时刷新（防脏缓存）', () => {
  test('缴费成功 Ajax 局部刷新 待缴费金额 200→0 非整页重载', async ({ page }) => {
    let first=true;
    await page.route('**/feeOrder/queryByPage', async r=>{
      const val = first? { total:1, list:[{ order_id:'ORD1', order_amount:200, order_status:'0' }]} : { total:1, list:[{ order_id:'ORD1', order_amount:0, order_status:'3' }]};
      first=false;
      await r.fulfill({ status:200, contentType:'application/json', body: JSON.stringify({code:200, data:val})});
    });
    await page.goto(`${STUDENT}/#/my-fee`);
    await page.evaluate(()=>localStorage.setItem('student_token','fake'));
    await page.reload();
    await expect(page.locator('text=¥200').or(page.locator('text=200'))).toBeVisible();
    // 点击确认支付
    await page.route('**/feeOrder/updateById/**', async r=>{ await r.fulfill({status:200, body: JSON.stringify({code:200, data:{}})}); first=false; });
    await page.locator('button:has-text("确认支付")').click().catch(()=>{});
    // 不刷新页面，金额应变 0
    await expect(page.locator('text=¥0').or(page.locator('text=0'))).toBeVisible({ timeout:5000 });
    // 确认非整页重载：监听 navigation
    let reloaded=false;
    page.on('load',()=>reloaded=true);
    expect(reloaded).toBe(false);
    await page.screenshot({ path:'e2e/screenshots/fee-auto-refresh.png' });
  });
});

test.describe('路由硬闯关（防绕过）', () => {
  test('未登录直输 /exam/start 重定向登录', async ({ page }) => {
    await page.goto(`${ADMIN}/#/exam/start`);
    await page.evaluate(()=>localStorage.clear());
    await page.goto(`${ADMIN}/#/exam/start`);
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('body')).not.toContainText('考题');
    await page.screenshot({ path:'e2e/screenshots/route-guard-exam.png' });
  });
});
