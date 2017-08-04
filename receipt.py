# coding=utf-8
import re
import selenium.webdriver
import selenium.webdriver.support.ui as selec
import datetime
import pymysql
import time

'''适用于上期所2014年5月23日及以后的库存周报数据格式'''
pattern0=re.compile('<div.*?n_right fr box">(.*?)</html>',re.S)
pattern1=re.compile('<div id="库存周报\d+_\d+".*?<tbody>(.*?)</tbody>',re.S)
pattern2=re.compile('<tr (.*?)</tr>',re.S)
pattern3=re.compile('>日期：(.*?)年(.*?)月(.*?)日</td>',re.S)
pattern4=re.compile('<font.*?">(.*?)</font>.*?年</.*?">(.*?)</.*?月</.*?">(.*?)</f',re.S)
pattern5=re.compile('>交割商品：(.*?)</td>',re.S)
pattern6=re.compile('<td(.*?)td>',re.S)
pattern7=re.compile('>(.*?)</',re.S)

pattern8=re.compile('colspan="\d">.*?strong>(.*?)</strong',re.S)
pattern9=re.compile('<td (.*?)</td>',re.S)

pattern10=re.compile('<table class="ui-datepicker-calendar">.*?<tbody>(.*?)</tbody>',re.S)
pattern11=re.compile('<tr>(.*?)</tr>',re.S)
pattern12=re.compile('<td (.*?)</td>',re.S)

def connDB():
    connMysql=pymysql.connect(host='localhost',user='root',passwd='693456',db='warehouse_receipts',port=3306,charset='utf8')
    if not connMysql:
        raise (NameError,'数据库连接失败了哦！')
    return connMysql

def getPage(driver,pageNum,lastPage):
    contTemp = driver.page_source
    tbody=re.findall(pattern10,contTemp)
    tr=re.findall(pattern11,tbody[0])
    trCount=len(tr)
    xpath=[]
    contMonth=[]
    for i in range(0,trCount):
        td=re.findall(pattern12,tr[i])
        if 'has-data' in td[5] and 'href=' in td[5]:
            xpath.append('.//*[@id="calendar"]/div/table/tbody/tr[%d]/td[6]/a'%(i+1))
    xpathCount=len(xpath)
    if pageNum<lastPage-1:
        for j in range(0,xpathCount):
            friday=driver.find_element_by_xpath(xpath[xpathCount-j-1])
            friday.click()
            time.sleep(2)
            contents=driver.page_source
            contMonth.append(contents)
        prevMonth = driver.find_element_by_xpath('.//*[@id="calendar"]/div/div/a[1]')
        prevMonth.click()
    if pageNum==lastPage-1:
        for j in range(0,2):
            friday=driver.find_element_by_xpath(xpath[xpathCount-j-1])
            friday.click()
            time.sleep(2)
            contents=driver.page_source
            contMonth.append(contents)
    time.sleep(1)
    return contMonth

def analyzeHTML(contents,pageNum,lastPage):
    sql = 'insert into data_week VALUES '
    right_box=re.findall(pattern0,contents)
    tbody=re.findall(pattern1,right_box[0])
    tr=re.findall(pattern2,tbody[0])
    trCount=len(tr)
    i=0
    if pageNum<lastPage-1:
        date=re.findall(pattern3,tbody[0])
    if pageNum==lastPage-1:
        date = re.findall(pattern4, tbody[0])
    date=date[0]+'-'+date[1]+'-'+date[2]
    dataRow=[-1,-1,-1,-1,-1,-1]
    while i<trCount :
        commodity=re.findall(pattern5,tr[i])
        if commodity:
            i+=2
        else:
            td=re.findall(pattern6,tr[i])
            
        i+=1

