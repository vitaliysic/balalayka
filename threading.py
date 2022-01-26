import platform
import time
from pathlib import Path
from threading import Thread
import logging

import config as cfg

# from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, \
    UnexpectedAlertPresentException, ElementNotInteractableException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class Browser(Thread):
    stop = False
    pause = True

    account = {}
    product = {}

    set_value_script = "arguments[0].innerHTML = arguments[1]"
    thread_status = None

    def __init__(self, driver, account, product, script, index):
        super().__init__(name=str(index))
        self.driver = driver
        self.script = script
        self.account = account
        self.product = product

    def run(self) -> None:
        driver = self.driver
        # driver.get("http://whatismyipaddress.com")

        try:
            self.signin()

            while self.pause:
                time.sleep(1)

            self.set_status_form_value(self.thread_status, 'running')

            while not self.stop:
                time.sleep(1)
                if self.pause:
                    self.log("Поток поставлен на паузу")
                    while True:
                        self.set_status_form_value(self.thread_status, 'pause')
                        if not self.pause:
                            self.set_status_form_value(self.thread_status, 'running')
                            self.log("Возобновление работы")
                            break
                try:
                    if not self.check_health():
                        time.sleep(1)
                except UnexpectedAlertPresentException:
                    self.resolve_alert()

            driver.close()
        except WebDriverException as e:
            self.log("Критическое завершение работы: " + e.msg)
            return

    def get_headers_from_mystery_box_sale(self):
        driver = self.driver
        url = 'https://www.binance.com/en/nft/goods/sale/' + self.account['boxId'] + '?isBlindBox=1&isOpen=false'
        driver.get(url)
        time.sleep(5)

        input_sum = driver.find_element(by=By.XPATH,
                                        value='/html/body/div[1]/div/div[2]/main/div/div/div[5]/div[2]/div/div[1]/input')
        ActionChains(driver).move_to_element(input_sum).key_down(Keys.CONTROL, "a") \
            .send_keys(Keys.DELETE).send_keys(5).perform()

        time.sleep(5)
        driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/main/div/div/div[8]/button[2]').click()

    def signin(self):
        driver = self.driver

        self.get('https://accounts.binance.com/en/login')

        by_email = driver.find_element(by=By.XPATH, value='//*[@id="tab-email"]/div')
        ActionChains(driver).move_to_element(by_email).click().perform()

        email = driver.find_element(by=By.XPATH,
                                    value='//*[@id="wrap_app"]/main/div[2]/div/div/div[2]/div[1]/form/div/div[1]/div[2]/div/input')
        ActionChains(driver).move_to_element(email).click().send_keys(self.account['email']).perform()

        password = driver.find_element(by=By.XPATH,
                                       value='//*[@id="wrap_app"]/main/div[2]/div/div/div[2]/div[1]/form/div/div[2]/div[2]/div/input')
        ActionChains(driver).move_to_element(password).click().send_keys(self.account['password']).perform()

    def check_health(self):
        driver = self.driver
        return True
        #
        # try:
        #     driver.find_element_by_xpath("//*[contains(text(), 'Girls want you')]")
        #     self.log('Найден псевдо бан: Girls want you')
        # except NoSuchElementException:
        #     pass
        # else:
        #     try:
        #         no = driver.find_element_by_xpath("//span[contains(text(), 'No')]//..")
        #         self.scroll_to_elem(no)
        #     except NoSuchElementException:
        #         self.log('Невозможно найти кнопку No на банере Girls Want You')
        #         return True
        #     ac = ActionChains(driver)
        #     try:
        #         ac.move_to_element(no).click().perform()
        #     except ElementNotInteractableException:
        #         self.log('Невозможно нажать на кнопку No банера Girls Want You')
        #         return True
        #
        # try:
        #     driver.find_element_by_xpath("//*[contains(text(), 'A girl wants you')]")
        #     self.log('Найден псевдо бан: A girl wants you')
        # except NoSuchElementException:
        #     pass
        # else:
        #     try:
        #         no = driver.find_element_by_xpath("//span[contains(text(), 'No')]//..")
        #     except NoSuchElementException:
        #         self.log('Невозможно найти кнопку No на банере A girl wants you')
        #         return True
        #     ac = ActionChains(driver)
        #     try:
        #         ac.move_to_element(no).click().perform()
        #     except ElementNotInteractableException:
        #         self.log('Невозможно нажать кнопку No на банере A girl wants you')
        #         return True

    def resolve_alert(self):
        driver = self.driver

        try:
            alert = driver.switch_to.alert()
        except NoAlertPresentException:
            return
        alert.accept()

    def scroll_to_elem(self, elem):
        driver = self.driver

        driver.execute_script("arguments[0].scrollIntoView(true);", elem)

    def highlight(self, element, effect_time, color, border):
        """Highlights (blinks) a Selenium Webdriver element"""
        driver = self.driver

        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)

        original_style = element.get_attribute('style')
        apply_style("border: {0}px solid {1};".format(border, color))
        time.sleep(effect_time)
        apply_style(original_style)

    def log(self, msg):
        logging.info("Thread {0:>2} ".format(self.name) + msg)

    def get(self, url):
        driver = self.driver
        driver.get(url)

        import status_form

        body = driver.find_element(by=By.TAG_NAME, value='body')
        script = "arguments[0].insertAdjacentHTML('afterBegin', arguments[1])"
        driver.execute_script(script, body, status_form.form)

        thread_id = driver.find_element(by=By.ID, value='thread_id')
        self.thread_status = driver.find_element(by=By.ID, value='thread_status')
        thread_product_id = driver.find_element(by=By.ID, value='thread_product_id')
        thread_product_amount = driver.find_element(by=By.ID, value='thread_product_amount')
        thread_start = driver.find_element(by=By.ID, value='thread_start')

        timer_script = driver.find_element(by=By.ID, value='timer_script')
        self.driver.execute_script("eval(arguments[0].innerHTML)", timer_script)

        self.set_status_form_value(thread_id, self.name)
        self.set_status_form_value(thread_product_id, self.product['id'])
        self.set_status_form_value(thread_product_amount, self.product['amount'])
        self.set_status_form_value(thread_start, self.product['startTime'])

    def set_status_form_value(self, elem, value):
        self.driver.execute_script(self.set_value_script, elem, value)


