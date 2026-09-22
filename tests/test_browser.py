"""Real headless Chromium, all HTTP requests fulfilled by local HTML fixtures."""
import os
from dataclasses import replace
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import yaml

from publisher.browser import Fanqie
from publisher.content import Blocked, Chapter


@unittest.skipUnless(os.getenv('RUN_BROWSER_TESTS') == '1', 'Set RUN_BROWSER_TESTS=1 with Chromium installed')
class BrowserTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = yaml.safe_load(Path('config/publisher.yaml').read_text(encoding='utf-8'))
        self.site = Fanqie(Path(self.temp.name), '123', '测试作品', self.config)
        await self.site.__aenter__()
        self.site.manage_url = 'https://fanqienovel.com/main/writer/chapter-manage/123&test?type=1'
        self.url = 'https://fanqienovel.com/main/writer/123/publish/456'
        self.chapter = Chapter(Path('unused'), 1, '门后的脚步', '她听见脚步。', '', 'hash')
        self.editor = '''<input class="serial-input" value="1">
        <input placeholder="请输入标题" value="门后的脚步">
        <div class="syl-editor-container"><div class="syl-editor"><div class="ProseMirror" contenteditable="true">她听见脚步。</div></div></div>
        <div class="outline-editor"><div class="syl-editor"><div class="ProseMirror" contenteditable="true">秘密大纲</div></div></div>'''
        self.list_html = f'<div>测试作品</div><table><tbody><tr><td>第1章 门后的脚步 已发布</td><td><a href="{self.url}">编辑</a></td></tr></tbody></table>'
        async def route(request):
            html = self.editor if '/publish/' in request.request.url else '<div role="tabpanel">' + self.list_html + '</div>'
            await request.fulfill(status=200, content_type='text/html; charset=utf-8', body=html)
        await self.site.context.route('**/*', route)

    async def asyncTearDown(self):
        await self.site.__aexit__(None, None, None)
        self.temp.cleanup()

    async def test_only_prose_editor_filled(self):
        await self.site.page.goto(self.url)
        await self.site.fill(self.chapter)
        self.assertEqual(await self.site.page.locator('.outline-editor').inner_text(), '秘密大纲')

    async def test_multiline_prose_is_not_truncated(self):
        await self.site.page.goto(self.url)
        chapter = replace(self.chapter, body='第一段。\n\n第二段。\n\n最后一段。')
        await self.site.fill(chapter)
        await self.site.check_editor(chapter)
        self.assertEqual(await self.site.page.locator('.outline-editor').inner_text(), '秘密大纲')

    async def test_publish_dialog_sequence(self):
        await self.site.page.set_content('''<button>下一步</button><button data-apm-action="core_chain_long_story_next_confirm" onclick="this.remove();document.querySelector('#typo').hidden=false">下一步</button>
          <button id="typo" hidden onclick="this.remove();document.querySelector('#check').hidden=false">提交</button>
          <button id="check" hidden onclick="this.remove();document.querySelector('#settings').hidden=false">仅基础检测</button>
          <div id="settings" hidden><label><input type="radio">是</label>
          <button onclick="if(document.querySelector('input').checked){document.body.textContent='已提交'}">确认发布</button></div>''')
        await self.site.submit()
        self.assertEqual(await self.site.page.locator('body').inner_text(), '已提交')

    async def test_typo_warning_clicks_dialog_submit(self):
        await self.site.page.set_content('''<button>提交</button>
          <div role="dialog"><div>发布提示</div><div>检测到你还有错别字未修改，是否确定提交？</div>
          <button>取消</button><button onclick="this.parentElement.remove();document.body.insertAdjacentHTML('beforeend','<span>继续</span>')">提交</button></div>''')
        step = {'role':'button', 'name':'提交'}
        locator = self.site.page.locator('[role="dialog"]').get_by_role(step['role'], name=step['name'], exact=True)
        await locator.click()
        self.assertEqual(' '.join((await self.site.page.locator('body').inner_text()).split()), '提交 继续')

    async def test_login_follows_workbench_redirect(self):
        calls = 0
        async def route(request):
            nonlocal calls
            if request.request.url == self.site.home:
                calls += 1
                if calls == 1:
                    await request.fulfill(status=302, headers={'Location': '/main/writer/'})
                    return
                html = f'<a href="{self.site.manage_url}">章节管理</a>'
            else:
                html = '<div>工作台</div>'
            await request.fulfill(content_type='text/html; charset=utf-8', body=html)
        await self.site.context.route('**/*', route)
        await self.site.login()
        self.assertTrue(self.site.state.exists())
        self.assertEqual(calls, 2)

    async def test_sms_login(self):
        calls = 0
        async def route(request):
            nonlocal calls
            calls += 1
            html = '''<span>验证码登录</span><input placeholder="手机号">
                <input placeholder="请输入验证码"><label class="arco-checkbox"><input type="checkbox" style="display:none"><span>同意</span></label>
                <button>获取验证码</button>
                <button onclick="location.href='/main/writer/'">登录/注册</button>'''
            if calls > 1:
                html = f'<a href="{self.site.manage_url}">章节管理</a>'
            await request.fulfill(content_type='text/html; charset=utf-8', body=html)
        await self.site.context.route('**/*', route)
        with patch('getpass.getpass', side_effect=['13800000000', '123456']), patch('builtins.input', return_value='AGREE'):
            await self.site.login_sms()
        self.assertTrue(self.site.state.exists())

    async def test_sms_requires_agreement(self):
        self.list_html = '<span>验证码登录</span><input placeholder="手机号"><input type="checkbox">'
        with patch('getpass.getpass', return_value='13800000000'), patch('builtins.input', return_value='NO'):
            with self.assertRaises(Blocked):
                await self.site.login_sms()
        self.assertFalse(await self.site.page.locator('input[type="checkbox"]').is_checked())

    async def test_verified_remote_identity_and_body(self):
        self.assertEqual(await self.site.verify(self.chapter, self.url), 'published')

    async def test_wrong_remote_body_blocks(self):
        self.editor = self.editor.replace('她听见脚步。', '另一个正文')
        with self.assertRaises(Blocked):
            await self.site.verify(self.chapter, self.url)

    async def test_wrong_remote_id_blocks(self):
        self.list_html = self.list_html.replace('/456', '/999')
        with self.assertRaises(Blocked):
            await self.site.verify(self.chapter, self.url)

    async def test_pending_not_archived(self):
        self.list_html = self.list_html.replace('已发布', '审核中')
        self.assertEqual(await self.site.verify(self.chapter, self.url), 'pending')

    async def test_deferred_existing_publication_is_not_resubmitted(self):
        self.assertFalse(await self.site.resume_deferred(self.chapter, self.url))

    async def test_deferred_requires_matching_saved_body(self):
        self.list_html = '<div>测试作品</div><div>暂无章节内容</div>'
        self.assertTrue(await self.site.resume_deferred(self.chapter, self.url))
        self.editor = self.editor.replace('她听见脚步。', '不完整正文')
        with self.assertRaises(Blocked):
            await self.site.resume_deferred(self.chapter, self.url)

    async def test_paginated_duplicates(self):
        self.list_html = '''<div>测试作品</div><table><tbody><tr><td>第2章 其他</td></tr></tbody></table>
        <button class="arco-pagination-item-next" onclick="document.querySelector('td').textContent='第1章 门后的脚步';this.disabled=true">下一页</button>'''
        with self.assertRaises(Blocked):
            await self.site.duplicate_check(self.chapter)

    async def test_substring_title_is_not_duplicate(self):
        chapter = replace(self.chapter, number=5, title='十三栋')
        await self.site.page.set_content('<table><tr><td><div class="table-title">第3章 青梧苑没有十三栋</div></td><td>已发布</td></tr></table>')
        async def listing(draft=False):
            self.site.panel = self.site.page.locator('table')
        self.site.listing = listing
        await self.site.duplicate_check(chapter)

    async def test_exact_title_with_other_number_is_duplicate(self):
        chapter = replace(self.chapter, number=5, title='十三栋')
        await self.site.page.set_content('<table><tr><td><div class="table-title">第3章 十三栋</div></td></tr></table>')
        async def listing(draft=False):
            self.site.panel = self.site.page.locator('table')
        self.site.listing = listing
        with self.assertRaises(Blocked):
            await self.site.duplicate_check(chapter)
