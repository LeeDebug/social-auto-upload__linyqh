# -*- coding: utf-8 -*-
from datetime import datetime
from playwright.async_api import Playwright, async_playwright
import os
import asyncio

from conf import LOCAL_CHROME_PATH  # 本地Chrome路径配置
from utils.base_social_media import set_init_script  # 初始化脚本工具函数
from utils.files_times import get_absolute_path  # 获取绝对路径工具函数
from utils.log import melon_logger  # 日志工具

# 主函数入口
class MelonVideo(object):
    def __init__(self, account_file):
        self.account_file = account_file  # Cookie文件路径
        self.local_executable_path = LOCAL_CHROME_PATH  # 本地Chrome路径

    # 异步主函数
    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

    # 上传视频主流程
    async def upload(self, playwright: Playwright) -> None:
        if self.local_executable_path:
            # 启动带指定路径的Chromium浏览器
            browser = await playwright.chromium.launch(
                headless=False,
                executable_path=self.local_executable_path,
            )
        else:
            # 启动默认Chromium浏览器
            browser = await playwright.chromium.launch(headless=False)

        # 创建浏览器上下文并加载Cookie
        context = await browser.new_context(storage_state=f"{self.account_file}")
        context = await set_init_script(context)
        context.on("close", lambda: context.storage_state(path=self.account_file))

        # 创建新页面并访问目标网址
        page = await context.new_page()

        """
        #region 执行 Melon 抢票的新逻辑
        """
        # 访问页面
        melon_logger.info("[+] 开始访问页面 https://tkglobal.melon.com/performance/index.htm?langCd=EN&prodId=210513")
        await page.goto("https://tkglobal.melon.com/performance/index.htm?langCd=EN&prodId=210513")

        # 等待 2s 中，让页面渲染完毕
        await asyncio.sleep(2)




        # 第一步：点击 id 是 cal_wrapper 的 tbody 标签中，第一个没有 disabled="disabled" 属性的 button 标签
        # 定位到 tbody，并选择第一个未禁用的 button
        melon_logger.info("[+] 第一步：点击 id 是 cal_wrapper 的 tbody 中第一个未禁用的 button 标签")

        # 第一步：获取 id="cal_wrapper" 的 tbody 标签
        melon_logger.info("[+] 开始获取 id='cal_wrapper' 的 tbody 元素")
        tbody = page.locator("#cal_wrapper")
        melon_logger.info("[+] 成功获取 id='cal_wrapper' 的 tbody 元素")

        # 遍历 tbody 中所有 tr 标签
        melon_logger.info("[+] 开始遍历 tbody 中的所有 tr 元素")
        tr_elements = await tbody.element_handles()
        melon_logger.info("[+] 成功获取 tbody 中的所有 tr 元素")

        for tr in tr_elements:
            # 遍历所有 tr 标签中所有 td 标签
            melon_logger.info("[+] 开始遍历当前 tr 元素中的所有 td 元素")
            td_elements = await tr.query_selector_all("td")
            melon_logger.info("[+] 成功获取当前 tr 元素中的所有 td 元素")

            for td in td_elements:
                # 获取每个 td 标签中的 button 按钮
                melon_logger.info("[+] 开始查找当前 td 元素中的 button 元素")
                button = await td.query_selector("button:not([disabled='disabled'])")
                if button:
                    # 如果获取到第一个没有 disabled="disabled" 属性的，则点击它
                    melon_logger.info("[+] 找到第一个未禁用的 button 元素，准备点击")
                    await button.click()
                    melon_logger.info("[+] 已点击第一个未禁用的 button 元素")
                    break
                else:
                    melon_logger.info("[+] 当前 td 元素中未找到未禁用的 button 元素")
        await asyncio.sleep(1)



        # 第二步：点击 id 是 section_time 且 class 是 cont_process 的 dd 标签中，
        # id 是 list_time 的 ul 标签中第一个 li 的 button 按钮
        melon_logger.info("[+] 开始第二步操作：查找 id 是 section_time 且 class 是 cont_process 的元素")
        section_time_element = page.locator("#section_time.cont_process")
        melon_logger.info("[+] 成功找到 id 是 section_time 且 class 是 cont_process 的元素")

        melon_logger.info("[+] 开始查找 dd 元素下 id 为 list_time 的 ul 元素")
        # 先使用 locator 定位，再使用 element_handle 获取元素句柄
        list_time_ul_locator = section_time_element.locator("#list_time.list_type")
        list_time_ul = await list_time_ul_locator.element_handle()
        if list_time_ul:
            melon_logger.info("[+] 成功找到 dd 元素下 id 为 list_time 的 ul 元素")

            melon_logger.info("[+] 开始遍历 ul 元素中的 li 元素")
            # 遍历 ul 元素句柄，查找 li 元素
            li_elements = await list_time_ul.query_selector_all("li")
            melon_logger.info("[+] 成功获取 ul 元素中的 li 元素列表")

            for li in li_elements:
                melon_logger.info("[+] 开始查找 li 元素中的 button 元素")
                button = await li.query_selector("button")
                if button:
                    melon_logger.info("[+] 找到第一个 button 元素，准备点击")
                    await button.click()
                    melon_logger.info("[+] 已点击第一个 button 元素")
                    break
                else:
                    melon_logger.info("[+] 当前 li 元素中未找到 button 元素")
        else:
            melon_logger.info("[+] 当前 dd 元素下未找到 id 为 list_time 的 ul 元素")
        await asyncio.sleep(1)

        # 定义一个变量用于存储新窗口的引用
        new_window__reservation = None
        # 监听新页面事件
        def on_new_page(new_page):
            nonlocal new_window__reservation
            new_window__reservation = new_page
        context.on("page", on_new_page)

        # 第三步：点击 class 是 button btColorGreen reservationBtn 的 button 按钮
        melon_logger.info("[+] 第三步：点击 class 是 button.btColorGreen.reservationBtn 的 button 按钮")
        reservation_button = page.locator("button.button.btColorGreen.reservationBtn")
        await reservation_button.click()
        melon_logger.info("[+] 点击操作完成，等待新页面出现完成")
        await asyncio.sleep(2)



        # 第四步：监听新窗口打开，命名为 reservationPage，并将后续操作移至新窗口
        melon_logger.info("[+] 第四步：监听新窗口打开，并将操作移至新窗口")
        try:
            melon_logger.info("[+] 开始监听新窗口的上下文创建")
            # async with browser.contexts[-1].expect_event("page") as new_context_info:
            # 等待新窗口打开并加载
            if new_window__reservation:
                await new_window__reservation.wait_for_load_state()
                print("新窗口的 URL:", new_window__reservation.url)

                # 在新窗口上执行操作
                # await new_window__reservation.screenshot(path="new_window__reservation.png")  # 截图保存

                print("正在等待新页面打开...")
                # 这里可以执行其他异步操作，例如等待几秒钟
                await asyncio.sleep(1)
                print("在等待新页面打开的同时，这里可以做其他事情")
                print("new_context_info 1:", new_window__reservation)
                # 这里应该是触发新窗口打开的操作，例如点击一个按钮
            melon_logger.info("[+] 新页面已完全加载")
        except Exception as e:
            melon_logger.error(f"[!] 监听新页面打开或页面加载失败: {str(e)}")
            return
        print("new_context_info 233:", new_window__reservation)
        await asyncio.sleep(5)




        # 第五步：将 reservationPage 页面中，id 是 certification 的 div 中，
        # class 是 ac 的 h3 标签背景换成浅红色
        melon_logger.info("[+] 第五步：将 reservationPage 页面中 certification div 的.ac h3 标签背景换成浅红色")
        await new_window__reservation.evaluate("""
            () => {
                const h3Element = document.getElementById('certification');
                if (h3Element) {
                    h3Element.style.backgroundColor = 'lightcoral';  // 浅红色
                }
            }
        """)
        melon_logger.info("[+] 页面操作完成，已将背景改为浅红色")


        # 关闭弹出的选票页面
        await new_window__reservation.close()
        await asyncio.sleep(2)



        """
        #endregion 执行 Melon 抢票的新逻辑
        """


        await page.goto("https://www.baidu.com")

        await context.storage_state(path=self.account_file)  # 保存Cookie
        melon_logger.info('cookie更新完毕！')
        await asyncio.sleep(2)
        # 检查上下文是否仍然活跃
        try:
            await context.pages[0].evaluate("() => console.log('Context is active')")
            print("上下文仍然活跃")
        except Exception as e:
            print(f"上下文已关闭: {e}")
        await asyncio.sleep(2)

        # 使用状态变量管理关闭逻辑
        # if context:
        #     try:
        #         await context.close()
        #     except Exception as close_error:
        #         melon_logger.warning(f"关闭上下文时出错: {close_error}")
        # await asyncio.sleep(2)
        #
        # if browser:
        #     try:
        #         await browser.close()
        #     except Exception as close_error:
        #         melon_logger.warning(f"关闭浏览器时出错: {close_error}")

    # 设置定时发布时间
    async def set_schedule_time(self, page, publish_date):
        melon_logger.info("click schedule")
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

    # 处理上传错误
    async def handle_upload_error(self, page):
        melon_logger.error("视频出错了，重新上传中")
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)


