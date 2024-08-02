#textline 줄 바꿈 표현

from asyncio import subprocess
import pandas as pd
from topic_modeling import *
from GPT_Modeling import *
import re
import pymysql 
import datetime
from PyQt5.QtGui import QPixmap
from gtts import gTTS



import pyaudio
import wave
import requests

import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
import os
try:
    os.remove('dataset/address.txt')
except FileNotFoundError:
    pass
try:
    os.remove('dataset/carnumber.txt')
except FileNotFoundError:
    pass
try:
    os.remove('dataset/name.txt')
except FileNotFoundError:
    pass
try:
    os.remove('dataset/phonenumber.txt')
except FileNotFoundError:
    pass



#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("AIchat.ui")[0]


#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMaiAI_Service_ndow, form_class) :


    na_flag=False
    ph_flag=False
    add_flag=False
    car_flag=False



    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.start.clicked.connect(self.start_b)
        self.confirm.clicked.connect(self.printTextFunction)
        self.AI_Service_db_download.clicked.connect(self.download_privacy)
        self.AI_Service_chat_download.clicked.connect(self.download_chatdb)
        self.end.clicked.connect(QCoreApplication.instance().quit)
        self.citizenimage.setPixmap(QPixmap("citizen.png"))
        self.citizenimage.setScaledContents(True) 
        self.chatbotimage.setPixmap(QPixmap("chatbot.png"))
        self.chatbotimage.setScaledContents(True)  



        conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8') 
        cursor = conn.cursor()
        sql = """select max(category) from AI_Service_chatdb;"""
        sql1 = 'use AI_Service_CHAT'
        cursor.execute(sql1)
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit() 
        conn.close() 
        y=list(result)
        y=y[0]
        y=list(y)
        y=y[0]
        try:
            self.cate = y+1
        except TypeError:
            self.cate = 0

    def download_privacy(self):
        conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8') 
        cursor = conn.cursor() 
        sql1 = 'use AI_Service_CHAT'
        sql = """ 
            SELECT * FROM AI_Service_db;
        """ 
        cursor.execute(sql1)
        cursor.execute(sql)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        df.columns=['id','name','phonenum','address','carnum','date','category']
        df.to_excel('AI_Service_chat_privacyDB.xlsx')


    def download_chatdb(self):
        conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8') 
        cursor = conn.cursor() 
        sql1 = 'use AI_Service_CHAT'
        sql = """ 
            SELECT * FROM AI_Service_chatdb;
        """
        cursor.execute(sql1)
        cursor.execute(sql)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        df.columns=['id','user','chatbot','date','category']
        df.to_excel('AI_Service_chat_dialogDB.xlsx')



    def printTextFunction(self) :
        self.AI_Service_bot()
    
    def start_b(self) :
        self.c_f="행정민원 접수 및 질의응답 AI 상담사 입니다. 무엇을 도와드릴까요?"
        self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
        self.AI_Service_chat_text.setWordWrap(True)
        self.GoogleTTS(self.c_f)          
    
 
    def GoogleTTS(self,chtext):
        tts = gTTS(text=chtext,lang ='ko')
        tts.save("helloKo.mp3")

    def collect_carnumber(self,text):
        data = text
        try:
            patt = re.compile(r'\d{2,3}\w\d{4,5}')
            match = patt.search(data)
            carnumber = match.group()
            f= open('dataset/carnumber.txt','w')   
            f.write(carnumber)
            f.close()
            f=open('dataset/carnumber.txt','r')
            car_data=f.readline()
            self.c_f=('네, '+car_data+" 차량 신고 맞으신가요? 맞으시다면 시민님, 성함은 어떻게 되시나요? 이름은 단어로 시작해주세요")
            self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)
        except AttributeError:
            self.c_f="잘 못 알아 들었어요, 다시 말씀해주시겠어요?"
            self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)

       
        return self.c_f


    def collect_name(self,text):
        data = text
        first_name=['김','정','홍','오','이','박','최','정','강','조','윤','장','임','한','서','신','권','황','안','선우','익']

        data = data.replace('이름','')
        for i in range(len(first_name)):
            try:
                patt = re.compile(r'[ ]? '+first_name[i]+'..')
                match = re.search(patt, data)  
                name=match.group()
                f= open('dataset/name.txt','w')   
                f.write(name)
                f.close()
                f=open('dataset/name.txt','r')
                name_data=f.readline()
                self.c_f=('네, '+name_data+" 님 맞으신가요? 맞으시다면 시민님 휴대폰 번호는 어떻게 되시나요?")
                self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
                self.AI_Service_chat_text.setWordWrap(True)
                self.GoogleTTS(self.c_f)
            except AttributeError as a:
                i+=1
        '''
        self.c_f="잘 못 알아 들었어요, 다시 말씀해주시겠어요?"
        self.AI_Service_chat_text.setText("챗봇 : "+self.c_f)
        self.AI_Service_chat_text.setWordWrap(True)
        self.GoogleTTS(self.c_f)
        '''
                
  
        return self.c_f


    def collect_phonenumber(self,text):
        data = text
        try:
            patt = re.compile(r'\d{3}?\d{4}?\d{4}')
            match = patt.search(data)
            phonenumber = match.group()
            f= open('dataset/phonenumber.txt','w')   
            f.write(phonenumber)
            f.close()
            f=open('dataset/phonenumber.txt','r')
            phone_data=f.readline()
            self.c_f=('네, '+phone_data+" 맞으신가요? 맞으시다면 신고하시고자 하시는 곳 주소 불러주시겠습니까?")
            self.AI_Service_chat_text.setText("AI Counselor: "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)
        except AttributeError:
            self.c_f="잘 못 알아 들었어요, 다시 말씀해주시겠어요?"
            self.AI_Service_chat_text.setText("AI Counselor: "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)


        return self.c_f
        
    def collect_address(self,text):
        data = text
        try:
            #patt = re.compile(r'(\w+[도시]\s)(?:.+[시구]\s)(.+[읍면동])\s?(\w+\d*\w*[동,리,로,길]\s*)?(\w*\d+-?\d*)?')
            patt = re.compile(r'(\w+[도시]\s)(?:.+[시구]\s)\s?(\w+\d*\w*[동,리,로,길]\s*)?(\w*\d+-?\d*)?')
            match = patt.search(data)
            address = match.group()
            f= open('dataset/address.txt','w')   
            f.write(address)
            f.close()
            f=open('dataset/address.txt','r')
            address_data=f.readline()
            self.c_f=('네, '+address_data+"로 접수 도와드리겠습니다. 감사합니다. 더 신고하실 사항 있으신가요?")
            self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)
        except AttributeError:
            self.c_f="잘 못 알아 들었어요, 다시 말씀해주시겠어요?"
            self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)


        return self.c_f

    def AI_Service_bot(self):
        global na_flag, car_flag, ph_flag, add_flag
        chatbot_flag =True
        

        end_list=['괜찮아요','없습니다']
        con_list=['네','더 있어요']
        de=['주정차','차','불법','신고','접수','단속','위반','주차','견인신고']
        self.text=self.people_text.text()
        self.people_text_2.setText("시민 문의 : "+self.text)

        a_patt = re.compile(r'(\w+[도시]\s)(?:.+[시구]\s)\s?(\w+\d*\w*[동,리,로,길]\s*)?(\w*\d+-?\d*)?')
        a_match = a_patt.search(self.text)
        c_patt = re.compile(r'\d{2,3}\w\d{4,5}')
        c_match = c_patt.search(self.text)
        p_patt = re.compile(r'\d{3}?\d{4}?\d{4}')
        p_match = p_patt.search(self.text)


        if a_match:
            try:
                a_match.group()
                self.text="주소는 " + self.people_text.text()
                print(self.text)
            except AttributeError:
                pass
        elif p_match:
            try:
                p_match.group()
                self.text="전화번호는 " + self.people_text.text()
                print(self.text)
            except AttributeError:
                pass
        elif c_match:
            try:
                c_match.group()
                self.text="차량번호는 " + self.people_text.text()
                print(self.text)
            except AttributeError:
                pass
        else:
            self.text=self.people_text.text()
            print(self.text)



        if self.text in end_list:
            chatbot_flag=False
        if self.text in con_list:
            self.c_f="네, 그럼 추가로 신고하실 내용 말씀해 주시겠습니까?"
            self.AI_Service_chat_text.setText("AAI Counselor : "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)
            chatbot_flag=False
                #pass
        if chatbot_flag == True:

            if self.text == '아니요':
                self.c_f="네, 그럼 다시 말씀해 주시겠습니까?"
                self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
                self.AI_Service_chat_text.setWordWrap(True)
                self.GoogleTTS(self.c_f)
            else:
                try:
                    self.model=lsa_model.LSA_Model(self.text)
                    text_file="t1.txt"
                    key_topic=[line.strip() for line in open(text_file, encoding="UTF8").readlines()]
                    for d in range(len(key_topic)):
                        if key_topic[d] in de:
                            topic='불법 주정차 신고'
                            break
                        elif '차량번호' in key_topic[d]:
                            topic = '차량번호 추출'
                            break
                        elif '이름' in key_topic[d]:
                            topic = '이름 추출'
                            break
                        elif '번호' in key_topic[d]:
                            topic = '전화번호 추출'
                            break
                        elif '주소' in key_topic[d]:
                            topic = '주소 추출'
                            break
                        else: 
                            topic='감정분석'


                    if topic=='불법 주정차 신고':
                        self.c_f = '네, 불법 주정차 신고 도와 드릴게요, 차량 번호 불러 주시겠어요?'
                        self.AI_Service_chat_text.setText("AI Counselor : "+self.c_f)
                        self.AI_Service_chat_text.setWordWrap(True)
                        self.GoogleTTS(self.c_f)
                        self.AI_DBChat(self.text,self.c_f,self.cate)
                        na_flag=False
                        ph_flag=False
                        add_flag=False
                        car_flag=True
                    elif topic=='차량번호 추출':
                        self.s_t= self.collect_carnumber(self.text)
                        self.AI_DBChat(self.text,self.s_t,self.cate)
                        na_flag=True
                        ph_flag=False
                        add_flag=False
                        car_flag=False
                    elif topic=='전화번호 추출': 
                        self.s_t = self.collect_phonenumber(self.text)
                        self.AI_DBChat(self.text,self.s_t,self.cate)
                        na_flag=False
                        ph_flag=False
                        add_flag=True
                        car_flag=False
                    elif topic == '주소 추출':
                        self.s_t = self.collect_address(self.text,)
                        self.AI_DBChat(self.text,self.s_t,self.cate)
                        try:
                            self.AI_DB(self.cate)
                        except FileNotFoundError:
                            pass
                        na_flag=False
                        ph_flag=False
                        add_flag=False
                        car_flag=False
                    elif topic =='이름 추출':
                        self.s_t = self.collect_name(self.text)
                        self.AI_DBChat(self.text,self.s_t,self.cate)
                        na_flag=False
                        ph_flag=True
                        add_flag=False
                        car_flag=False
                    
                    elif topic == '감정분석':
                        self.s_t =gpt_model.KoGPT_Main().call_kogpt(self.text)
                        try:
                            if (car_flag==True) and (na_flag==False) and (add_flag==False) and (ph_flag==False) :
                                self.c_f = self.s_t+'시민님, 접수를 위해 차량 번호 불러 주시겠어요?'
                                self.AI_Service_chat_text.setText("AI Counselor: "+self.c_f)
                                self.AI_Service_chat_text.setWordWrap(True)
                                self.GoogleTTS(self.c_f)
                                self.AI_DBChat(self.text,self.c_f,self.cate)
                    
                            elif (na_flag==True) and (car_flag==False) and (add_flag==False) and (ph_flag==False) :
                                self.c_f =  self.s_t+'시민님, 접수를 위해 성함 불러 주시겠어요? 이름은 단어로 시작해주세요'
                                self.AI_Service_chat_text.setText("AI 상담사 : "+self.c_f)
                                self.AI_Service_chat_text.setWordWrap(True)
                                self.GoogleTTS(self.c_f)
                                self.AI_DBChat(self.text,self.c_f,self.cate)

                            elif (ph_flag==True)and (na_flag==False) and (car_flag==False) and (add_flag==False)  :
                                self.c_f =  self.s_t+'시민님, 접수를 위해 휴대폰번호 불러 주시겠어요?'
                                self.AI_Service_chat_text.setText("AI 상담사 : "+ self.c_f)
                                self.AI_Service_chat_text.setWordWrap(True)
                                self.GoogleTTS(self.c_f)
                                self.AI_DBChat(self.text,self.c_f,self.cate)
                            elif (add_flag==True)and (ph_flag==False)and (na_flag==False) and (car_flag==False)  :
                                self.c_f =  self.s_t+'시민님, 접수를 위해 신고하시고자 하는 주소 불러 주시겠어요?'
                                self.AI_Service_chat_text.setText("AI 상담사 : "+self.c_f)
                                self.AI_Service_chat_text.setWordWrap(True)
                                self.GoogleTTS(self.c_f)
                                self.AI_DBChat(self.text,self.c_f,self.cate)
                            else:
                                self.AI_Service_chat_text.setText("AI 상담사 : "+self.s_t)
                                self.AI_DBChat(self.text,self.s_t,self.cate)
                                self.GoogleTTS(self.s_t)
                        except NameError:
                            self.AI_Service_chat_text.setText("AI 상담사 : "+self.s_t)
                            self.AI_DBChat(self.text,self.s_t,self.cate)
                            self.GoogleTTS(self.s_t)

                except ValueError:
                    self.c_f="잘 못알아 들었어요, 다시 말씀해주시겠어요?"
                    self.AI_Service_chat_text.setText("AI 상담사 : "+self.c_f)
                    self.AI_Service_chat_text.setWordWrap(True)
                    self.GoogleTTS(self.c_f)
                


        else:
            self.c_f="네, 지금까지  AI 상담사 이였습니다. 감사합니다."
            self.AI_Service_chat_text.setText("AI 상담사 : "+self.c_f)
            self.AI_Service_chat_text.setWordWrap(True)
            self.GoogleTTS(self.c_f)
        
    def AI_DBChat(self,u_t,s_t,cate):
        d = datetime.datetime.now()
        conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8') 
        cursor = conn.cursor() 
        d = str(d)
        # 파일 불러오기
        u = u_t
        s= s_t
        ca=cate

        sql1 = 'use AI_Service_CHAT'
        sql2 = """INSERT INTO AI_Service_chatdb (user, chatbot, date, category) VALUES (%s,%s,%s,%s);"""

        val2 = (u,s,d,ca)
        cursor.execute(sql1)

        cursor.execute(sql2,val2)

        conn.commit() 
        conn.close() 

    def AI_DB(self,cate):
        d = datetime.datetime.now()
        conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8') 
        cursor = conn.cursor() 
        d = str(d)
        ca=cate

        n_f=open('dataset/name.txt','r')
        n=n_f.readline()
        n_f.close()

        p_f=open('dataset/phonenumber.txt','r')
        p=p_f.readline()
        p_f.close()

        a_f=open('dataset/address.txt','r')
        a=a_f.readline()
        a_f.close()

        c_f=open('dataset/carnumber.txt','r')
        c=c_f.readline()
        c_f.close()

        sql1 = 'use AI_Service_CHAT'

        sql = """INSERT INTO AI_Service_db (name, phonenum, address, carnum, date, category) VALUES (%s,%s,%s,%s,%s,%s);"""


        val = (n,p,a,c,d,ca)

        cursor.execute(sql1)
        cursor.execute(sql,val)

        conn.commit() 
        conn.close() 


if __name__ == '__main__':

    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()