class Binance:
    thread_count = 0
    threads = []
    accounts = []
    proxy = []
    products = []
    script = ''

    def __init__(self, accounts, proxy, products, thread_count=0):
        self.drivers = []
        self.accounts = accounts
        self.proxy = proxy
        self.products = products

        if thread_count == 0:
            count = 1000
        else:
            count = thread_count
        if count > len(accounts):
            count = len(accounts)
        if count > len(proxy):
            count = len(proxy)

        self.thread_count = count

        script_file = open('script.js')
        self.script = script_file.read()
        script_file.close()

    def set_up_chrome(self, index):

        options = webdriver.ChromeOptions()

        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ' \
                     '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        # options.add_argument(f'user-agent={user_agent}')

        mobile_emulation = {
            "deviceName": "iPhone 6/7/8"
        }
        # options.add_experimental_option("mobileEmulation", mobile_emulation)

        # options.add_argument("--use-fake-ui-for-media-stream")
        # options.add_argument("--use-fake-device-for-media-stream")
        # options.add_argument('--use-file-for-fake-video-capture=' + str(Path('webcam.y4m').absolute()))
        # options.add_argument('--use-file-for-fake-audio-capture=' + str(Path('microphone.wav').absolute()))

        options.add_argument(r'--user-data-dir=' + str(Path('data/chrome/profile' + str(index)).absolute()))
        # options.add_argument(r'--profile-directory=Profile ' + str(index + 1))

        # options.add_argument("--load-extension=" + str(Path('ext/hola.crx').absolute()))chrome_options.add_extension(

        service = Service(ChromeDriverManager(log_level=logging.FATAL).install())

        service_args = []
        if not cfg.debug:
            service_args = ['--proxy=' + self.proxy[index]['address'], '--proxy-type=' + self.proxy[index]['type'],
                            '--proxy-auth=' + self.proxy[index]['auth']]

        options.add_argument("--start-maximized")

        return webdriver.Chrome(options=options, service=service, service_args=service_args)

    def run(self, profile=None):
        # display = Display(visible=False, size=(1920, 1080)).start()
        try:
            if profile is None:
                for index in range(0, self.thread_count):
                    self.drivers.append(self.set_up_chrome(index))
            else:
                self.thread_count = 0
                self.drivers.append(self.set_up_chrome(profile))

            for index in range(self.thread_count):
                thread = Browser(self.drivers[index], self.accounts[index], self.products[index], self.script, index)
                self.threads.append(thread)
                thread.start()

            while self.check_threads():
                cmd = input("#: ")
                if cmd == "e" or cmd == "exit":  # выход
                    self.close_all_threads()
                    for index, thread in enumerate(self.threads):
                        thread.join()
                    logging.info("До свидания!")
                elif cmd.startswith("s"):  # скриншот: s[index]
                    if len(cmd) == 1:
                        for index in range(0, self.thread_count):
                            self.drivers[index].save_screenshot("browser-" + str(index) + ".png")
                    else:
                        index = int(cmd[1:])
                        self.drivers[index].save_screenshot("browser-" + str(index) + ".png")
                elif cmd.startswith("v"):  # состояние
                    pass
                elif cmd.startswith("p"):  # пауза: p[index]
                    if len(cmd) == 1:
                        for index in range(0, self.thread_count):
                            self.pause_thread(index)
                    else:
                        index = int(cmd[1:])
                        self.pause_thread(index)
                elif cmd.startswith("r"):  # возобновление: r[index]
                    if len(cmd) == 1:
                        for index in range(0, self.thread_count):
                            self.resume_thread(index)
                    else:
                        index = int(cmd[1:])
                        self.resume_thread(index)
                elif cmd.startswith("rs"):  # перезапустить: rs[index]
                    if len(cmd) == 1:
                        for index in range(0, self.thread_count):
                            self.resume_thread(index)
                    else:
                        index = int(cmd[1:])
                        self.resume_thread(index)
                elif cmd == "hs":  # hotswap
                    self.hotswap()

        except WebDriverException as e:
            logging.error("Что-то пошло не так: " + e.msg)

        # display.stop()

    def hotswap(self):
        import hotswap
        for browser in hotswap.browsers:
            if not (browser['index'] > len(self.drivers)):
                index = browser['index']
                if browser['account'] != {}:
                    self.accounts[index] = browser['account']
                    if browser['proxy'] == {}:
                        self.threads[index].account = browser['account']
                        self.threads[index].signin()
                if browser['proxy'] != {}:
                    self.proxy[index] = browser['proxy']
                    self.restart_thread(index)

    def restart_thread(self, index):
        self.threads[index].stop = True
        self.drivers[index] = self.set_up_chrome(index)
        self.threads[index] = Browser(self.drivers[index], self.accounts[index], self.products[index],
                                      self.script, index)

    def check_threads(self):
        for index, thread in enumerate(self.threads):
            if thread.is_alive():
                return True
        return False

    def close_all_threads(self):
        for index, thread in enumerate(self.threads):
            thread.stop = True

    def pause_thread(self, index):
        self.threads[index].pause = True

    def resume_thread(self, index):
        self.threads[index].pause = False


if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")

    bnc = Binance(cfg.accounts, cfg.proxy, cfg.products, cfg.threadCount)
    bnc.run()
