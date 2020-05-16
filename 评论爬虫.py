from __future__ import print_function
import requests
import json
import re #正则匹配
import time #时间处理模块
import jieba #中文分词
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from PIL import Image
from wordcloud import WordCloud  #绘制词云模块
from snownlp import SnowNLP

# import paddlehub as hub


def getMovieinfo(url):
    '''
    请求爱奇艺评论接口，返回response信息
    参数  url: 评论的url
    return: response信息
    '''
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",

    }
    response = session.get(url, headers=headers)
    if response.status_code == 200:
         return response.text
    return None

#解析jgon数露，获取评论
def saveMoviernforoFile(lastId,arr,url):

    # '''
    # 解析json数据，获取评论
    # 爬取爱奇艺评论区
    # #参数lastrd：最后一条评论ID arx：存故文本的1ist
    # ：return：新的lastrd
    # '''
    if url == None:
        url="https://sns-comment.iqiyi.com/v3/comment/get_comments.action?agent_type=118&agent_version=9.11.5&authcookie=null&business_type=17&content_id=15472234400&hot_size=0&page=&page_size=20&types=time&last_id="

    url+=str(lastId)
    responseTxt=getMovieinfo(url)
    responseJson=json.loads(responseTxt)
    comments=responseJson['data']['comments']
    for val in comments:
        #print(val.keys())
        if'content'in val.keys():
            print(val['content'])
            arr.append(val['content'])
            lastId=str(val['id'])
    return lastId

#解析jgon数露，获取评论
def saveMoviernforoFileBili(lastId,arr,url):

    # '''
    # 爬取bilibili评论区
    # 解析json数据，获取评论
    # #参数lastrd：最后一条评论ID arx：存故文本的1ist
    # ：return：新的lastrd
    # 752881391回形针
    # 582921863
    # '''
    if url == None:
        url="https://api.bilibili.com/x/v2/reply?callback=jQuery17202354826870397837_1588331328657&type=1&oid=752881391&sort=2&_=1588331336930&pn="
    url+=str(lastId)
    responseTxt=getMovieinfo(url)
    responseJson=json.loads(responseTxt)
    comments=responseJson['data']['replies']
    for val in comments:
        #print(val.keys())
        if'content'in val.keys():
            print(val['content']['message'])
            arr.append(val['content']['message'])
    return lastId


def clear_special_char(content):

    #清除没有意义的字符，数据清洗

    s = re.sub(r"</?(.+?)>|&nbsp;|\t|\r", "", content)
    s = re.sub(r"\n", "", s)
    s = re.sub(r"\*", "\\*", s)
    s = re.sub("\u4e00-\u9fa5^a-z^A-Z^0-9", "", s)
    s = re.sub(
        '[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+',
        '', s)
    s = re.sub('[a-zA-Z]', "", s)
    s = re.sub('^\d+(\.\d+)?$', "", s)
    s = re.sub(u'[\U00010000-\U0010ffff]', ' ', s)
    s = re.sub(u'[\uD800-\uDBFF][\uDC00-\uDFFF]', ' ', s)
    for ch in '，。；：“”、》《、|*&…🙏！♥♡😊🌚？💚√🍼【】💔🐴]๑👍[🌟😘🤘ﾉ🐱👩‍❤“💎🌸💙😁❄，≧▽≦👀🐶🍬😂 !🧡😃 ヾ↗~↖＾ 🏻🍋～♀٩௰^ و˃͈ ̶ω˂😆௰ ˂🔒🧍💛💚💖Ő ∀Ő∀✔🤠( ง _ • 。́ ) ง🔒✨🍑💙💜👧🐛🐟✊🌠🌨💪⭐”…':
        s = s.replace(ch, ' ')
    return s





def fenci(text):
    '''
    利用jieba进行分词
    参数 text:需要分词的句子或文本
    return：分词结果
    '''


    jieba.load_userdict('words_bilibili.txt')
    seg = jieba.lcut(text,cut_all = False)
    print(seg)
    return seg


def stopwordslist(file_path):
    '''
    创建停用词表
    参数 file_path:停用词文本路径
    return：停用词list
    '''
    stopwords = [line.strip() for line in open(file_path,encoding='UTF-8').readlines()]


    return stopwords


def movestopwords(sentence,stopwords,counts):
    '''
    去除停用词,统计词频
    参数 file_path:停用词文本路径 stopwords:停用词list counts: 词频统计结果
    return：None
    '''
    out = []
    for word in sentence:
        if word not in stopwords:
            if len(word)!=1:
                counts[word] = counts.get(word,0)+1

    return None

