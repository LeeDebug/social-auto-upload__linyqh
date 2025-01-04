# -*- coding: utf-8 -*-
from datetime import datetime

from playwright.async_api import Playwright, async_playwright
import os
import asyncio

from conf import LOCAL_CHROME_PATH
from utils.base_social_media import set_init_script
from utils.files_times import get_absolute_path
from utils.log import baijiahao_logger


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=account_file)
        context = await set_init_script(context)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://baijiahao.baidu.com/builder/rc/home")
        try:
            await page.wait_for_selector("div.woo-panel-main div.LoginCard_con_3LLIV button.LoginCard_btn_Jp_u1 span.woo-button-wrap span.woo-button-content span.LoginCard_text_3BtVI:text('注册/登录百家号')", timeout=5000)  # 等待5秒

            baijiahao_logger.info("[+] 等待5秒 cookie 失效")
            return False
        except:
            baijiahao_logger.success("[+] cookie 有效")
            return True


async def baijiahao_setup(account_file, handle=False):
    account_file = get_absolute_path(account_file, "baijiahao_uploader")
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            return False
        baijiahao_logger.info('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
        await get_baijiahao_cookie(account_file)
    return True


async def get_baijiahao_cookie(account_file):
    async with async_playwright() as playwright:
        options = {
            'args': [
                '--lang en-GB'
            ],
            'headless': False,  # Set headless option here
        }
        # Make sure to run headed.
        browser = await playwright.chromium.launch(**options)
        # Setup context however you like.
        context = await browser.new_context()  # Pass any options
        context = await set_init_script(context)
        # Pause the page, and start recording manually.
        page = await context.new_page()
        await page.goto("https://baijiahao.baidu.com/builder/theme/bjh/login")
        await page.click('text="注册/登录百家号"')
        await page.wait_for_url("https://baijiahao.baidu.com/builder/rc/home")
        # await page.goto("https://me.baijiahao.com/content/video")

        # TODO 点击调试器的继续，保存cookie
        # await page.pause()

        # 保存cookie
        await context.storage_state(path=account_file)
        baijiahao_logger.success("[+] account 文件写入成功")
        baijiahao_logger.info("[+] 如需检测 cookie 是否有效，请重新运行该脚本")


class BaiJiaHaoVideo(object):
    def __init__(self, title, file_path, tags, publish_date: datetime, account_file):
        self.title = title  # 视频标题
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.date_format = '%Y-%m-%d %H:%M'
        self.local_executable_path = LOCAL_CHROME_PATH

    async def handle_upload_error(self, page):
        baijiahao_logger.error("视频出错了，重新上传中")
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # 使用 Chromium 浏览器启动一个浏览器实例
        print(self.local_executable_path)
        if self.local_executable_path:
            browser = await playwright.chromium.launch(
                headless=False,
                executable_path=self.local_executable_path,
            )
        else:
            browser = await playwright.chromium.launch(
                headless=False
            )  # 创建一个浏览器上下文，使用指定的 cookie 文件
        context = await browser.new_context(storage_state=f"{self.account_file}")
        context = await set_init_script(context)
        context.on("close", lambda: context.storage_state(path=self.account_file))

        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://aigc.baidu.com/make")
        # baijiahao_logger.info('正在上传-------{}.mp4'.format(self.title))
        # 等待页面跳转到指定的 URL，没进入，则自动等待到超时
        baijiahao_logger.info('正在打开 度加创作工具 ...')
        await page.wait_for_url("https://aigc.baidu.com/make")




        div = await page.wait_for_selector('div.grid.overflow-hidden.group-hover\\:grid-rows-\\[1fr\\].grid-rows-\\[0fr\\].transition-all')
        await div.hover()

        # 等待页面上有一个符合条件的按钮
        btn = await page.wait_for_selector(
            '.loki-button:has-text("生成文案")',
            state='visible',
            timeout=10000  # 最长等待时间（毫秒）
        )
        print("btn: ", btn)
        await btn.click()


        # # 查找所有符合条件的按钮
        # buttons = await page.query_selector_all('.loki-button')
        # print("buttons: ", buttons)
        #
        # for button in buttons:
        #     button_text = await button.text_content() if await button.text_content() else ''
        #
        #     if button_text == '生成文案':
        #         print("\n\nbutton_text: ", button_text)
        #         # 定位按钮的父组件的父组件
        #         parent_parent = await button.evaluate_handle('el => el.parentElement?.parentElement')
        #         print("parent_parent: ", parent_parent)
        #
        #         # 增加鼠标 hover 事件
        #         await parent_parent.hover()
        #
        #         # 定位兄弟组件中的 span 标签
        #         sibling_elements = await parent_parent.evaluate_handle(
        #             """
        #             (parent) => {
        #                 const siblings = Array.from(parent.parentElement?.children || []);
        #                 return siblings
        #                     .filter(sibling => sibling !== parent)
        #                     .flatMap(sibling => Array.from(sibling.querySelectorAll('span')));
        #             }
        #             """
        #         )
        #         print("sibling_elements: ", sibling_elements)
        #         # 增加鼠标 hover 事件
        #         await parent_parent.hover()
        #
        #         # 获取 span 文案
        #         if sibling_elements:
        #             span_texts = sibling_elements.evaluate(
        #                 """
        #                 spans => spans.map(span => span.textContent.trim())
        #                 """
        #             )
        #
        #             if span_texts:
        #                 print('Span 文案:', span_texts)
        #
        #         # 点击第一个匹配的按钮
        #         await button.click()
        #         break  # 点击第一个后跳出循环







        print("遍历完毕")

        # 点击 "上传视频" 按钮
        upload_button = page.locator("button[class^='loki-button']:text('一键成片')")
        print("upload_button: ", upload_button)
        await upload_button.wait_for(state='visible')  # 确保按钮可见

        # async with page.expect_file_chooser() as fc_info:
        #     await upload_button.click()
        # file_chooser = await fc_info.value
        # await file_chooser.set_files(self.file_path)

        print("等待 20s 时间")
        await asyncio.sleep(20)

        # if not await page.get_by_text("封面编辑").count():
        #     raise Exception("似乎没有跳转到到编辑页面")

        # await asyncio.sleep(1)

        # 等待按钮可交互
        # new_feature_button = page.locator('button[type="button"] span:text("我知道了")')
        # if await new_feature_button.count() > 0:
        #     await new_feature_button.click()

        baijiahao_logger.info("正在选择原创类型...")
        # 点击 "原创" 按钮
        # await page.get_by_text("原创").locator("xpath=following-sibling::input").click()
        # await page.locator("div[class^='Type_gap1'] div[class^='Type_type_2'] label:has(span.woo-radio-text:has-text('原创'))").click()
        # await page.locator("label.woo-radio-main:has-text('原创') input").click()

        baijiahao_logger.info("正在填充标题和话题...")
        await page.get_by_text("标题").locator("xpath=following-sibling::div").click()
        baijiahao_logger.info("clear existing title")
        await page.keyboard.press("Backspace")
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.press("Delete")
        baijiahao_logger.info("filling new  title")
        await page.keyboard.type(self.title)
        await page.keyboard.press("Enter")

        # 快手只能添加3个话题
        for index, tag in enumerate(self.tags[:3], start=1):
            baijiahao_logger.info("正在添加第%s个话题" % index)
            await page.keyboard.type(f"#{tag} ")
            await asyncio.sleep(2)

        max_retries = 60  # 设置最大重试次数,最大等待时间为 2 分钟
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 获取包含 '上传中' 文本的元素数量
                number = await page.locator("text=上传中").count()

                if number == 0:
                    baijiahao_logger.success("视频上传完毕")
                    break
                else:
                    if retry_count % 5 == 0:
                        baijiahao_logger.info("正在上传视频中...")
                    await asyncio.sleep(2)
            except Exception as e:
                baijiahao_logger.error(f"检查上传状态时发生错误: {e}")
                await asyncio.sleep(2)  # 等待 2 秒后重试
            retry_count += 1

        if retry_count == max_retries:
            baijiahao_logger.warning("超过最大重试次数，视频上传可能未完成。")

        # 定时任务
        if self.publish_date != 0:
            await self.set_schedule_time(page, self.publish_date)

        # 判断视频是否发布成功
        while True:
            try:
                publish_button = page.get_by_text("发布", exact=True)
                if await publish_button.count() > 0:
                    await publish_button.click()

                await asyncio.sleep(1)
                confirm_button = page.get_by_text("确认发布")
                if await confirm_button.count() > 0:
                    await confirm_button.click()

                # 等待页面跳转，确认发布成功
                await page.wait_for_url(
                    "https://cp.baijiahao.com/article/manage/video?status=2&from=publish",
                    timeout=5000,
                )
                baijiahao_logger.success("视频发布成功")
                break
            except Exception as e:
                baijiahao_logger.info(f"视频正在发布中... 错误: {e}")
                await page.screenshot(full_page=True)
                await asyncio.sleep(1)

        await context.storage_state(path=self.account_file)  # 保存cookie
        baijiahao_logger.info('cookie更新完毕！')
        await asyncio.sleep(2)  # 这里延迟是为了方便眼睛直观的观看
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

    async def set_schedule_time(self, page, publish_date):
        baijiahao_logger.info("click schedule")
        publish_date_hour = publish_date.strftime("%Y-%m-%d %H:%M:%S")
        await page.locator("label:text('发布时间')").locator('xpath=following-sibling::div').locator(
            '.ant-radio-input').nth(1).click()
        await asyncio.sleep(1)

        await page.locator('div.ant-picker-input input[placeholder="选择日期时间"]').click()
        await asyncio.sleep(1)

        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date_hour))
        await page.keyboard.press("Enter")
        await asyncio.sleep(1)
