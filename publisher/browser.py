from __future__ import annotations

import asyncio
import getpass
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from .content import Blocked, Chapter, DailyQuota, normalized


class Fanqie:
    def __init__(self, data: Path, book: str, title: str, config: dict):
        if not re.fullmatch(r"\d+", book) or not title:
            raise Blocked("请配置 FANQIE_BOOK_ID 和 FANQIE_BOOK_TITLE")
        self.data, self.book, self.title, self.config = data, book, title, config
        self.ui = config["ui"]
        self.home = "https://fanqienovel.com/main/writer/book-manage"
        self.state = data / "storage-state.json"

    async def __aenter__(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            storage_state=str(self.state) if self.state.exists() else None,
            locale="zh-CN", timezone_id="Asia/Shanghai", viewport={"width": 1440, "height": 1000},
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(15000)
        return self

    async def __aexit__(self, kind, error, tb):
        if error:
            try:
                await self.page.screenshot(path=str(self.data / "last-error.png"), full_page=True,
                    mask=[self.page.get_by_placeholder("手机号", exact=True),
                          self.page.get_by_placeholder("请输入验证码", exact=True)])
            except Exception:
                pass
        await self.context.close()
        await self.browser.close()
        await self.pw.stop()

    async def save_session(self):
        temporary = self.state.with_suffix(".tmp")
        await self.context.storage_state(path=str(temporary))
        temporary.chmod(0o600)
        temporary.replace(self.state)

    async def authenticated(self):
        # The observed identifier may be a test attribute instead of a DOM id.
        link = self.page.locator(f'a[href*="/chapter-manage/{self.book}&"]')
        if await link.count() == 1 and await link.is_visible():
            self.manage_url = await link.get_attribute("href")
            if self.manage_url.startswith("/"):
                self.manage_url = "https://fanqienovel.com" + self.manage_url
            self.assert_url(self.manage_url, manage=True)
            return True
        return False

    async def login(self, interactive=False):
        await self.page.goto(self.home, wait_until="domcontentloaded")
        timeout = self.config["login_timeout_seconds"] if interactive else 20
        deadline = time.monotonic() + timeout
        clicked = set()
        while time.monotonic() < deadline:
            if urlparse(self.page.url).path in {"/main/writer", "/main/writer/"}:
                await self.page.goto(self.home, wait_until="domcontentloaded")
            if await self.authenticated():
                await self.save_session()
                return
            if interactive:
                refresh = self.page.get_by_text("点击刷新", exact=True)
                if await refresh.count() == 1 and await refresh.is_visible():
                    await refresh.click()
                for label in self.ui["login_labels"]:
                    locator = self.page.get_by_text(label, exact=True)
                    if label not in clicked and await locator.count() == 1 and await locator.is_visible():
                        await locator.click()
                        clicked.add(label)
                # Refresh screenshot atomically so scp never reads half an image.
                shot = self.data / "login.tmp.png"
                await self.page.screenshot(path=str(shot))
                shot.replace(self.data / "login.png")
            await asyncio.sleep(2)
        raise Blocked("登录未完成或目标作品不可见；运行 login，查看 /data/login.png 扫码；验证码/实名需本人完成")

    async def login_sms(self):
        await self.page.goto(self.home, wait_until="domcontentloaded")
        await self.page.get_by_text("验证码登录", exact=True).click()
        phone = await asyncio.to_thread(getpass.getpass, "番茄账号手机号（隐藏输入）: ")
        if not re.fullmatch(r"1\d{10}", phone):
            raise Blocked("当前番茄表单仅适配中国大陆 11 位手机号")
        await self.page.get_by_placeholder("手机号", exact=True).fill(phone)
        # Agreement is an explicit operator action, never silently preselected.
        consent = await asyncio.to_thread(input, "番茄要求同意《用户协议》和《隐私政策》。本次同意请输入 AGREE，否则退出: ")
        if consent.strip() != "AGREE":
            raise Blocked("未同意登录协议，已停止")
        checkbox = self.page.locator('input[type="checkbox"]')
        if not await checkbox.is_checked():
            await self.page.locator('label.arco-checkbox').click()
        if not await checkbox.is_checked():
            raise Blocked("协议复选框未选中，未发送短信")
        await self.page.get_by_text("获取验证码", exact=True).click()
        while True:
            await asyncio.sleep(2)
            texts = []
            for frame in self.page.frames:
                try:
                    texts.append(await frame.locator('body').inner_text(timeout=2000))
                except Exception:
                    pass
            text = '\n'.join(texts)
            if '请完成下列验证' in text or '拖动完成' in text:
                print('等待人工滑块验证，短信尚未确认发送。截图：/data/sms-login.png', flush=True)
            elif re.search(r'重新获取|重新发送|\d+\s*[s秒]', text):
                print('页面显示短信倒计时，请查看手机。', flush=True)
            else:
                print('短信发送状态未确认，请查看 /data/sms-login.png。', flush=True)
            await self.page.screenshot(path=str(self.data / "sms-login.png"),
                                      mask=[self.page.get_by_placeholder("手机号", exact=True),
                                            self.page.get_by_placeholder("请输入验证码", exact=True)])
            code = await asyncio.to_thread(getpass.getpass,
                "输入已收到的短信验证码；/refresh 更新截图；人工拖动可输入 /drag x1 y1 x2 y2；回车退出（隐藏输入）: ")
            if code == '/refresh':
                continue
            if code.startswith('/drag '):
                values = code.split()[1:]
                if len(values) != 4 or any(not re.fullmatch(r'\d{1,4}', v) for v in values):
                    raise Blocked('拖动格式应为 /drag x1 y1 x2 y2')
                x1, y1, x2, y2 = map(int, values)
                if max(x1, x2) >= 1440 or max(y1, y2) >= 1000:
                    raise Blocked('拖动坐标超出截图范围')
                # Only explicit interactive operator input, no automatic CAPTCHA solver.
                await self.page.mouse.move(x1, y1)
                await self.page.mouse.down()
                for step in range(1, 31):
                    await self.page.mouse.move(x1 + (x2-x1)*step/30, y1 + (y2-y1)*step/30)
                    await asyncio.sleep(0.05)
                await self.page.mouse.up()
                continue
            if not re.fullmatch(r"\d{4,8}", code):
                raise Blocked("未输入有效验证码；检查 /data/sms-login.png，必要时本人处理验证")
            break
        await self.page.get_by_placeholder("请输入验证码", exact=True).fill(code)
        await self.page.get_by_role("button", name="登录/注册", exact=True).click()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if urlparse(self.page.url).path in {"/main/writer", "/main/writer/"}:
                await self.page.goto(self.home, wait_until="domcontentloaded")
            if await self.authenticated():
                await self.save_session()
                return
            await asyncio.sleep(1)
        raise Blocked("短信登录未通过或目标作品不可见；检查 /data/last-error.png")

    def assert_url(self, url: str, manage=False):
        parsed = urlparse(url)
        prefix = f"/main/writer/chapter-manage/{self.book}&" if manage else f"/main/writer/{self.book}/publish/"
        if parsed.scheme != "https" or parsed.netloc != "fanqienovel.com" or not parsed.path.startswith(prefix):
            raise Blocked("页面作品 ID 或域名不匹配")

    async def listing(self, draft=False):
        await self.page.goto(self.manage_url, wait_until="domcontentloaded")
        await self.page.wait_for_load_state('networkidle')
        await self.page.get_by_text(self.title, exact=False).wait_for(state="visible")
        notice = self.page.get_by_role('button', name='我知道了', exact=True)
        if await notice.count() == 1 and await notice.is_visible():
            await notice.click()
        if draft:
            await self.page.get_by_role("tab", name="草稿箱", exact=True).click()
            await self.page.get_by_role('link', name='新建草稿', exact=True).wait_for(state='visible')
            await self.page.wait_for_load_state('networkidle')
        self.panel = self.page.locator('[role="tabpanel"]:not([aria-hidden="true"])')
        await self.panel.wait_for(state='visible')
        empty = (self.panel.get_by_text(re.compile(r'^共\s*0\s*篇草稿$')) if draft else
                 self.panel.get_by_text(self.ui["empty_text"], exact=True))
        await self.panel.locator(self.ui["rows"]).or_(empty
        ).first.wait_for(state="visible")
        self.assert_url(self.page.url, manage=True)

    async def rows(self):
        """Enumerate all pages, abort on unknown pagination or stalled pages."""
        seen = set()
        for _ in range(1000):
            rows = self.panel.locator(self.ui["rows"]).filter(visible=True)
            texts = await rows.all_inner_texts()
            fingerprint = tuple(texts)
            if fingerprint in seen:
                raise Blocked("章节分页未前进，无法证明不存在重复")
            seen.add(fingerprint)
            for row in await rows.all():
                yield row
            next_button = self.panel.locator(self.ui["next_page"]).filter(visible=True)
            if await next_button.count() == 0:
                # If a pagination control exists but its next button changed, fail closed.
                if await self.panel.locator('[class*="pagination"]').filter(visible=True).count():
                    raise Blocked("未知分页控件，请更新 next_page 选择器")
                return
            if await next_button.count() != 1:
                raise Blocked("分页按钮不唯一")
            classes = await next_button.get_attribute("class") or ""
            if "disabled" in classes or await next_button.get_attribute("aria-disabled") == "true" or not await next_button.is_enabled():
                return
            await next_button.click()
            for _ in range(30):
                if tuple(await rows.all_inner_texts()) != fingerprint:
                    break
                await asyncio.sleep(0.2)
            else:
                raise Blocked("分页超时")
        raise Blocked("章节分页超出限制")

    async def row_identity(self, row):
        title = row.locator('.table-title')
        if await title.count() != 1:
            title = row.locator('td').first
        text = (await title.inner_text()).strip()
        match = re.fullmatch(r'第\s*(\d+)\s*章\s*(.+)', text)
        return (int(match[1]), match[2].strip()) if match else (None, text)

    async def duplicate_check(self, chapter: Chapter):
        for draft in (False, True):
            await self.listing(draft)
            async for row in self.rows():
                number, title = await self.row_identity(row)
                if number == chapter.number or title == chapter.title:
                    raise Blocked(f"后台已有同号/同名章节（含草稿），请人工核对第 {chapter.number} 章")

    async def create(self):
        await self.listing()
        link = self.page.get_by_role("link", name="新建章节", exact=True)
        href = await link.get_attribute("href")
        if href.startswith("/"):
            href = "https://fanqienovel.com" + href
        self.assert_url(href)
        await self.page.goto(href, wait_until="domcontentloaded")
        await self.page.wait_for_url(re.compile(rf'^https://fanqienovel\.com/main/writer/{self.book}/publish/\d+(?:[/?]|$)'))
        await self.page.locator(self.ui["title"]).wait_for(state="visible")
        self.assert_url(self.page.url)
        if not re.search(r"/publish/\d+", self.page.url):
            raise Blocked("新章节未分配远端 ID")
        return self.page.url

    async def fill(self, chapter: Chapter):
        await self.page.wait_for_load_state('networkidle')
        await self.page.locator(self.ui["number"]).fill(str(chapter.number))
        await self.page.locator(self.ui["title"]).fill(chapter.title)
        body = self.page.locator(self.ui["body"])
        await body.click()
        await body.press('ControlOrMeta+A')
        await body.press('Backspace')
        for index, paragraph in enumerate(re.split(r'\n\s*\n', chapter.body)):
            if index:
                await self.page.keyboard.press('Enter')
            await self.page.keyboard.insert_text(paragraph)
        await self.check_editor(chapter)

    async def check_editor(self, chapter: Chapter):
        self.assert_url(self.page.url)
        if await self.page.locator(self.ui["number"]).input_value() != str(chapter.number):
            raise Blocked("远端章节号不一致")
        if await self.page.locator(self.ui["title"]).input_value() != chapter.title:
            raise Blocked("远端章节标题不一致")
        if normalized(await self.page.locator(self.ui["body"]).inner_text()) != normalized(chapter.body):
            raise Blocked("远端正文与本地不一致")

    async def submit(self):
        for step in self.ui["publish_steps"]:
            if 'selector' in step:
                locator = self.page.locator(step['selector'])
            elif step.get('name') == '提交':
                # Typo warnings render a second Submit button in a dialog.
                # Use it when present, while keeping fixture/older-page support.
                dialog_locator = self.page.locator('[role="dialog"]').get_by_role(
                    step['role'], name=step['name'], exact=True)
                locator = dialog_locator if await dialog_locator.count() else self.page.get_by_role(
                    step['role'], name=step['name'], exact=True)
            elif 'text' in step:
                locator = self.page.get_by_text(step['text'], exact=True).filter(visible=True)
            else:
                locator = self.page.get_by_role(step["role"], name=step["name"], exact=True)
            if step.get('optional'):
                try:
                    await locator.wait_for(state='visible', timeout=5000)
                except Exception:
                    if await locator.count() == 0 or not await locator.is_visible():
                        continue
                    raise
            await locator.click()
        quota = self.page.get_by_text('提交字数超出每日上限', exact=True)
        try:
            await quota.wait_for(state='visible', timeout=2000)
        except Exception:
            return
        # Preserve the existing editor before closing the browser on rejection.
        await self.page.get_by_role('button', name='取消', exact=True).click()
        await self.page.get_by_role('button', name='存草稿', exact=True).click()
        await self.page.get_by_text('保存成功', exact=True).wait_for(state='visible')
        raise DailyQuota('番茄提交字数超出每日上限；已保存原章节，次日定时恢复')

    async def resume_deferred(self, chapter: Chapter, url: str) -> bool:
        """Only used for a recorded explicit quota rejection, never unknown submissions."""
        self.assert_url(url)
        await self.listing()
        async for row in self.rows():
            number, title = await self.row_identity(row)
            if number == chapter.number or title == chapter.title:
                return False  # May have been published manually: verify instead.
        await self.page.goto(url, wait_until='domcontentloaded')
        await self.page.wait_for_load_state('networkidle')
        await self.check_editor(chapter)
        return True

    async def verify(self, chapter: Chapter, url: str) -> str:
        self.assert_url(url)
        remote_id = re.search(r"/publish/(\d+)", url)[1]
        deadline = time.monotonic() + self.config["verification_timeout_seconds"]
        while time.monotonic() < deadline:
            await self.listing()
            async for row in self.rows():
                text = await row.inner_text()
                if not re.search(rf"第\s*{chapter.number}\s*章", text) or chapter.title not in text:
                    continue
                link = row.locator(f'a[href*="/publish/{remote_id}"]')
                preview = row.locator(f'a[href="/main/writer/preview/{self.book}&{remote_id}"]')
                if await link.count() != 1 and await preview.count() != 1:
                    raise Blocked("同号/同名行远端 ID 不一致，禁止归档")
                if any(s in text for s in self.ui["rejected_statuses"]):
                    raise Blocked("番茄审核未通过，请人工处理")
                if any(s in text for s in self.ui["published_statuses"]):
                    await self.page.goto(url, wait_until="domcontentloaded")
                    await self.page.wait_for_load_state('networkidle')
                    await self.page.locator(self.ui["body"]).wait_for(state="visible")
                    await self.check_editor(chapter)
                    return "published"
                if any(s in text for s in self.ui["pending_statuses"]):
                    return "pending"
            await asyncio.sleep(3)
        raise Blocked("未能核验已发布状态；保留 ready 和事务记录，禁止自动重发")
