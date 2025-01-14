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

        melon_logger.info("[+] 完成第一步操作")




        # 第二步：点击 id 是 section_time 且 class 是 cont_process 的 dd 标签中，
        # id 是 list_time 的 ul 标签中第一个 li 的 button 按钮
        melon_logger.info("[+] 第二步：点击 id 是 section_time.cont_process dd 中 list_time ul li 的第一个 button 按钮")
        time_button = page.locator("#section_time.cont_process dd #list_time ul li button").first
        await time_button.click()




        # 第三步：点击 class 是 button btColorGreen reservationBtn 的 button 按钮
        melon_logger.info("[+] 第三步：点击 class 是 button.btColorGreen.reservationBtn 的 button 按钮")
        reservation_button = page.locator("button.button.btColorGreen.reservationBtn")
        await reservation_button.click()




        # 第四步：监听新窗口打开，命名为 reservationPage，并将后续操作移至新窗口
        melon_logger.info("[+] 第四步：监听新窗口打开，并将操作移至新窗口")
        async with page.context.expect_page() as new_page_info:
            await reservation_button.click()  # 再次点击触发新页面
        reservation_page = await new_page_info.value
        await reservation_page.wait_for_load_state("load")  # 等待新页面加载完成




        # 第五步：将 reservationPage 页面中，id 是 certification 的 div 中，
        # class 是 ac 的 h3 标签背景换成浅红色
        melon_logger.info("[+] 第五步：将 reservationPage 页面中 certification div 的.ac h3 标签背景换成浅红色")
        await reservation_page.evaluate(
            "document.querySelector('#certification.ac h3').style.backgroundColor = 'lightcoral';"
        )
        melon_logger.info("[+] 页面操作完成，已将背景改为浅红色")

        """
        #endregion 执行 Melon 抢票的新逻辑
        """




        await page.goto("https://www.baidu.com")

        await context.storage_state(path=self.account_file)  # 保存Cookie
        melon_logger.info('cookie更新完毕！')
        await context.close()

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
