import requests
import time
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
from bs4 import BeautifulSoup
from collections import Counter
from pylab import mpl
import pkuseg#北大分词库，实现代码在注释中(不好用)
import pprint
import jieba 
mpl.rcParams['font.sans-serif'] = ['STZhongsong']#指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False

user_id = []
comment2 = []
rating = []
useful = []
count1 = 0
bar_width=0.2
movie_rating = 0

def get_html(url):#获取页面
    try:
        json_kv = {'user-agent':'Mozill/5.0'}
        r = requests.get(url,headers = json_kv,timeout = 30)
        r.raise_for_status()
        if r.status_code == 200:
            pass
        r.encoding = 'utf-8'      
        return r.text.replace('<br>','')
    except:
        return 'error'

def gte_serch_name():#获取电影名
    try:
        print('请输入电影名：',end = '')
        a = str(input())
        print('')           
        start_url = 'https://www.douban.com/search?q='+a
        html_code_1 = get_html(start_url)
        if html_code_1 == 'error':
            return 'error'
        
        url_1 = analyze_html_1(html_code_1)
        if url_1 == 'error':
            return 'error'
        
        html_code_2 = get_html(url_1)
        if html_code_2 == 'error':
            return 'error'

        html_code_3 = analyze_html_2(html_code_2)
        if html_code_3 == 'error':
            return 'error'
        else:
            return '1'
    except:
        return 'error'

def analyze_html_3(html_code,url):#解析第三次获得的url（获取更多评价，id，推荐程度，支持度......）
    try:
        soup = BeautifulSoup(html_code,"lxml")
        global count1
        global comment2
        count3 = 0
        for i in soup.find_all('div',class_ = 'comment'):

            u = str(i.find('span',class_ = 'short').get_text())#获取用户评价内容
            u.replace(' ','')
            if len(u) > 0:
                comment2.append(u)
            else:
                comment2.append(np.nan)

            count3 = count3 + 1            
            f = i.find('span',class_ = 'votes')#获取该用户的评论的"有用"数
            h = f.get_text()
            h.replace(' ','')
            useful.append(str(h))

            count = 0
            for j in i.find_all('a'):#获取用户id
                count = count + 1
                if count == 2:
                    v = j.string
                    v.replace(' ','')
                    user_id.append(str(v))
                    break
                else:
                    continue

            count = 0
            for j  in i.find_all('span'):#获取用户的推荐分数
                count = count + 1
                t = str(j.get('class'))
                if count == 5:                    
                    h = re.findall('\d+',t)
                    if len(h) > 0:
                        rating.append(str(h[0]))
                    else:
                        rating.append('99')
                    break
                else:
                    continue

            count1 = count1 + 1

            if count3  == 20:
                break                

        try:#解析下一页url并嵌套解析
            g = soup.find('a',class_ = 'next')
            f = str(g.get('href'))
            if count1 <= 200:#获得的数量+-20（ps：未登录爬取。200为最大值！！！！！）
                if len(f) >= 15:
                    l = re.findall('\d+',url)
                    url_next = 'https://movie.douban.com/subject/'+str(l[0])+'/comments'+f
                    analyze_html_3(get_html(url_next),url_next)
            else:
                print('')
        except:
            return 'error'
        return '1'

    except:
        return 'error'

def analyze_html_2(html_code):#解析第二次获得的htnl代码
    global movie_rating
    try:
        soup = BeautifulSoup(html_code,"lxml")

        for i in soup.find_all('span',class_ = 'pl'):
            try:
                p = i.find('a')
                t = p.string
                num = re.findall('\d+',t)
                a = int(num[0])
                if a > 10000:
                    url_2 = p.get('href')
                    break
            except:
                continue
        print('......')
        print('')

        for movie_name in soup.find_all('title'):#获取爬到的电影标题
            name = movie_name.string
            if len(name):
                break    
        str(name)

        for score1 in soup.find_all('strong'):#获取爬到的电影分数
            score = score1.string
        print('电影名：',name.replace(' ',''),'分数为：',score,sep = '')
        movie_rating = score
        print('')

        jianjie = str(soup.find('span',property='v:summary').get_text())#获取爬到的电影简介
        print('电影简介：',jianjie.replace(' ',''),sep = '')

        time.sleep(6)

        for i in soup.find_all('div',class_ = 'comment'):#获取用户id，推荐分数，评价内容

            count = 0
            for j in i.find_all('a'):#获取用户id
                count = count + 1
                if count == 2:
                    user_id1 = str(j.string)
            
            count = 0
            for j  in i.find_all('span'):#获取用户推荐分数
                count = count + 1
                t = str(j.get('class'))
                if count == 5:
                    rating1 = re.findall('\d+',t)
                    break
                else:
                    continue
            a = int(rating1[0])

            comment1 = str(i.find('span',class_ = 'short').get_text())#获取用户评价内容

            print('用户id：',user_id1.replace(' ',''))
            
            if a == 50:
                print('推荐程度：⭐ ⭐ ⭐ ⭐ ⭐')

            elif a == 40:
                print('推荐程度：⭐ ⭐ ⭐ ⭐')

            elif a == 30:
                print('推荐程度：⭐ ⭐ ⭐')

            elif a == 20:
                print('推荐程度：⭐ ⭐')

            elif a == 10:
                print('推荐程度：⭐')

            elif a == 0:
                print('推荐程度：')
            else:
                print('推荐程度：','error!!')

            print('评价内容：',comment1.replace(' ',''))
            print('')

        y = analyze_html_3(get_html(url_2),url_2)
        if y == 'error':
            return 'error'
        else:
            return '1'

    except:
        return 'error'

