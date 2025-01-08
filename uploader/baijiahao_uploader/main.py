# -*- coding: utf-8 -*-
import json
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
        browser = await playwright.chromium.launch(headless=True)
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
    def __init__(self, account_file):
        self.account_file = account_file
        self.local_executable_path = LOCAL_CHROME_PATH
    # def __init__(self, title, file_path, tags, publish_date: datetime, account_file):
    #     self.title = title  # 视频标题
    #     self.file_path = file_path
    #     self.tags = tags
    #     self.publish_date = publish_date
    #     self.account_file = account_file
    #     self.date_format = '%Y-%m-%d %H:%M'
    #     self.local_executable_path = LOCAL_CHROME_PATH

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

        await asyncio.sleep(2) # 等待页面稳定后

        baijiahao_logger.info('正在获取 新闻热点 ...')
        # await page.wait_for_url("https://aigc.baidu.com/jdkwnwqnjkd")



        # 删除 localStorage 中所有以 ttv- 开头的条目
        baijiahao_logger.info('正在删除 LocalStorage 中所有 ttv- 的属性 ...')
        await page.evaluate("""
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('ttv-')) {
                    localStorage.removeItem(key);
                }
            });
        """)

        # 获取 ReleasesInformation 数据
        baijiahao_logger.info('正在获取 LocalStorage 属性 ...')
        releases_information = await page.evaluate("() => { return localStorage.getItem('ReleasesInformation') || null; }")
        print("releases_information before: ", releases_information)
        # 如果 ReleasesInformation 存在并且是有效的 JSON 格式，则解析为字典，否则初始化为空字典
        if releases_information:
            releases_information = json.loads(releases_information)
        else:
            releases_information = {}
        print("releases_information after: ", releases_information)

        await asyncio.sleep(2)  # 等待列表加载完毕后

        # 获取 Hot_News_List 列表中的每个新闻项目
        baijiahao_logger.info('正在获取 热点新闻 列表 ...')
        hot_news_list = await page.query_selector_all(
            "div.overflow-auto.flex-grow.h-0.saas-scrollbar.mt-\\[-4px\\].pl-\\[24px\\].pr-\\[10px\\].pb-\\[18px\\] > div"
        )
        print("hot_news_list: ", hot_news_list)
        # 替代方案 2
        # hot_news_list_111 = await page.query_selector_all(
        #     "div.overflow-auto.saas-scrollbar > div"
        # )
        # print("hot_news_list_111: ", hot_news_list_111)
        # 替代方案 3
        # hot_news_list_222 = await page.query_selector_all(
        #     "//div[contains(@class, 'overflow-auto') and contains(@class, 'saas-scrollbar')]//div"
        # )
        # print("hot_news_list_222: ", hot_news_list_222)

        baijiahao_logger.info('正在遍历 热点新闻 列表 ...')
        for index, hot_news_item in enumerate(hot_news_list, start=1):
            # 获取新闻标题内容
            hot_news_item_title_element = await hot_news_item.query_selector(
                "div.flex.text-gray-darker.items-center.relative.pr-\\[56px\\] span")
            baijiahao_logger.info(f"添加 hover 事件，展示出 ‘生成文案’ 按钮")
            await hot_news_item_title_element.hover()
            # print("hot_news_item_title_element: ", hot_news_item_title_element)
            hot_news_item_title = await hot_news_item_title_element.text_content() if hot_news_item_title_element else None
            baijiahao_logger.info(f"第 {index} 条新闻标题: {hot_news_item_title}")

            # 如果标题存在并且在 ReleasesInformation 中已定义过，则跳过
            if hot_news_item_title in releases_information:
                baijiahao_logger.info(f"[+] 标题 '{hot_news_item_title}' 已生成文案，跳过处理")
                continue

            # 点击 “生成文案” 按钮
            hot_news_item_button = await hot_news_item.query_selector("button:has-text('生成文案')")
            print("hot_news_item_button: ", hot_news_item_button)
            # is_visible = await hot_news_item_button.is_visible()
            # print("hot_news_item_button > is_visible: ", is_visible)
            if hot_news_item_button:
                print("hot_news_item_button > text before: ", await hot_news_item_button.inner_text())
                await hot_news_item_button.click()
                baijiahao_logger.info(f"[+] 正在生成文案: {hot_news_item_title}")
                print("hot_news_item_button > text after: ", await hot_news_item_button.inner_text())

                # ing = await hot_news_item.query_selector("button:has-text('文案生成中')")
                # print("ing > text: ", ing)
                # print("ing > text.text_content: ", ing.inner_text())

                # 在 localStorage 中更新 ReleasesInformation
                # releases_information[hot_news_item_title] = "已生成文案"
                # await page.evaluate(f'localStorage.setItem("ReleasesInformation", {json.dumps(releases_information)});')
                break

        # 通过 `page.on('popup')` 捕获新打开的页面
        print("创建 new_page 属性来接受新打开的页面")
        new_page = None  # 外部声明 `new_page`
        # 捕获新页面打开的事件
        def handle_popup(popup):
            nonlocal new_page  # 使用 nonlocal 来引用外部的 `new_page`
            new_page = popup
        page.on('popup', handle_popup)

        print("循环完毕，继续检测 一键成片 按钮")
        # 循环检测 One_Click_Publish 按钮的 disabled 属性
        one_click_publish_button = await page.query_selector("button:has-text('一键成片')")
        print("one_click_publish_button: ", one_click_publish_button)
        while True:
            # 检查按钮是否禁用
            disabled = await one_click_publish_button.get_attribute("disabled")
            if disabled is None:
                # 如果没有禁用，则点击该按钮
                # await one_click_publish_button.click()
                # TODO 模拟打开新窗口
                await page.evaluate("window.open('https://aigc.baidu.com/builder/aigc?source=111&target=222')")
                baijiahao_logger.info("[+] 点击了一键成片按钮")
                break
            baijiahao_logger.info("[+] One_Click_Publish 按钮仍然禁用，继续检测...")
            await asyncio.sleep(1)  # 每秒检测一次

        # 等待打开的新页面并延时关闭
        # await page.wait_for_timeout(5000)  # 等待5秒
        # # await page.close()

        # 等待新页面打开
        print("按钮点击完毕，等待打开新页面 ...")
        await page.wait_for_event('popup')  # 等待弹出的页面
        # 确保新页面 URL 符合要求
        print("新页面已打开，new_page 是: ", new_page)
        if new_page:
            print("new_page.url(): ", new_page.url())
            new_page_url = await new_page.url()
            print("new_page_url: ", new_page_url)
            if new_page_url.startswith("https://aigc.baidu.com/builder/aigc?"):
                baijiahao_logger.info(f"[+] 新页面已成功打开，URL: {new_page_url}")
                await asyncio.sleep(10)  # 这里延迟是为了方便眼睛直观的观看
                await new_page.close()

            else:
                baijiahao_logger.warning(f"[+] 新页面 URL 不符合预期: {new_page_url}")


        await context.storage_state(path=self.account_file)  # 保存cookie
        baijiahao_logger.info('cookie更新完毕！')

        await asyncio.sleep(5000)  # 这里延迟是为了方便眼睛直观的观看

        # try:
        #     await context.close()
        #     baijiahao_logger.info('浏览器上下文已成功关闭')
        #     # await browser.close()
        # except Exception as e:
        #     baijiahao_logger.error(f'关闭浏览器上下文或保存cookie时出现错误: {e}')

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

