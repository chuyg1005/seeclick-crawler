from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image, ImageDraw

import os
import time

from utils import *

import re
import logging

import argparse


class CrawlerBase:
    def __init__(self, driver_path, width=1920, height=1080, wait_timeout=3, logger=None):
        self.driver_path = driver_path
        self.width = width
        self.height = height
        self.wait_timeout = wait_timeout
        self.driver = self.buildDriver(driver_path, width, height, wait_timeout)
        self.logger = logger

    @staticmethod
    def buildDriver(driver_path, width, height, wait_timeout):
        service = webdriver.chrome.service.Service(executable_path=driver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')  # 避免沙箱模式
        chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm的使用
        chrome_options.add_argument('--charset=utf-8')  # 设置字符编码为 UTF-8
        # 设置文件下载目录
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "./downloads"
        })

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(width, height)

        driver.implicitly_wait(wait_timeout)  # 设置隐式等待时间
        return driver

    def restart(self):
        if self.logger:
            self.logger.info("restart driver")
        else:
            print("restart driver")
        self.driver.quit()
        self.driver = self.buildDriver(self.driver_path, self.width, self.height, self.wait_timeout)

    def quit(self):
        self.driver.quit()

    def accessURL(self, url):
        if self.logger:
            self.logger.info("access url: {}".format(url))
        else:
            print("access url: {}".format(url))
        self.driver.get(url)


