# coding = utf-8
import urllib.request, urllib.error # 指定URL，获取数据
from bs4 import BeautifulSoup       # 网页解析，获取数据
import re                           # 正则表达式，文字匹配
import xlwt                         # Excel写入

## 正则表达式
# 影片链接
findLink = re.compile(r'<a href="(.*?)">')  # compile()用来创建正则表达式对象,懒惰模式，最后取出的是括号中的字符
# 影片图片
findImage = re.compile(r'<img.*src="(.*?)".*>')
# 影片标题
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片内容
findBD = re.compile(r'<p class="">(.*?)</p>', re.S)
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 影片评价人数
findRatingNum = re.compile(r'<span>(\d*)人评价</span>')
# 影片概况
findAbstract = re.compile(r'<span class="inq">(.*)</span>')


## 1.1 得到一个指定URL的页面内容(爬取单个网页)
def askURL(url):
    # header的作用是伪装，模拟头部信息，让网站以为我们是浏览器而不是爬虫
    header = {
        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }
    request = urllib.request.Request(url, headers=header)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, 'code'): # hasattr是Has Attribute的简称，作用是检查某个对象是否有某种属性，返回布尔值
            print(e.code)      # code一般是在报错时才会出现，当豆瓣发现我们是爬虫时，会返回418错误
        if hasattr(e, 'reason'):
            print(e.reason)

    return html

## 正则表达式解析
def resolveData(html, datalist):
    soup = BeautifulSoup(html, 'html.parser')
    for item in soup.find_all('div', class_='item'):
        data = list()    # 保存一部电影的所有信息
        item = str(item) # 将item保存为字符串，方便之后作为正则表达式的校验字符串

        link = re.findall(findLink, item)[0]
        data.append(link)

        image = re.findall(findImage, item)[0]
        data.append(image)

        title = re.findall(findTitle, item)
        if len(title) > 1:
            ctitle = title[0]
            data.append(ctitle)
            # 外文名处理这里遇到了\xa0以及斜杠的去除问题
            # etitle = ("".join(title[1].split())).replace('/', '')
            etitle = title[1].replace('/', '')
            data.append(etitle)
        else:
            data.append(title[0])
            data.append(' ')

        bd = re.findall(findBD, item)[0]
        bd = re.sub('<br/>', ' ', bd)
        bd = re.sub('/', ' ', bd)
        # 影片内容这里也遇到了\xa0问题
        # bd = (''.join(bd.split()))
        data.append(bd.strip())

        rating = re.findall(findRating, item)[0]
        data.append(rating)

        ratingNum = re.findall(findRatingNum, item)[0]
        data.append(ratingNum)

        abstract = re.findall(findAbstract, item) # abstract可能有不存在的情况
        if len(abstract) != 0:
            abstract = abstract[0].replace('。', '')
            data.append(abstract)
        else:
            data.append(' ')
        
        datalist.append(data)    

## 1.2 爬取(多个)网页
def getData(baseurl):
    datalist = list()
    # 豆瓣Top250电影每个页面有25部电影，总共有10个页面
    # 所以循环10次
    for page in range(10):
        url = baseurl + str(page * 25)
        html = askURL(url)

        ## 2 解析数据
        resolveData(html, datalist)
    return datalist

## 3.1 保存到excel
def saveXsl(datalist, savepath):
    workbook = xlwt.Workbook(encoding='utf-8')  # 创建workbook对象，可以理解为一个excel文件
    worksheet = workbook.add_sheet('sheet1')  # 创建工作表对象，就是excel文件里的一个工作表
    col_name = ('电影链接', '电影图片', '电影中文名','电影外文名', '电影相关信息', '电影评分', '电影评分人数', '电影概述')
    for col in range(len(col_name)):
        worksheet.write(0, col, col_name[col])
    for row in range(1, len(datalist)):
        for col in range(len(col_name)):
            worksheet.write(row, col, datalist[row][col])

    workbook.save(savepath)

def main():
    baseurl = "https://movie.douban.com/top250?start="
    savepath = "/Users/fjz/Desktop/cralwer.xls"
    # 1.分析并爬取网页
    # 2.解析数据
    datalist = getData(baseurl)
    # 3.保存数据
    saveXsl(datalist, savepath)



if __name__ == "__main__": # 函数入口
    main()
