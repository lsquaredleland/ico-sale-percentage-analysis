import time
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import requests
import csv
import datetime

url = 'https://icodrops.com/ico-stats/'

browser = webdriver.PhantomJS()
browser.get(url)
time.sleep(2)

lastHeight = browser.execute_script("return document.body.scrollHeight")
print('lastHeight', lastHeight)
while True:
	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(1)
	newHeight = browser.execute_script("return document.body.scrollHeight")
	if newHeight == lastHeight:
		break
	lastHeight = newHeight

soup = BeautifulSoup(browser.page_source, "html.parser")
icos = soup.findAll("a", {'id': 'n_color'})


def clean(input):
	return re.sub("[^0-9.]", "", input)


def raised(input):
	try:
		return clean(input.find('div', class_='goal-in-card').find('span').text.strip())
	except:
		return '-'


def ico_price(input):
	try:
		return clean(input.find('div', class_='token_pr').findAll('div')[1].text.strip())
	except:
		return '-'


def subpage_data(url):
	percent = '-'
	goal = '-'
	date = '-'
	html = requests.get(url).content
	soup = BeautifulSoup(html, "lxml")
	try:
		percent = soup.findAll('div', class_='col-12 col-md-6')[1].findAll('li')[-1].text
		if 'Available for Token Sale' in percent:
			percent = str.replace(re.sub("[^0-9.,]", "", percent), ',', '.')
		else:
			percent = '-'
	except:
		percent = '-'

	try:
		text = soup.find('div', class_='ico-right-col')
		goal = clean(text.find('div', class_="goal").text.split("(")[0].strip())
	except:
		goal = '-'

	try:
		text = soup.find('div', class_='ico-right-col')
		date = text.find('div', class_="sale-date").text.strip()
	except:
		date = '-'

	return [percent, goal, date]

columns = ['name', 'percent_sold', 'url', 'date', 'raised', 'goal', 'ico_price', 'curr_price', 'usd_roi', 'eth_roi', 'btc_roi']
data = []

for ico in icos:
	name = ico.find('h3').text.strip()
	url = ico['href']
	[percent_sold, goal, date] = subpage_data(url)
	curr_price = clean(ico.find('div', class_='usd-price').findAll('div')[1].contents[0])
	usd_roi = clean(ico.find('div', class_='st_r_usd').findAll('div')[1].contents[0])
	eth_roi = clean(ico.find('div', class_='st_r_eth').findAll('div')[1].contents[0])
	btc_roi = clean(ico.find('div', class_='st_r_btc').findAll('div')[1].contents[0])

	line = [name, percent_sold, url, date, raised(ico), goal, ico_price(ico), curr_price, usd_roi, eth_roi, btc_roi]
	print(line)
	data.append(line)


now = datetime.datetime.now()
date = now.strftime("%Y_%m_%d")

with open("ico_sale_data_" + date + ".csv", "w+") as my_csv:
	csvWriter = csv.writer(my_csv, delimiter=',')
	csvWriter.writerow(columns)
	csvWriter.writerows(data)
