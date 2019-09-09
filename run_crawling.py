import os
import json
import shutil
from watcha_crawling import watcha_crawler


data_dir = './movielist'
data_finished_dir = './movielist_finished'
data_to_save_dir = './data'


def crawl_one_list(crawler, movielist_file):
  all_data = {}

  file_path_to_read = os.path.join(data_dir, movielist_file)
  file_path_finished = os.path.join(data_finished_dir, movielist_file)
  with open(file_path_to_read, 'r', encoding='utf-8') as f:
    list_before = json.load(f)
    list_movie = list_before['movieListResult']['movieList']
    len_movie = len(list_movie)

    for i in range(len_movie):
      data_movie = {}
      data_movie['movieName'] = list_movie[i]['movieNm']
      movie_url = crawler.find_matching(list_movie, i)
      data_movie['synopsis'] = crawler.save_synopsis(movie_url)
      data_movie['comments'] = crawler.save_comments(movie_url, 100)
      all_data[i] = data_movie

  file_path_to_save = os.path.join(data_to_save_dir, 'data_'+movielist_file)

  with open(file_path_to_save, 'w', encoding='utf-8') as make_file:
    json.dump(all_data, make_file, ensure_ascii=False, indent='\t')

  shutil.move(file_path_to_read, file_path_finished)


#
#
wd = "./chromedriver"
crawler = watcha_crawler(wd)

crawler.log_in('kpdpkp@naver.com', 'meanimo123')  # 댓글 더보기를 하려면 로그인 해야 함.

#
#
#
file_list = os.listdir(data_dir)
file_list.sort()

for file in file_list:
  crawl_one_list(crawler, file)

# with open('./movielist/curPage=1&itemPerPage=100&prdtStartYear=2016&prdtEndYear=2016.json', 'r', encoding='utf-8') as f:
#   list_before = json.load(f) #json.loads(f.read())
#   # sss = f.read(100)
#   # sss = sss.encode('utf-8').decode('unicode_escape')
#   # # sss = sss.decode('unicode_escape')
#   # print(sss)
#   print(list_before)