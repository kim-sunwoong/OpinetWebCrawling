from selenium import webdriver
import pandas as pd
import numpy as np
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from glob import glob
import os
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
from time import gmtime, strftime

driver = webdriver.Chrome(service = Service("/home/sunnypc/dev_ws/driver/chromedriver"))
url = 'https://www.opinet.co.kr/searRgSelect.do'
driver.get(url)


sido = driver.find_element(By.ID , 'SIDO_NM0')
sido_list = sido.find_elements(By.TAG_NAME, 'option')
sido_names =[sido.get_attribute('value') for sido in sido_list]
sido_names = sido_names[1:]

gu = driver.find_element(By.ID, 'SIGUNGU_NM0')
gu_tag_list = gu.find_elements(By.TAG_NAME, 'option')
gu_names = [gu.get_attribute('value') for gu in gu_tag_list]
gu_names = gu_names[1:]

gas_level_temp = driver.find_element(By.ID , 'templ_list0')
gas_level = gas_level_temp.find_element(By.TAG_NAME , 'ul')
gas_level = gas_level.find_elements(By.TAG_NAME , 'li')


FINAL_DF = pd.DataFrame()
dt_list = []

# Each City
for each_sido in sido_names:
    # print(f'현재 작업중인 도시 : {each_sido}')
    sido = driver.find_element(By.ID , 'SIDO_NM0')
    sido.send_keys(each_sido)
    time.sleep(0.1)

    gu = driver.find_element(By.ID, 'SIGUNGU_NM0')
    gu_tag_list = gu.find_elements(By.TAG_NAME, 'option')
    gu_names = [gu.get_attribute('value') for gu in gu_tag_list]
    gu_names = gu_names[1:]


    # Each gu
    for each_gu in gu_names:
        #print(f'    현재 작업중인 구 : {each_gu}')
        gu = driver.find_element(By.ID, 'SIGUNGU_NM0')
        driver.implicitly_wait(0.1)
        gu.send_keys(each_gu)

        gas_level_temp = driver.find_element(By.ID , 'templ_list0')
        gas_level = gas_level_temp.find_element(By.TAG_NAME , 'ul')
        gas_level = gas_level.find_elements(By.TAG_NAME , 'li')

        # Loop for each gas type tab
        for each_gas_level in range(len(gas_level)):
            gas_level[each_gas_level].click()

            # First tab has id tag 'os_price2'
            # and second tab has id tag 'os_price1'
            # thus some condition
            if each_gas_level+1 == 1:
               id_num = 2
            elif each_gas_level+1 == 2:
                id_num = 1
            elif each_gas_level+1 == 3:
                id_num = 3
            elif each_gas_level+1 == 4:
                id_num = 4

            # Check for id_num
            # print(f'id_num: {id_num}')

            _info_temp = gas_level_temp.find_element(By.ID, f'os_price{id_num}')

            body_info = _info_temp.find_element(By.ID , f'body{id_num}')
            gas_station_Name = body_info.find_elements(By.TAG_NAME, 'a')


            for each_row in gas_station_Name:
                gen_info = []
                
                #Insert sido and gu info for every each row
                gen_info.append(each_sido)
                gen_info.append(each_gu)

                each_row.click()

                # Since there is possibility of getting unexpected popup or window
                # Try for Class 'w_i' (in this case legal station)
                try:
                    WebDriverWait(driver, 0.01).until(EC.presence_of_element_located((By.CLASS_NAME, "w_i")))
                    driver.find_element(By.CLASS_NAME, "w_i").click()
                    station = driver.find_element(By.ID, 'vlt_os_nm').text
                    address = driver.find_element(By.ID, 'vlt_addr').text
                    gen_info.append(station)
                    gen_info.append('')
                    gen_info.append(address)
                    gen_info.append('불법')

                # Otherwise loop as normal
                except TimeoutException:

                    # Getting information from the popup window (potential for more info)
                    # Station Name
                    station_temp = driver.find_element(By.ID , 'os_nm')
                    station = station_temp.get_attribute('innerText')
                    gen_info.append(station)
                    # Tel
                    phone_temp = driver.find_element(By.ID , 'phn_no')
                    phone = phone_temp.get_attribute('innerText')
                    gen_info.append(phone)
                    # Address
                    address_temp = driver.find_element(By.ID , 'rd_addr')
                    address = address_temp.get_attribute('innerText')
                    gen_info.append(address)
                    # INC
                    inc_temp = driver.find_element(By.ID , 'poll_div_nm')
                    inc = inc_temp.get_attribute('innerText')
                    gen_info.append(inc)
                    # Prices (for Primier, Regular, Diesel, Kerosene)
                    infoTbody = driver.find_element(By.ID , 'infoTbody')
                    gas_type_temp = infoTbody.find_elements(By.TAG_NAME, 'tr')
                    
                    price_info = ['','','','']     
                    # Each price
                    for each in gas_type_temp:
                        gas_str = each.find_element(By.CLASS_NAME, 'nobd_l').get_attribute('innerText')
                        if gas_str == '고급휘발유':
                            price_temp = infoTbody.find_element(By.ID , 'b034_p')
                            price_info[0] = price_temp.get_attribute('innerText')
                        elif gas_str == '보통휘발유':
                            price_temp = infoTbody.find_element(By.ID , 'b027_p')
                            price_info[1] = price_temp.get_attribute('innerText')
                        elif gas_str == '경유':
                            price_temp = infoTbody.find_element(By.ID , 'd047_p')
                            price_info[2] = price_temp.get_attribute('innerText')
                        elif gas_str == '등유':
                            price_temp = infoTbody.find_element(By.ID , 'c004_p')
                            price_info[3] = price_temp.get_attribute('innerText')
                    row_info = gen_info+price_info
                    dt_list.append(row_info)
gas_station = pd.DataFrame(dt_list)

column_list = ['City', "Gu" , 'Gas_Station', 'Tel', 'Address', 'Inc','Pre','Reg','Die','Ker']
gas_station.columns = column_list

# Replace ',' for price value
gas_station['Pre'] = gas_station['Pre'].str.replace(',','')
gas_station['Reg'] = gas_station['Reg'].str.replace(',','')
gas_station['Die'] = gas_station['Die'].str.replace(',','')

# Only unique stations
gas_station = gas_station.drop_duplicates(subset=["Gas_Station"])

# Save
path = '/home/sunnypc/dev_ws/eda/data'
time = str(strftime("%Y-%m-%d", gmtime()))
gas_station.to_csv(f'{path}/GasStation_{time}.csv')gas_station.to_csv(f'{path}/GasStation.csv')

                
                
