from selenium import webdriver
import time
 
## remember to input your own file path to your chrome driver here if you're using chrome
#browser = webdriver.Chrome(C:\RealSoftwares\chromedriver_win32")

#disabling cookies on the site
fp = webdriver.FirefoxProfile()
fp.set_preference("network.cookie.cookieBehavior", 2)
browser = webdriver.Firefox(firefox_profile=fp)

browser.maximize_window()
url = 'https://www.allabolag.se/'
browser.get(url)
 
multi_screen_data_search = browser.find_element_by_xpath("//input[@name='what']")
multi_screen_data_search.send_keys("SOBI") #Take name from excelsheet for searching

button = browser.find_element_by_xpath('//button[normalize-space()="Sök"]')
button.click()

links = browser.find_elements_by_partial_link_text('(publ)')

for link in links:
	myLink = link.get_attribute("href")	
	link.click()

links = browser.find_elements_by_partial_link_text('Visa styrelsen')
for link in links:
	myLink = link.get_attribute("href")	
	link.click()

browser.implicitly_wait(10)

name = browser.find_element_by_xpath("//table[@class='table--background-separator company-table color-theme-2']/tbody/tr/th/span/span/span").get_attribute("innerHTML")	
val = browser.find_element_by_xpath("//table[@class='table--background-separator company-table color-theme-2']/tbody/tr/td[1]").get_attribute("innerHTML")
print(name+ " : "+ val)

place = browser.find_element_by_xpath("//div[@class='cc-flex-grid']/div[2]/dl/dt[3]").get_attribute("innerHTML")
value = browser.find_element_by_xpath("//div[@class='cc-flex-grid']/div[2]/dl/dd[3]").get_attribute("innerHTML")
print(place+ " : "+ value)








		
