# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 19:08:45 2023

@author: shubh
"""

import os
from selenium import webdriver
import pymongo
import time
from bs4 import BeautifulSoup
import requests
import re
import json
import pandas as pd

#change directory as per requirement. 
#Please ensure chromedriver is in the specified directory
def change_working_directory():
    path = input("Please enter the directory and ensure that chrome driver is in the directory (without quotes): ")
    os.chdir(path)
    wd = os.getcwd()
    print(f"Changed working directory to: {os.getcwd()}")
    return wd

wd = change_working_directory()

#2
def part_2(wd):
    chrome_driver_path = os.path.join(wd,'chromedriver')
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    driver.get("https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold")
    for i in range(8):
        elements = driver.find_elements_by_class_name("sc-29427738-0.sc-e7851b23-1.dVNeWL.hfa-DJE.Asset--loaded")
        element = elements[i]
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        time.sleep(20)
        with open(f'bayc_{i+1}.html','w',encoding = 'utf-8') as f:
            f.write(driver.page_source)
        driver.back()
    driver.quit()
part_2(wd)

#3
def part_3(wd):
    #change if required
    username = 'shubham1510'
    password = 'SK1510'
    con = 'mongodb+srv://' + username + ':' + password + '@cluster0.bv6w4n5.mongodb.net/?retryWrites=true&w=majority'
    client=pymongo.MongoClient(con)
    db = client['individual_assignment_2']
    collection = db['bayc']
    soups = []
    ape_names = []
    attributes = {}
    for i in range(1,9):
        filename = f"bayc_{i}.html"
        filepath = os.path.join(wd, filename)
        pages = open(filepath,'r', encoding = 'utf-8').read()
        soups.append(BeautifulSoup(pages,'html.parser'))
        ape_names.append(soups[i-1].find('h1', {'class': 'sc-29427738-0 hKCSVX item--title'}).text.strip())
        soup = BeautifulSoup(pages,'html.parser')
        divs = soup.find_all('div', {'class': 'sc-d6dd8af3-0 hkmmpQ item--property'})
        text = [div.text for div in divs]
        attributes[ape_names[i-1]] = text
        df = pd.DataFrame.from_dict(attributes, orient='index')
        df = df.rename(columns=lambda x: f'trait_{x+1}')
        df = df.reset_index().rename(columns={'index': 'ape_id'})
        df_dict = df.to_dict('records')
        collection.insert_many(df_dict)
part_3(wd)

#4
def part_4(wd):
    url = 'https://www.yellowpages.com/search?'
    params = {'search_terms':'pizzeria','geo_location_terms':'San Francisco, CA'}
    response = requests.get(url, params=params,headers ={"user-agent": "Mozilla/5.0"})
    with open('sf_pizzeria_search_page.html', 'w', encoding = 'utf-8') as f:
        f.write(response.text)
        f.close()
part_4(wd)
#5
def part_5(wd):
    page = open('sf_pizzeria_search_page.html','r', encoding = 'utf-8').read()
    soup = BeautifulSoup(page,'html.parser')
    business_number_element = soup.find_all('h2', {'class': 'n'})
    business_class_name = soup.find_all('a', {'class': 'business-name'})
    name = [i.text.strip() for i in business_class_name]
    search_rank = [i.text.strip().split('.')[0] for i in business_number_element]
    url = []
    for a in soup.find_all('a',{'class':"business-name"}, href=True):
        url.append(a['href'])
    for i in range(len(url)):  
        url[i] = 'https://www.yellowpages.com' + url[i]
    restaurants = soup.find_all('div', class_='result')
    restaurant = [i.text.strip() for i in restaurants]
    dollar_signs = []
    for i in range(len(restaurant)):
        dollar_signs.append(re.findall('\${1,5}', restaurant[i]))
    rating=[]
    reviews_count = []
    trip_advisor_rating = []
    trip_advisor_reviews_count = []
    years_in_business = []
    amenities = []
    review = []
    for i in range(len(restaurants)) :
        try:
            rating.append(restaurants[i].find('div', {'class': 'ratings',}).find('div')['class'][1:])
        except:
            rating.append(None)
        try:
            reviews_count.append(restaurants[i].find('div', {'class': 'ratings',}).find('span',{'class':'count'}).text.strip('()'))
        except:
            reviews_count.append(None)
        try:
            ta_rating = restaurants[i].find('div', {'class': 'ratings', 'data-tripadvisor': True})
            trip_advisor_rating.append(json.loads(ta_rating['data-tripadvisor'])['rating'])
        except:
            trip_advisor_rating.append(None)
        try:
            ta_n_reviews = restaurants[i].find('div', {'class': 'ratings', 'data-tripadvisor': True})
            trip_advisor_reviews_count.append(json.loads(ta_n_reviews['data-tripadvisor'])['count'])
        except:
            trip_advisor_reviews_count.append(None)
        try:
            years_in_business.append(restaurants[i].find('div', {'class': 'years-in-business',}).find('div',{'class':'number'}).text.strip('()'))
        except:
            years_in_business.append(None)
        try:
            amenities_tag = restaurants[i].find('div', {'class': 'amenities-info',})
            amenities.append(', '.join(amenities_tag.text.strip().split(', ')))
        except:
            amenities.append(None)
        try:
            review.append(restaurants[i].find("div",{"class":"snippet"}).text)
        except:
            review.append(None)
    df = pd.DataFrame({'rating': rating[1:31],
        'reviews_count': reviews_count[1:31],
        'trip_advisor_rating': trip_advisor_rating[1:31],
        'trip_advisor_reviews_count': trip_advisor_reviews_count[1:31],
        'years_in_business': years_in_business[1:31],
        'amenities': amenities[1:31],
        'review': review[1:31],
        'url': url[1:31],
        'search_rank': search_rank[1:31],
        'name': name[1:31],
        'dollar_signs':dollar_signs[1:31]})
    df['dollar_signs'] = df['dollar_signs'].str[0]
    df["rating"]= df["rating"].str.join(" and ")
    df['reviews_count'] = df['reviews_count'].str.extract('(\d+)').astype(float)
    df['trip_advisor_rating'] = pd.to_numeric(df['trip_advisor_rating'])
    df['trip_advisor_reviews_count'] = df['trip_advisor_reviews_count'].astype(float)
    df['years_in_business'] = df['years_in_business'].astype(float)
    df['search_rank'] = df['search_rank'].astype(float)
    return df
df = part_5(wd)

#6
def part_6(df):
    df_dict = df.to_dict('records')
    username = 'shubham1510'
    password = 'SK1510'
    con = 'mongodb+srv://' + username + ':' + password + '@cluster0.bv6w4n5.mongodb.net/?retryWrites=true&w=majority'
    client=pymongo.MongoClient(con)
    db = client['individual_assignment_2']
    collection = db['sf_pizzerias']
    collection.insert_many(df_dict)
    return con
con = part_6(df)

#7
def part_7(con):
    client=pymongo.MongoClient(con)
    db = client['individual_assignment_2']
    collection = db['sf_pizzerias']
    url = []
    search_rank = []
    for doc in collection.find():
        url.append([doc['url']])
        search_rank.append([doc['search_rank']])
    search_rank_new = []
    for item in search_rank:
        search_rank_new += item
    search_rank_new = [int(i) for i in search_rank_new]
    url_new = []
    for item in url:
        url_new += item
    html_files = []
    for i in range(30):
        html_files.append('sf_pizzerias_' + str(format(search_rank_new[i], '02') +".html"))
        page = requests.get(url_new[i],headers ={"user-agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")
        with open(html_files[i], "w", encoding = 'utf-8') as file:
            file.write(str(soup.prettify()))
            file.close()
        time.sleep(10)
    return html_files
html_files = part_7(con)

#8
def part_8(html_files):
    address = []
    phone = []
    website = []
    soups = []
    for i in range(len(html_files)):
        url = open(html_files[i], "r", encoding = 'utf-8').read()
        soups.append(BeautifulSoup(url, "html.parser"))
        address.append(soups[i].find("section", {"id": "details-card"}).find_all('p')[1].text.split(': '))
        phone.append(soups[i].find("section", {"id": "details-card"}).find("p",{"class":"phone"}).text.split(':  '))
        try:
            website.append(soups[i].find("p", {"class": "website"}).text.split(': '))
        except:
            website.append(None)
    cleaned_addresses = []
    for i in address:
        cleaned_address = i[0].replace('\n','').replace('Address:','').strip()
        cleaned_addresses.append(cleaned_address)
    cleaned_phone = []
    for i in phone:
        cleaned_phones = i[0].replace('\n','').replace('Phone:','').strip()
        cleaned_phone.append(cleaned_phones)
    cleaned_website = []
    for i in website:
        if i:
            cleaned_websites = i[0].replace('\n','').replace('Website:','').strip()
            cleaned_website.append(cleaned_websites)
        else:
            cleaned_website.append(None)

    df = pd.DataFrame({'address': cleaned_addresses,
                       'phone': cleaned_phone,
                       'website': cleaned_website})
    return df
df = part_8(html_files)

#9
def part_9(df):
    address = list(df['address'])
    phone = list(df['phone'])
    website = list(df['website'])
    url = 'http://api.positionstack.com/v1/forward'
    params = {"access_key": "ee76ae35b91eb738fe7473778625debd"}
    headers ={"user-agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    username = 'shubham1510'
    password = 'SK1510'
    con = 'mongodb+srv://' + username + ':' + password + '@cluster0.bv6w4n5.mongodb.net/?retryWrites=true&w=majority'
    client=pymongo.MongoClient(con)
    db = client['individual_assignment_2']
    collection = db['sf_pizzerias']    
    longitude = []
    latitude = []
    for i in range(len(address)):
        params["query"] = address[i]
        page = requests.get(url, params=params)
        location = page.json()
        latitude.append(location['data'][0]['latitude'])
        longitude.append(location['data'][0]['longitude'])
    df['longitude'] = longitude
    df['latitude'] = latitude
    df_dict = df.to_dict('records')
    for i in range(len(address)):
        collection.update_one({'search_rank': float(i+1)}, {'$set': {'latitude': latitude[i], 'longitude': longitude[i], 'phone': phone[i], 'website': website[i],'address': address[i]}})
part_9(df)