class Crawler(CrawlerBase):
    def __init__(self, driver_path, save_dir, logger, draw_box=False, scrape_hover=False):
        super().__init__(driver_path, 1920, 1080, 3)
        self.driver_path = driver_path
        self.width = 1920
        self.height = 1080
        self.wait_timeout = 3
        self.bounded = False
        self.save_dir = save_dir
        self.draw_box = draw_box  # 是否需要draw_box
        self.scrape_hover = scrape_hover  # 是否需要检测hover的元素
        os.makedirs(save_dir, exist_ok=True)
        self.additional_timeout = 2
        self.box_color = (255, 0, 0)
        self.logger = logger

    def saveScreenshot(self, save_path):
        self.logger.info("save screenshot to {}".format(save_path))
        self.driver.save_screenshot(save_path)

    def findAllClickableElements(self):
        # elements = self.driver.find_elements(By.XPATH,
        #                                      "//a | //button | //input[@type='submit'] | //input[@type='button'] | //label | //*[@onclick]")
        elements = self.driver.find_elements(By.XPATH,
                                             "//a | //button | //input[@type='submit'] | //*[@onclick]")

        return elements

    def findAllTitledElements(self):
        elements = self.driver.find_elements(By.XPATH, "//*[@title]")
        return elements

    def findAllMouseOverElements(self):
        # 1. method1
        # elements = self.driver.find_elements(By.XPATH, "//*[@onmouseover]")
        # 2. method2
        # 使用JavaScript执行脚本来获取所有绑定了mouseover事件的元素
        elements = self.driver.execute_script(
            'return Array.from(document.querySelectorAll("*")).filter(elem => {'
            '   const events = getEventListeners(elem);'
            '   return events.hasOwnProperty("mouseover");'
            '});'
        )
        return elements

    def findAllElements(self):
        """查找页面上的所有elements"""
        return self.driver.find_elements(By.XPATH, '//*')

    def findAllHiddenElements(self):
        elements = self.driver.find_elements(By.XPATH, "//*")
        hidden_elements = [element for element in elements if not element.is_displayed()]
        return hidden_elements

    def findAllNotHiddenElements(self):
        elements = self.driver.find_elements(By.XPATH, "//*")
        not_hidden_elements = [element for element in elements if element.is_displayed()]
        return not_hidden_elements

    def __processClickableElements(self):
        results = []
        signatures = set()
        elements = self.findAllClickableElements()
        for element in elements:
            # 判断当前元素是否是叶子节点
            try:
                left_top = (element.location['x'], element.location['y'])
                width, height = element.size['width'], element.size['height']
                right_bottom = (left_top[0] + width, left_top[1] + height)
                text = element.text
                if text is None or text == '':
                    text = element.get_attribute("value")
                if text is None or text == '':
                    continue
                if width == 0 or height == 0:
                    continue
                if self.bounded and (right_bottom[0] >= self.width or right_bottom[1] >= self.height):
                    continue
                signature = f'{left_top[0]}-{left_top[1]}-{width}-{height}'
                if signature in signatures: continue
                signatures.add(signature)
                results.append({"left-top": left_top, "size": (width, height), "text": text, "type": "text"})
                self.logger.info(f"location: ({left_top[0]}, {left_top[1]}), size: ({width}, {height}), text: {text}")
                #     draw.rectangle([left_top, right_bottom], outline=self.box_color, width=2)
            except Exception as exp:
                self.logger.warn(exp)
                continue
        return results

    def __processHoverElementsV2(self, draw=None):
        results = []
        signatures = set()
        elements = self.findAllTitledElements()
        for element in elements:
            # 判断当前元素是否是叶子节点
            try:
                left_top = (element.location['x'], element.location['y'])
                width, height = element.size['width'], element.size['height']
                right_bottom = (left_top[0] + width, left_top[1] + height)
                text = element.text
                if not element.is_displayed():
                    continue
                if width == 0 or height == 0:
                    continue
                if self.bounded and (right_bottom[0] >= self.width or right_bottom[1] >= self.height):
                    continue
                if text is None or text.strip() == '':
                    title = element.get_attribute("title")
                    if title is None or title == '': continue
                    signature = f'{left_top[0]}-{left_top[1]}-{width}-{height}'
                    if signature in signatures: continue
                    signatures.add(signature)
                    results.append({"left-top": left_top, "size": (width, height), "text": title, "type": "hover"})
                    self.logger.info(
                        f"location: ({left_top[0]}, {left_top[1]}), size: ({width}, {height}), text: {title}")
                    #     draw.rectangle([left_top, right_bottom], outline=self.box_color, width=2)
            except Exception as exp:
                self.logger.warn(exp)
                continue
        return results

    def __processHoverElements(self, draw=None):
        elements = self.findAllNotHiddenElements()
        # 获取悬停前的页面源代码
        before_hover_page_source = self.driver.page_source
        # 创建ActionChains对象
        # hidden_elements = self.findAllHiddenElements()
        not_hidden_elements = self.findAllNotHiddenElements()
        actions = ActionChains(self.driver)
        results = []
        signatures = set()
        for element in elements:
            # 判断当前元素是否是叶子节点
            try:
                is_leaf_element = self.isLeafElement(element)
                if not is_leaf_element:
                    continue
                left_top = (element.location['x'], element.location['y'])
                width, height = element.size['width'], element.size['height']
                right_bottom = (left_top[0] + width, left_top[1] + height)
                if not element.is_displayed():
                    continue
                if width == 0 or height == 0:
                    continue
                if right_bottom[0] >= 1920 or right_bottom[1] >= 1080:
                    continue
                signature = f'{left_top[0]}-{left_top[1]}-{width}-{height}'
                if signature in signatures: continue
                signatures.add(signature)
                # actions.reset_actions()
                actions.move_to_element(element).perform()
                after_hover_page_source = self.driver.page_source
                if after_hover_page_source != before_hover_page_source:
                    # hidden_elements_now = self.findAllHiddenElements()
                    not_hidden_elements_now = self.findAllNotHiddenElements()
                    display_elements = set(not_hidden_elements_now) - set(not_hidden_elements)
                    tips = []
                    if len(display_elements) > 0:
                        print('================================================================')
                        print(f"location: ({left_top[0]}, {left_top[1]}), size: ({width}, {height})")
                        if draw is not None:
                            draw.rectangle([left_top, right_bottom], outline=self.box_color, width=2)
                        for display_element in display_elements:
                            if not self.isLeafElement(display_element): continue
                            if display_element.text is None or display_element.text.strip() == '': continue
                            print(display_element.text)
                            tips.append(display_element.text)
                        if len(tips) > 0:
                            sep = '@@'
                            text = sep.join(tips)
                            results.append({"left-top": left_top, "size": (width, height), "text": text})
            except Exception as exp:
                print(exp)
                continue
        return results

    def processURL(self, url, save_name=None):
        if save_name is None:
            # save_name = urlparse(url).hostname
            save_name = generate_url_hash(url)
        save_path = os.path.join(self.save_dir, save_name + ".png")
        self.accessURL(url)

        # 等待第一个div加载结束
        wait = WebDriverWait(self.driver, self.wait_timeout)  # 设置最长等待时间为10秒
        wait.until(EC.presence_of_element_located((By.XPATH, "//div")))
        # 再sleep 5s
        time.sleep(self.additional_timeout)

        # 缩放
        if not self.bounded:
            width = self.driver.execute_script("return document.body.scrollWidth")
            height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.set_window_size(width, height)
        else:
            width = self.width
            height = self.height

        results = self.__processClickableElements()
        if self.scrape_hover:
            results += self.__processHoverElementsV2()
        # if not self.scrape_hover:
        #     results = self.__processClickableElements()
        # else:
        #     results = self.__processHoverElementsV2()

        # 最后保存截图，防止保存到空白的
        self.saveScreenshot(save_path)
        image = Image.open(save_path)
        # image = image.resize([self.width, self.height], Image.ANTIALIAS)
        image = image.resize([width, height])

        for result in results:
            result['url'] = url
            result['image_path'] = save_path
            self.logger.info(result)

        if self.draw_box:  # draw-box放到最后
            draw = ImageDraw.Draw(image)
            for result in results:
                left_top = result['left-top']
                size = result['size']
                draw.rectangle([left_top, (left_top[0] + size[0], left_top[1] + size[1])], outline=self.box_color,
                               width=2)

        image.save(save_path)
        image.close()

        # self.driver.close()

        return results

    @staticmethod
    def isLeafElement(element):
        """判断元素是否是叶子节点"""
        # children = element.find_elements(By.XPATH, './*')
        html = element.get_attribute('innerHTML')
        # 使用正则表达式匹配包含子元素的HTML标签
        pattern = r'<[^>]*>.*?<[^>]*>'
        # 查找匹配项
        match = re.search(pattern, html, re.DOTALL)

        if match:
            return True
        else:
            return False
        # if '<' in inner and '>' in inner:
        #     return False
        # else:
        #     return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_file", type=str, default="./test_urls.txt")
    args = parser.parse_args()

    driver_path = "./chromedriver"
    test_url = "file://" + args.test_file
    logger = logging.getLogger(__name__)
    crawler = Crawler(driver_path, './images', logger, draw_box=True, scrape_hover=True)
    crawler.processURL(test_url, "./test.png")
    # crawler.accessURL(test_url)
    # crawler.saveScreenshot("./test.png")
    # start = time.time()
    # for test_url in test_urls:
    #     crawler.processURL(test_url)
    # end = time.time()
    # print(f"cost time: {end - start}")
    crawler.quit()
