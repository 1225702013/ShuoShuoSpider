import os
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import requests
import traceback
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
class ShuoShuoSpider:
    ##初始化类
    def __init__(self):
        ###设置Chrome启动方式为隐式
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')

        self.friendName = ""
        self.time = ""
        self.info = ""

    def createWordCloud(self,path):
        ##2.1读取动态文本
        text_from_file_with_apath = open(path+".txt", encoding='utf-8').read()

        ##2.2利用结巴分词进行文本分词
        wordlist_after_jieba = jieba.cut(text_from_file_with_apath, cut_all=True)
        wl_space_split = " ".join(wordlist_after_jieba)

        ##2.3初始化词云
        my_wordcloud = WordCloud(background_color="white",#指定词云背景色
                                 width=1000, height=860,#指定词云尺寸
                                 font_path="C:\\Windows\\Fonts\\HYShuaiXianTiW.ttf",#指定词云字体
                                 mask=plt.imread('xin.jpg')#指定词云生成样式图
                                 )
        my_wordcloud.generate(wl_space_split)

        #2.4展示词云
        my_wordcloud.to_file("WordCloud.png")#保存到当前文件夹
        plt.imshow(my_wordcloud)
        plt.axis("off")#关闭坐标系
        plt.show()

        #脚本主类
        # #

    def getShuoShuo(self,num):
        ##0.初始化
        path_str = "H:/"+num+"/"#好友动态文本保存的路径
        if not os.path.exists(path_str):
            os.makedirs(path_str)  # 创建文件夹

        ##1.隐式启动Chrome，并访问QQ空间
        driver = webdriver.Chrome(options=self.chrome_options)#
        driver.get("https://user.qzone.qq.com/{}/main".format(num))
        time.sleep(3)
        print("开始登录")

        ##2.selenium交换到登陆的iframe中，执行登陆点击
        driver.switch_to.frame(driver.find_element_by_id("login_frame"))
        driver.find_element_by_id("img_out_1225702013").click()
        print("登陆成功，去除遮罩")
        time.sleep(5)

        ##3.去除亲密度提示遮罩层
        driver.find_element_by_xpath("//*[@id=\"friendship_promote_layer\"]/table/tbody/tr[1]/td[2]/a").click()
        print("成功去除，进入动态页面")
        time.sleep(1)

        ##4.进入动态页面
        driver.find_element_by_xpath("//*[@id=\"QM_Profile_Mood_A\"]").click()
        time.sleep(3)

        ##5.selenium交换到动态的iframe
        driver.switch_to.frame(driver.find_element_by_id("app_canvas_frame"))
        time.sleep(10)

        ##6.获取好友备注
        self.friendName = driver.find_element_by_xpath("//*[@id=\"msgList\"]/li[1]/div[3]/div[2]/a").text
        print("获取iframe成功，现在抓取"+self.friendName+"的动态")

        ##7.准备抓取
        li_len = 0#初始化单page动态li数
        last_len = 0#初始化累积抓取动态数
        lenght = int(driver.find_element_by_id("pager_last_0").text)#获得动态总页数


        ##8.迭代抓取每条动态文本，包括转发的动态
        for p in range(0,lenght-1):

            ###8.1获取当前页面动态数
            str_list = []
            list = driver.find_element_by_xpath("//ol").find_elements_by_xpath("*")
            li_len = len(list)

            ###8.2动态迭代
            for i in range(1,li_len):
                self.info = driver.find_element_by_xpath("//ol/li[{}]/div[3]/div[2]/pre".format(i)).text
                str_list.append(self.info)

            ###8.3将本次抓取的动态数量累加
            last_len = last_len + li_len

            ###8.4selenium交换到默认主页
            driver.switch_to.default_content()

            ###8.5命令selenium执行滑动到底部操作
            js = "var q=document.documentElement.scrollTop=100000"
            driver.execute_script(js)
            time.sleep(1)

            ###8.6当滑动到底部后，再次交换到iframe并点击下一页
            driver.switch_to.frame(driver.find_element_by_id("app_canvas_frame"))
            driver.find_element_by_id("pager_next_{}".format(p)).click()
            time.sleep(5)

            ###8.7追加保存抓取的文本到本地文档
            print("现在开始保存抓取到的文本")
            f = open(path_str+self.friendName+".txt", mode="a+",encoding="utf-8")  # 追加打开文档
            try:
                for i in range(0,len(str_list)):#迭代写入
                    f.write(str_list[i]+"\n")
                f.flush()
                f.close()
                print("保存成功")
                print("已经保存了{}条动态".format(last_len))
            except Exception as e:
                traceback.print_exc()#抛出异常
                f.flush()
                f.close()
                print("保存失败")
            print("\n\n抓取下一页动态")
        ##9.当全部动态抓取完毕，生成词云
        self.createWordCloud(path_str+self.friendName)

            # print(li_len)
            # for i in range(1,li_len+1):




        #
        # self.time = driver.find_element_by_xpath("//*[@id=\"fct_1599084186_311_0_1560406488_0_1\"]/div[1]/div[4]/div[2]/span").text
        # self.info = driver.find_element_by_xpath("//*[@id=\"feed_1599084186_311_0_1560406488_0_1\"]/div[1]").text
        # self.info = driver.find_element_by_xpath("").text

        #self.friendName = driver.find_element_by_xpath("//*[@id=\"goProfileFeedsLink\"]/a").click()


if __name__ == '__main__':
    num = "1225702013"#此处填入好友QQ
    s = ShuoShuoSpider()
    s.getShuoShuo(num)#启动脚本主类