def drawcounts(counts,num):
    '''
    根据词频绘制统计表

    return：none
    '''
    x_aixs = []
    y_aixs = []
    c_order = sorted(counts.items(),key = lambda x:x[1],reverse = True) # 对二维数据进行排序
    # print(x_crder)
    for c in c_order[:num]:
        x_aixs.append(c[0])
        y_aixs.append(c[1])

    matplotlib.rcParams['font.sans-serif'] = ['SimHei'] #指定默认字体
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.bar(x_aixs,y_aixs)
    plt.title('词频统计结果')
    plt.show()

def drawcloud(word_f):
    '''
    根据词频绘制词云图
    参数 word_f:统计出的词频结果
    return：none
    '''

    #背景图片
    # coud_mask = np.array(Image.open(''))
    #忽略显示的词
    st = set(["东西","这是","真的"])
    #生成
    wc = WordCloud(background_color='white',
                   mask=None,
                   max_words=150,
                   font_path='simhei.ttf',
                   min_font_size=10,
                   max_font_size=100,
                   width=400,
                   relative_scaling=0.3,
                   stopwords=st
                   )
    wc.fit_words(word_f)
    wc.to_file('pic.png')




def crawler(num,choose,url):
    lastId = '0'
    arr = [] # 评论的存放数组
    if choose=="aqy":
        with open('aqy.txt','a',encoding='utf-8') as f:
            for i in range(num):
                lastId = saveMoviernforoFile(lastId,arr,url)
                time.sleep(0.5)
            for item in arr:
                item = clear_special_char(item)  # 清楚特殊字符
                if item.strip()!='':
                    try:
                        f.write(item+'\n')
                    except Exception as e:
                        print("含有特殊字符")
    elif choose=="bilibili":
        with open('bilibili.txt','a',encoding='utf-8') as f:
            for i in range(num):
                lastId = saveMoviernforoFileBili(i+1,arr,url)
                time.sleep(0.5)
            for item in arr:
                item = clear_special_char(item)  # 清楚特殊字符
                if item.strip()!='':
                    try:
                        f.write(item+'\n')
                    except Exception as e:
                        print("含有特殊字符")
    else:
        print("没有此选项")


    print('一共爬取：',len(arr))

def analys(counts,choose):
    if choose =="aqy":
        f = open('aqy.txt', 'r', encoding='utf-8')
        for line in f:
            words = fenci(line)
            stopwords = stopwordslist('add_words.txt')
            movestopwords(words, stopwords, counts)
        f.close()
        np.save('my_file.npy', counts)
    if choose =="bili":
        f = open('bilibili.txt', 'r', encoding='utf-8')
        for line in f:
            words = fenci(line)
            stopwords = stopwordslist('add_words.txt')
            movestopwords(words, stopwords, counts)
        f.close()
        np.save('my_file_bili.npy', counts)



if __name__ == "__main__":
    num = 10 # num是页数，一页十条评论，假如爬取1000条，设置num=100
    counts = {}
    url = None  # 可换成想要爬取的网页
    crawler(num,"bilibili",url) # 运行爬虫，生成文件txt.(num,choose,url)

    analys(counts,"bili") # 词频统计输入txt输出分词npy
    read_dictionary = np.load('my_file_bili.npy',allow_pickle=True).item() # 读取词频统计

    plt.figure(figsize=(50, 6))
    drawcounts(read_dictionary,50)
    drawcloud(read_dictionary)


# ---------------情感分析模块---------------------
# 判断句子的情感是积极还是消极的，准确率非常差不建议使用。

    # f = open('bilibili.txt', 'r', encoding='utf-8')
    # positive = 0
    # negative = 0
    # for line in f:
    #     a = SnowNLP(line).sentiments
    #     print(line+" "+str(a))
    #     if a >0.6:
    #         positive=positive+1
    #     if a <0.4:
    #         negative=negative+1
    #
    # print(positive)
    # print(negative)

# -----------------------------------------------------


    # 爱奇艺模块
    # f = open('aqy.txt','r',encoding='utf-8')
    # for line in f:
    #     words = fenci(line)
    #     stopwords = stopwordslist('add_words.txt')
    #     movestopwords(words,stopwords,counts)
    #
    # drawcounts(read_dictionary,10)
    # drawcloud(read_dictionary)
    # f.close()