# 设置并检查Cookie文件
async def melon_setup(account_file, handle=False):
    account_file = get_absolute_path(account_file, "melon_uploader")  # 获取绝对路径
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            return False  # 如果未启用自动处理，返回False
        melon_logger.info('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
        await get_melon_cookie(account_file)  # 获取新的Cookie文件
    return True


# 检查Cookie文件是否有效
async def cookie_auth(account_file):
    # 使用 Playwright 异步上下文管理器
    async with async_playwright() as playwright:
        # 启动Chromium浏览器
        browser = await playwright.chromium.launch(headless=True)
        # 创建一个新的浏览器上下文并加载Cookie
        context = await browser.new_context(storage_state=account_file)
        # 设置初始脚本
        context = await set_init_script(context)
        # 创建一个新的页面
        page = await context.new_page()
        # 打开目标网址
        await page.goto("https://gmember.melon.com/member/myinfo_form.htm")
        try:
            # 等待页面上特定元素加载，超时时间为5秒
            await page.wait_for_selector("div.wrap_booking h3:text('Sign In')", timeout=5000)
            melon_logger.info("[+] 等待5秒 cookie 失效")
            return False  # Cookie失效
        except:
            melon_logger.success("[+] cookie 有效")
            return True  # Cookie有效


# 获取新的Cookie文件
async def get_melon_cookie(account_file):
    async with async_playwright() as playwright:
        options = {
            'args': [
                '--lang en-GB'  # 设置浏览器语言
            ],
            'headless': False,  # 设置非无头模式，方便用户操作
        }
        # 启动浏览器
        browser = await playwright.chromium.launch(**options)
        # 创建新的浏览器上下文
        context = await browser.new_context()
        # 设置初始脚本
        context = await set_init_script(context)
        # 创建页面并打开目标网址
        page = await context.new_page()
        await page.goto("https://gmember.melon.com/login/login_form.htm")
        # await page.goto("https://tkglobal.melon.com/performance/index.htm?langCd=EN&prodId=210513")
        # await page.click('text="立即登录"')  # 点击“立即登录”按钮
        # await page.click('text="扫码登录"')  # 点击“扫码登录”按钮
        await page.wait_for_url("https://tkglobal.melon.com/main/index.htm**")  # 等待跳转到个人主页

        # 保存Cookie文件
        await context.storage_state(path=account_file)
        melon_logger.success("[+] account 文件写入成功")
        melon_logger.info("[+] 如需检测 cookie 是否有效，请重新运行该脚本")
