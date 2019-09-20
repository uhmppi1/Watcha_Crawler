#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os.path
import re
import selenium
# import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
import json
from collections import OrderedDict
import sys
import bs4
import json
import re


# In[4]:

#
# with open('Untitled', encoding = 'utf-8') as json_file:
#     list_before = json.load(json_file)
#
# list_movie = list_before['movieListResult']['movieList']
# len_movie = len(list_movie)
#

# In[301]:


class watcha_crawler(webdriver.Chrome):
    
    def log_in(self, id, password):
        self.get('https://watcha.com/ko-KR')
        now_html = self.page_source
        now_source = BeautifulSoup(now_html, 'lxml')

        #로그인 클릭 하는 코드
        self.find_elements_by_tag_name("li")[1].click()

        now_html = self.page_source
        now_source = BeautifulSoup(now_html, 'lxml')
        # 로그인 정보 넘겨주는 코드
        self.find_element_by_id("sign_in_email").send_keys(id)
        self.find_element_by_id("sign_in_password").send_keys(password)
        self.find_elements_by_tag_name("button")[6].click()
        
    
    def find_matching(self, list_movie, i): # 영화 리스트와 순서를 인풋으로 받으면
        
        count = 0
        name_movie_pre = list_movie[i]['movieNm'].strip() # 영화 리스트에서 매칭 쿼리를 잡고
        name_movie = re.sub(' ','%20',name_movie_pre)
        year_movie = list_movie[i]['prdtYear'].strip()
        nation_movie = list_movie[i]['repNationNm'].strip()
        self.get('https://watcha.com/ko-KR/search?query='+name_movie) # 왓챠에서 영화를 검색해 본다.
        now_html = self.page_source
        now_source = BeautifulSoup(now_html, 'lxml')
        title_prev = now_source.find_all('li', {'class':"css-106b4k6-Self e3fgkal0" }) # 검색 결과 다양한 영화가 나오니 listup을 한다.
        len_same = len(title_prev)
        
        print(name_movie_pre + '에 대한 결과')
        print('정답은 [{}], [{}], [{}]'.format(name_movie_pre, year_movie, nation_movie))

        for j in range(len_same): #제목, 제작년도, 국가를 매칭시켜서 맞는 걸 찾는다.
            try:
                query_title = title_prev[j].a.find_all('div')[2].find_all('div')[0].text.strip()
                query_movie = title_prev[j].a.find_all('div')[2].find_all('div')[1].text.split()[0].strip()
                query_nation = title_prev[j].a.find_all('div')[2].find_all('div')[1].text.split()[2].strip()

                # print('[', query_title, ']')
                # print('[', query_movie, ']')
                # print('[', query_nation, ']')
                # print('[', name_movie_pre, ']')
                # print('[', year_movie, ']')
                # print('[', nation_movie, ']')

                if(query_title == name_movie_pre and query_movie == year_movie and query_nation == nation_movie): # 세 조건이 맞으면
                    print(name_movie_pre + '매칭 성공\n##########################################\n')
                    movie_url = 'https://watcha.com' + title_prev[j].a['href'] # 매칭되는 영화 페이지를 리턴
                    count+=1
                    return movie_url
            except IndexError as e:  # pipaek : 연도나 국가 등의 정보가 없는 데이터가 있어서 이때 오류나지 않도록.
                continue
        
        if(count<1):
            if(len_same<1):
                print('검색 결과가 없음\n##########################################\n')
            else:
                print('검색 결과는 있지만 매칭되는 게 없음\n##########################################\n')
            movie_url = 0
            return movie_url

    def save_synopsis(self, movie_url):
        synopsis = ''
        if(movie_url != 0): # 매칭되는 영화가 있었으면
            try:
                self.get(movie_url)
                now_html = self.page_source
                now_source = BeautifulSoup(now_html, 'lxml')
                synopsis_prev = now_source.find_all('div', {'class':"css-1jyvmaq-ViewMore et86el20"})[0]
                synopsis_prev2 = synopsis_prev.a['href']
                self.get('https://watcha.com' + synopsis_prev2)
                now_html = self.page_source
                now_source = BeautifulSoup(now_html, 'lxml')
                synopsis = now_source.find_all('dd', {'class':"css-77qx4t-SummaryDetail e1kvv3954"})[0].text
            except IndexError as e:  # pipaek : 뜬금없이 synopsis 정보에 아무 내용이 없는 영화도 있다.
                return ""
    
        return synopsis
    
    def save_comments(self, movie_url, num_comments):
        if(movie_url != 0): # 매칭되는 영화가 있었으면
            self.get(movie_url+'/comments')
            for i in range(num_comments//3): #스크롤 내리는 코드. 로그인 해야함. num_comments만큼 댓글 수집. 
                self.execute_script("window.scrollTo(0, document.body.scrollHeight);") #한 번 스크롤에 3개씩 추가. 검증은 해봐야.
                time.sleep(0.1)
            now_html = self.page_source
            now_source = BeautifulSoup(now_html, 'lxml')
            comments_list = now_source.find_all('div', {'class':"css-wnwcvo-Comment e1oskw6f0"}) # 댓글 목록 수집
            how_many = len(comments_list)

            members = []
            
            for i in range(how_many):
                one_member = {}
                # 스포일러가 있는 경우와 없는 경우 나눠서 크롤링
                if str(type(comments_list[i].find('div', {'class': "css-1l07b40-Text-handleRenderInner e1xxz10x0"}))) != "<class 'NoneType'>":
                    one_member['comment'] = (comments_list[i].find('div', {'class': "css-1l07b40-Text-handleRenderInner e1xxz10x0"})).text
                else:
                    one_member['comment'] = comments_list[i].find('div', {'class': "css-v0bib7-Text-handleRenderInner e1xxz10x0"}).text
                one_member['ratings'] = comments_list[i].find_all('span')[0].text
                one_member['like'] = comments_list[i].find_all('em')[0].text
                one_member['dont_like'] = comments_list[i].find_all('em')[1].text
                members.append(one_member)
            
            return members
    
    


# In[302]:


'''wd = "./chromedriver"
crawler = watcha_crawler(wd)


# In[303]:


crawler.log_in('kpdpkp@naver.com','meanimo123') # 댓글 더보기를 하려면 로그인 해야 함.

synopsis = []
comments = []


# In[319]:


all_data = {}


# In[320]:


for i in range(len_movie):
    data_movie = {}
    data_movie['movieName'] = list_movie[i]['movieNm']
    movie_url = crawler.find_matching(list_movie,i)
    data_movie['synopsis'] = crawler.save_synopsis(movie_url)
    data_movie['comments'] = crawler.save_comments(movie_url,100)
    all_data[i] = data_movie


# In[327]:


all_data


# In[328]:


with open('all_data.txt', 'w', encoding = 'utf-8') as make_file:
    json.dump(all_data, make_file, ensure_ascii=False, indent='\t')


# # 스포일러가 있어요 를 누르는 코드. 고생했지만... 필요 없을 듯.
# now_html = crawler.page_source
# now_source = BeautifulSoup(now_html, 'lxml')
# now_source.find_all('button',{'class':'css-1txg5x6-StylelessButton-AcceptSpoilerButton e1xxz10x7'})
# num_spoil = len(now_source.find_all('button',{'class':'css-1txg5x6-StylelessButton-AcceptSpoilerButton e1xxz10x7'}))
# 
# for i in range(num_spoil):
#     crawler.find_elements_by_xpath("//button[@aria-label='Accept Spoiler']")[i].click()'''