'''
    for trEach in tbody:
        commodity=re.findall(pattern3,tb)
        tr=re.findall(pattern4,tb)
        trCount=len(tr)
        if commodity[0]!='黄金':
            td = re.findall(pattern9, tr[2])
            tdCount = len(td)
            for i in range(3,trCount):
                province=re.findall(pattern5,tr[i])
                warehouse=re.findall(pattern6,tr[i])
                numb=re.findall(pattern7,tr[i])
                total=re.findall(pattern8,tr[i])

                if province and warehouse:
                    dataRow[0]=date
                    dataRow[1]=commodity[0]
                    dataRow[2]=province[0]
                    if warehouse[0][0]:
                        dataRow[3]=warehouse[0][0]
                    else:
                        dataRow[3]=warehouse[0][1]
                    if tdCount>3:
                        if numb[2]:
                            dataRow[4]=numb[2]
                        else:
                            dataRow[4]=0.01
                        if numb[3]:
                            dataRow[5]=numb[3]
                        else:
                            dataRow[5]=0.01
                    else:
                        dataRow[4]=0.01
                        dataRow[5]=numb[1]
                    sql+="('%s','%s','%s','%s','%s','%s'),"%(dataRow[0],dataRow[1],dataRow[2],dataRow[3],dataRow[4],dataRow[5])
                if not province and not total and warehouse:
                    dataRow[0] = date
                    dataRow[1] = commodity[0]
                    dataRow[2] = dataRow[2]
                    if warehouse[0][0]:
                        dataRow[3]=warehouse[0][0]
                    else:
                        dataRow[3]=warehouse[0][1]
                    if tdCount>3:
                        if numb[2]:
                            dataRow[4]=numb[2]
                        else:
                            dataRow[4]=0.01
                        if numb[3]:
                            dataRow[5]=numb[3]
                        else:
                            dataRow[5]=0.01
                    else:
                        dataRow[4]=0.01
                        dataRow[5]=numb[1]
                    sql+="('%s','%s','%s','%s','%s','%s'),"%(dataRow[0],dataRow[1],dataRow[2],dataRow[3],dataRow[4],dataRow[5])
                if total:
                    dataRow[0] = date
                    dataRow[1] = commodity[0]
                    dataRow[2] = total[0]
                    dataRow[3] = total[0]
                    if tdCount>3:
                        if numb[2]:
                            dataRow[4]=numb[2]
                        else:
                            dataRow[4]=0.01
                        if numb[3]:
                            dataRow[5]=numb[3]
                        else:
                            dataRow[5]=0.01
                    else:
                        dataRow[4]=0.01
                        dataRow[5]=numb[1]
                    sql += "('%s','%s','%s','%s','%s','%s'),"% (dataRow[0],dataRow[1],dataRow[2],dataRow[3],dataRow[4],dataRow[5])
        if commodity[0]=='黄金':
            numb = re.findall(pattern7, tr[2])
            dataRow[0] = date
            dataRow[1] = commodity[0]
            dataRow[2]='no'
            dataRow[3]='no'
            dataRow[4]=0.01
            if numb[1]:
                dataRow[5]=numb[1]
            else:
                dataRow[5]=0.01
            sql += "('%s','%s','%s','%s','%s','%s'),"% (dataRow[0],dataRow[1],dataRow[2],dataRow[3],dataRow[4],dataRow[5])
    sqlLen = len(sql)
    sql = sql[0:sqlLen - 1]
    return sql
'''

if __name__=='__main__':
    startTime=datetime.datetime.now()
    lastPage=39
    driver = selenium.webdriver.Chrome()
    driver.get('http://www.shfe.com.cn/statements/dataview.html?paramid=dailystock')
    elem = driver.find_element_by_id('weeklystock')
    elem.click()
    time.sleep(1)
    connMysql = connDB()
    cur = connMysql.cursor()
    for i in range(0,lastPage):
        contMonth=getPage(driver,i,lastPage)
        for contents in contMonth:
            sql=analyzeHTML(contents)
            cur.execute(sql)
            connMysql.commit()
    connMysql.close()
    endTime=datetime.datetime.now()
    print('Running Time:', (endTime - startTime).seconds, 'seconds')