def analyze_html_1(html_code):#从主搜索页面获得第一行搜索url
    try:
        count = 0
        soup = BeautifulSoup(html_code,"html.parser")

        for i in soup.find_all('a'):#获得搜索结果的第一条url
            count = count + 1
            if count == 37:
                return i.get('href')
            
    except:
        return 'error'

def show():#统计结果
    global movie_rating
    c = float(movie_rating)
    print('成功爬取!!')
    print('')
    print('共',len(user_id),'个用户id',sep = '')
    print('')
    print('共',len(rating),'个用户评分',sep = '')
    print('')
    print('共',len(useful),'个“有用”数',sep = '')
    print('')
    return

def analyze_data():#画词云
    s = "".join(comment2)#评论合并
    cut_text = " ".join(jieba.cut(s))
    #    font = r'C:\\Windows\\fonts\\SourceHanSansCN-Regular.otf' 
    cloud = WordCloud(
        scale = 45,#清晰度        
        font_path = 'simhei.ttf',#设置字体，不指定就会出现乱码        
        background_color = 'white',#设置背景色        
        max_words = 180,#允许最大词汇
        collocations = False, #避免重复单词        
        max_font_size = 80,#最大号字体
        min_font_size = 10,#字体最小值
        #mask=pic, #造型遮盖
    )
    word_cloud = cloud.generate(cut_text) # 产生词云
    word_cloud.to_file("pjl_cloud4.jpg") #保存图片
    # 显示词云图片
    plt.imshow(word_cloud)
    plt.axis('off')#隐藏坐标轴
    plt.show()
    return

def show_p():#画柱状图
    d = []
    e = []

    for i in range(len(rating)):
        e.append(int(rating[i]))
        d.append(int(useful[i]))

    for x, y in enumerate(d):
        plt.text(x + bar_width, y + 100, '%s' % y, ha='center', va='bottom')

    plt.bar(range(len(d)),d,fc = 'r')
    plt.title("电影评论分析")
    plt.xlabel("评论数")
    plt.ylabel("有用数")
    plt.show()
    return

def main():#main函数
    i = 1
    while i == 1:
        x = gte_serch_name()
        if x == 'error':
            print('')
            print('出错了,换部电影试试！')
            print('')

        else:
            show()
            print('是否分析结果? (输入 y 或 n)')
            w = str(input())
            if w == 'y':
                analyze_data()
                show_p()
                print('')
                print('完成！！')
            else:
                pass            
            i = 0 
            
if __name__ == "__main__":
    main()

'''
s='中文：123456aa哈哈哈bbcc'
s = s.encode('UTF-8')
print(s)
'''
#print(movie_name)
    #movie_name = movie_name.encode()
    #movie_name = movie_name.dncode('UTF-8')
    #print(movie_name)
    #name=re.findall('[\u4e00-\u9fa5]+',movie_name)

#        for i in soup.find_all('span'):
#            j = i.get('property')
#            if j == 'v:summary':
#                jianjie = str(i.string)
#                break

#                if t == 'allstar50 rating':
#                    rating = str(j.get('title'))
#                elif str(j.get('class')) == 'allstar40 rating':
#                    rating = str(j.get('title'))
#                else:
#                    rating = '空！'
#                    continue

#            try:
#                rating1 = i.find('span',class_ = 'allstar50 rating')               
#                rating = str(rating1.get('title'))
#            except:
#                rating1 = i.find('span',class_ = 'allstar40 rating')
#                rating = str(rating1.get('title'))

#            try:#解析下一页url并嵌套解析
#                g = soup.find('a',class_ = 'next')
#                f = str(g.get('href'))
#                url_next = 'https://movie.douban.com/subject/27119724/comments?status=P'+f
#                print('next url：',url_next)
#                analyze_html_3(get_html(url_next))
#                if count1 == 100:
#                    print(user_id)
#                    print(rating)
#                    print(useful)
#                    return '1'
#            except:
#                continue

#        count1 = 0
#        for i in soup.find_all('div',class_ = 'comment'):
#            count1 = count1 + 1
#            if count1 == 1:
#                print(i)
#                print('........')
#            if count1 == 20:
#                print(i)
# 
'''
    seg = pkuseg.pkuseg()
    text = seg.cut(s)
       
    with open("./bb.txt", encoding="utf-8") as f:#更换aa.txt,bb.txt,cc.txt,dd.txt以尝试不同划分效果！！
        stop = f.read()  
    
    for i in text:
        if i not in stop:
            new_text.append(i)

    counter = Counter(new_text)
    pprint.pprint(counter.most_common(35))
    m = counter.most_common(35)

    for i in range(len(m)):
        k = list(m[count])
        word.append(k[0])
        count = count + 1
    print(word)
'''