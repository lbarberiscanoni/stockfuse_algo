from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import subprocess
import time
import platform

#options = webdriver.ChromeOptions()
#options.add_argument('--allow-running-insecure-content')
#browser = webdriver.Chrome(chrome_options=options)
#browser.maximize_window()

class Order():

    def __init__(self, browser, account, password):
        self.browser = browser
        self.account = account
        self.password = password

    def brokerLogin(self):
        self.browser.get("https://stockfuse.com/accounts/signin/?next=/#/login")
        try:
            element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modal-dialog")))
            print "found modal"
            time.sleep(1)
            try:
                WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "form-stockfuse-signin")))
                print "switched"
                emailInput = self.browser.find_element_by_id("id_identification")
                emailInput.send_keys(self.account)
                passwordInput = self.browser.find_element_by_id("id_password")
                passwordInput.send_keys(password)
                submitButton = self.browser.find_element_by_id("id_submit")
                i = 0
                while i < 30:
                    try:
                        submitButton.click()
                        submitButton.submit()
                        time.sleep(1)
                        i += 1
                    except:
                        i = 30
                    print i
                print "success"
                self.browser.get("https://stockfuse.com/match/bohv/" + self.account + "#/login")
            except:
                print "fail"
        except:
            print "fail"

    def makeOrder(self, orderType, stockToShort, direction):
        self.browser.refresh()
        print "function triggered"
        #let's put in the order
        #""
        element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "nav-colored-primary")))
        newTradeButton = self.browser.find_element_by_class_name("nav-colored-primary")
        print "trade button found"
        newTradeButton.click()
        print "clicked on New trade"
        time.sleep(1)

        shortSellRadio = self.browser.find_element_by_id("order-" + str(direction))
        print "found radio button"
        shortSellRadio.click()
        print "selected " + str(direction)

        time.sleep(1)
        inputBar = self.browser.find_element_by_css_selector(".ticker-sel .selectize-input input")
        print inputBar
        inputBar.send_keys(stockToShort.upper())
        time.sleep(2)
        inputBar.send_keys(Keys.RETURN)
        print "entered stock"

        time.sleep(2)
        lastPriceInpt = self.browser.find_element_by_class_name("price")
        print "found last price"
        print lastPriceInpt.text
        starting_price = float(lastPriceInpt.text)
        print starting_price

        time.sleep(0.3)
        aum = self.browser.find_element_by_class_name("order-form-account-value")
        aum = float(aum.text.replace(",", ""))
        aum = float(aum - 1000)
        tradeSize = float(aum / float(starting_price))
        tradeSize = int(round(tradeSize))
        print "doing a trade of " + str(tradeSize)

        time.sleep(0.2)
        qtyInput = self.browser.find_element_by_name("order-quantity")
        qtyInput.send_keys(tradeSize)
        print "entered qty"

        if orderType == "limit":
            limitOrderInput = self.browser.find_element_by_xpath("//select[@name='order-type']/option[text()='Limit']")
            limitOrderInput.click()
            print "clicked on limit order"
            time.sleep(0.2)
            limitOrderInput = self.browser.find_element_by_xpath("//input[@name='order-limit-price']")
            limitOrderInput.send_keys(str(starting_price))
            print "submitted price limit"
        else:
            print "market is the default"

        time.sleep(0.2)
        rationalTextArea = self.browser.find_element_by_name("order-comment")
        rationalTextArea.send_keys("it's a good call")
        print "entered rationale"

        time.sleep(1)
        submitButton = self.browser.find_element_by_class_name("btn-place-order")
        submitButton.click()
        print "success"

        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "alert-container")))
        confirmation = confirm(self.browser)

        return confirmation

    def confirm(self):
        i = 0
        confirmation = ""
        while i < 1:
            alert = self.browser.find_element_by_class_name("alert-container")
            confirmation = alert.text.split("\n")[1].strip()
            confirmation = str(confirmation)
            if confirmation != "Working on your order...":
                i = 1

        return confirmation

    def exitAllTrades(self):
        closeBtn = self.browser.find_elements_by_css_selector(".btn-close-constituent .pointer")
        print len(closeBtn)
        x = 1
        while x <= len(closeBtn):
            btn = self.browser.find_element_by_css_selector("#constituent-" + str(x) + " .btn-close-constituent .pointer")
            btn.click()
            time.sleep(1)
            self.browser.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            submitClosingBtn = self.browser.find_element_by_css_selector(".modal-footer .btn-place-order")
            submitClosingBtn.click()
            time.sleep(1)
            x += 1

    def exitLimit(self):
        closeBtn = self.browser.find_elements_by_css_selector(".btn-close-constituent .pointer")
        print len(closeBtn)
        x = 1
        while x <= len(closeBtn):
            btn = self.browser.find_element_by_css_selector("#constituent-" + str(x) + " .btn-close-constituent .pointer")
            btn.click()
            time.sleep(1)
            price = self.browser.find_element_by_class_name("price").text
            orderTypeBtn = self.browser.find_element_by_name("order-type")
            orderTypeBtn.send_keys("Limit")
            limitPriceInpt = self.browser.find_element_by_name("order-limit-price")
            limitPriceInpt.send_keys(str(float(price) * 0.998))
            self.browser.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            submitClosingBtn = self.browser.find_element_by_css_selector(".modal-footer .btn-place-order")
            submitClosingBtn.click()
            time.sleep(1)
            x += 1

    def closeOrder(self, account):
        self.browser.get("https://stockfuse.com/match/bohv/" + str(account) + "#/chatbase")
        time.sleep(1)
        try:
            chatBtn = self.browser.find_element_by_class_name("chat-close")
            chatBtn.click()
            time.sleep(2)
            #exitAllTrades(self.browser)
            exitLimit(self.browser)
        except:
            print "chat already closed"
            #exitAllTrades(self.browser)
            exitLimit(self.browser)

    def order_test():
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()

        brokerLogin(self.browser, "leggenda")
        time.sleep(2)
        try:
            confirmation = makeOrder(self.browser, "aapl", "buy")
            ticker = "aapl".upper()
            if confirmation == "Your order to buy " + ticker + " has been queued" or "You order has been accepted":
                print confirmation
            else:
                raise Exception(confirmation)
        except Exception as e:
            print e
            confirmation = makeOrder(self.browser, "aapl", "buy")
            print confirmation
        time.sleep(5)
        self.browser.close()
        #closeOrder()

    def closing_test():
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()

        brokerLogin(self.browser, "leggenda")
        time.sleep(2)
        self.browser.get("https://stockfuse.com/match/bohv/leggenda#/chatbase")
        chatBtn = self.browser.find_element_by_class_name("chat-close")
        chatBtn.click()
        time.sleep(2)
        exitLimit(self.browser) 
