from flask import Flask, render_template, request, flash, redirect, url_for
from IPython.display import HTML
import pandas as pd
import re
import os
import numpy as np
import csv
import datetime
import time
import pickle
from simhash import Simhash, SimhashIndex

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

choseong=['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
UPLOAD_FOLDER = 'file'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/Test', methods = ['POST', 'GET'])
def Test():
    if request.method == 'POST':
        print('dd')
        df = RenderCSV('test')
        
        pd.set_option('display.max_colwidth', -1)
        return render_template("index.html", tables=[df.to_html(classes='data',escape=False)], titles=df.columns.values)
    
@app.route('/GetData', methods = ['POST', 'GET'])
def GetData():
    if request.method == 'POST':
        data = request.form
        print(data)
        if int(data['methods']) is 1: # 직접입력
            if int(data['means']) is 1: # 키워드
                noise_processing(data['keyword'])
                df = RenderCSV('keyword')
                means = 1
                
            elif int(data['means']) is 2: # 게시글
                simhash(data['keyword'])
                df = RenderCSV('simhash')
                means = 2
        elif int(data['methods']) is 2: # 파일입력
            if int(data['means']) is 1: # 키워드
                #
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)

                    with open(path, 'r', encoding='UTF8') as f:
                        list_file = []
                        for line in f:
                            list_file.append(line.replace('\n',''))
                    noise_processing(list_file)
                    df = RenderCSV('keyword')
                means = 1
            elif int(data['means']) is 2: # 게시글
                #
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)

                    with open(path, 'r', encoding='UTF8') as f:
                        list_file = []
                        for line in f:
                            list_file.append(line.replace('\n',''))
                    simhash(list_file)
                    df = RenderCSV('simhash')
                means = 2
        try:
            df['URL'] = df['URL'].apply(lambda x: '<a href="{0}" target="_blank">{1}</a>'.format(x,x))
        except:
            pass
        pd.set_option('display.max_colwidth', -1)
        return render_template("index.html", tables=[df.to_html(classes='data',escape=False)], titles=df.columns.values, means=means, enable=1)
    
    return render_template("index.html")

def RenderCSV(means):
    where = './static/input/' + means + '/result.csv'
    data = pd.read_csv(where, encoding='euc-kr')
    data.index += 1
    data.columns.names = ['번호']
    return data

def noise_processing(keyword):
    TrainingFile='static/Train/noise처리_output_v0.1'
    keyword=pd.Series(keyword)
    ## Train Data 가져오기

    start_time = time.time()

    tr_data=pickle.load(open(TrainingFile+"_Metadata.pkl","rb"))

    #index=tr_data.columns
    contents=tr_data['제목']
    no_noise=tr_data['Processing'].fillna('-')
    publisher_id=tr_data['게시자 ID']
    site=tr_data['채널']
    url=tr_data['게시글 URL']
    contents_number=tr_data['고유번호']
    contents_size=tr_data['용량']
    contents_class=tr_data['분류']

    ##  #### csv 생성 결과 저장할 경로 지정해야함 

    fp0=open('static/input/keyword/result.csv','wt')

    fp0.write('검색게시글,유포게시물,유포사이트,게시자id,URL,탐지시간,고유번호,분류,용량')
    fp0.write('\n')


    switch=0
    is_null=1

    for i in range(keyword.size):
        if switch==0:
            fp0.write(str(keyword[i]).replace(',','')+',')
            is_null=1
            for j in range(no_noise.size):
                if keyword[i] in no_noise[j]:
                    is_null=0
                #1열 조정
                    if switch!=0:
                        fp0.write('-'+',')
                    switch=1
                    fp0.write(str(contents[j]).replace(',','')+',')
                    fp0.write(str(site[j]).replace(',','')+',')
                    fp0.write(str(publisher_id[j]).replace(',','')+',')
                    fp0.write(str(url[j]).replace(',','')+',')
                    now = datetime.datetime.now()
                    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                    fp0.write(str(nowDatetime).replace(',','')+',')
                    fp0.write(str(contents_number[j]).replace(',','')+',')
                    fp0.write(str(contents_class[j]).replace(',','')+',')
                    fp0.write(str(contents_size[j]).replace(',',''))
                    fp0.write('\n')
        
            if is_null:
                fp0.write('\n')
            switch=0
            
    fp0.close()
def get_features_char(unit_len,s):
    width = unit_len
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    #print([s[i:i + width] for i in range(max(len(s) - width + 1, 1))])
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

def get_features_word(unit_len,s):
    shingleLength = unit_len
    s = s.lower()
    s = re.sub('[-=_+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', s)
    tokens = s.split()
    #print(tokens)
    tokens_list=[tokens[i:i+shingleLength] for i in range(len(tokens) - shingleLength + 1)]
    #tokens_list=[tokens[i:i+shingleLength] for i in range(len(tokens) - shingleLength + 1) if len(tokens[i]) < 4]
    shingle_list=[]
    for i in tokens_list:
        #print(i)
        shingle=(str(i). replace('\'','').replace('[','').replace(']','').replace(',',''))
        shingle_list.append(shingle)
    return shingle_list

def simhash(keyword):
    TrainingFile='static/Train/noise처리_output_v0.1'
    topic=pd.Series(keyword)
    ###특수문제 제거 및 연속된 다수의 공백을 1개로 변환
    start_time = time.time()
    SpecChar_Delete=[]
    for row in topic:
        line=re.sub('[-=+_#}/\?;:{^$,.@*\"※~&%!ㆍ＋：』\\‘|\(\)\[\]\<\>`\'…》「◁◀▷▶▲□■」○◆⇒【√☆♥★！→◐『』™●】]',' ',row)
        line=line.replace('．','').replace('　','')
        #공백2개를 한개로 변환
        while True:
            if '  ' in line:
                line=line.replace("  "," ")
            else:
                break
        SpecChar_Delete.append(line)
    ####공백으로 분리하였을때  
    data=[]
    for line in SpecChar_Delete:
        line=line.strip()
        data.append(line.split(' '))

    ######숫자 관련 조건문 처리
    for row in range(len(data)):
        for col in range(len(data[row])):
            if 'IO' in data[row][col]:
                if data[row][col]=='IO':
                    data[row][col]='10'
                elif 'IO월' in data[row][col]:
                    data[row][col]=data[row][col].replace('IO월','10월')
                elif 'IO대' in data[row][col]:
                    data[row][col]=data[row][col].replace('IO대','10대')
                elif 'IOO가지' in data[row][col]:
                    data[row][col]=data[row][col].replace('IOO가지','100가지')
                elif data[row][col]=='IO8OP':
                    data[row][col]='1080P'
                elif data[row][col]=='IO8Op':
                    print(data[row][col], row,col)
                    data[row][col]='1080p'
            elif 'OI' in data[row][col]:
                if data[row][col]=='OI':
                    data[row][col]='01'
                elif ord('0')<=ord(data[row][col][data[row][col].find('OI')-1])<=ord('9'):
                    data[row][col]=data[row][col].replace('OI','01')
            elif 'O' in data[row][col]:
                if data[row][col]=='O':
                    data[row][col]='0'
                elif data[row][col]=='1O8Op':
                    data[row][col]='1O8Op'
                elif ord('0')<=ord(data[row][col][data[row][col].find('O')-1])<=ord('9'):
                    data[row][col]=data[row][col].replace('O','0')
                elif ord('0')<=ord(data[row][col][data[row][col].find('O')+1])<=ord('9'):
                    data[row][col]=data[row][col].replace('O','0')
                elif ord(data[row][col][data[row][col].find('O')-1])==ord('월'):
                    data[row][col]=data[row][col].replace('O','0')
            elif 'o' in data[row][col]:
                if ord('0')<=ord(data[row][col][data[row][col].find('o')-1])<=ord('9'):
                    data[row][col]=data[row][col].replace('o','0')
    ###문자열 다시 생성
    step2=[]
    for line in data:
        step2.append(" ".join(line))
    ####전처리 공백제거
    pre_one=[]
    for line in step2:
        pre_one.append(line.replace(' ',''))
    
    #####원문자 변환
    pre_han=[]
    One_Text=pd.read_csv('static/Train/one_pattern.csv', engine='python')
    before=One_Text['before']
    after=One_Text['after']
    for line in pre_one:  
        for index in range(len(before)):
            if before[index] in line:
                line=line.replace(before[index],after[index])
        pre_han.append(line)
    
    #### line han_pattern
    Han_Combination=pd.read_csv('static/Train/Han_Pattern_sin_v2.csv', engine='python')
    choseong=['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
    step3=[]
    for line in pre_han:
        step3.append(han_pattern(line))
    Eng_Pattern=pd.read_csv('static/Train/Eng_Pattern_v2.csv', engine='python')
    eng_before=Eng_Pattern['before']
    eng_after=Eng_Pattern['after']
    
    step4=[]
    for line in step3:
        for index in range(len(eng_before)):
            line=line.replace(eng_before[index],eng_after[index])
            line=han_pattern(line)
            line=line.replace(eng_after[index],eng_before[index])
        step4.append(line)
    
    Final_Pattern=pd.read_csv('static/Train/final_pattern_v2.csv', engine='python')
    before=Final_Pattern['before']
    after=Final_Pattern['after']
    step5=[]
    for line in step4:  
        for index in range(len(before)):
            if before[index] in line:
                if ord('가')<=ord(line[line.find(before[index])-1])<=ord('힣') or ord('ㄱ')<=ord(line[line.find(before[index])-1])<=ord('ㅣ') or ord('가')<=ord(line[line.find(before[index])+1])<=ord('힣') or ord('ㄱ')<=ord(line[line.find(before[index])+1])<=ord('ㅣ'):
                    line=line.replace(before[index],after[index])
        if 'O' in line:
            if ord('0')<=ord(line[line.find('O')-1])<=ord('9'):
                line=line.replace('O','0',line.find('O'))
        step5.append(line)
    output=[]
    for line in step5:
        line=line.replace('ㅡ','').replace('─','').replace('ltlt','').replace('gtgt','').replace('qu아','').replace('ㅅㅂ','').replace('ㅁㄹ','').replace('ㅅ','').replace('zz','').replace('ㅠㅠ','').replace('ㅁ','')
        while True:
            if 'ㅋ' in line:
                line=line.replace("ㅋ","")
            elif 'ㅎ' in line:
                line=line.replace("ㅎ","")
            elif 'ㅌ' in line:
                line=line.replace("ㅌ","")
            else:
                break
        if 'lt' in line:
            if line.find('lt')!=len(line)-2:
                if ord('가')<=ord(line[line.find('lt')+2])<=ord('힣') or ord('1')<=ord(line[line.find('lt')+2])<=ord('9') or ord('A')<=ord(line[line.find('lt')+2])<=ord('Z'):
                    line=line.replace('lt','').replace('gt','')
        output.append(line)
    
    X_test_no=pd.Series(output)
    X_test=topic

    ## Pickle 파일 load
    index=pickle.load(open(TrainingFile+"_Simhash.pkl","rb"))
    bit_len=index.f
    k_value=index.k

    TrainingFile=str(TrainingFile).replace("_Simhash","")
    unit_setting=pickle.load(open(TrainingFile+"_unit_setting.pkl","rb"))

    X_train=pickle.load(open(TrainingFile+"_Metadata.pkl","rb"))

    unit=unit_setting['unit']
    unit_len=unit_setting['unit_len']

    if unit==1:
        unt='c'
    else:
        unt='w'
    
    index_list=[]
    for i in range(X_test_no.size):
        if unit==1:
            h_value=Simhash(get_features_char(unit_len,X_test_no[i]), f=bit_len)
        else:
            h_value=Simhash(get_features_word(unit_len,X_test_no[i]), f=bit_len)
        index_list.append(index.get_near_dups(h_value))
    ## Train columns 가져오기

    contents=X_train['제목']
    no_noise=X_train['Processing']
    publisher_id=X_train['게시자 ID']
    site=X_train['채널']
    url=X_train['게시글 URL']
    contents_number=X_train['고유번호']
    contents_size=X_train['용량']
    contents_class=X_train['분류']
    fp0=open('static/input/simhash/result.csv','wt')

    fp0.write('검색게시글,유포게시물,유포사이트,게시자id,URL,탐지시간,고유번호,분류,용량')
    fp0.write('\n')

    switch=0
    for i in range(X_test.size):
        if switch==0:
            fp0.write(str(X_test[i]).replace(',','')+',')
        if index_list[i]:
            for j in index_list[i]:
                if switch!=0:
                    fp0.write('-'+',')
                switch=1
                fp0.write(str(contents[int(j)]).replace(',','')+',')
                fp0.write(str(site[int(j)]).replace(',','')+',')
                fp0.write(str(publisher_id[int(j)]).replace(',','')+',')
                fp0.write(str(url[int(j)]).replace(',','')+',')
                now = datetime.datetime.now()
                nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                fp0.write(str(nowDatetime).replace(',','')+',')
                fp0.write(str(contents_number[int(j)]).replace(',','')+',')
                fp0.write(str(contents_class[int(j)]).replace(',','')+',')
                fp0.write(str(contents_size[int(j)]).replace(',',''))
                fp0.write('\n')
            switch=0
        else:
            fp0.write('\n')

    fp0.close()

    
def han_pattern(line):
    for cho in range(len(choseong)):
        if choseong[cho] in line:
            H_before=Han_Combination[choseong[cho]]
            H_after=Han_Combination[choseong[cho]+'`']
            for index in range(len(H_before)):
                if H_before[index] in line:
                    line=line.replace(H_before[index],H_after[index])
    return line
    
if __name__ == "__main__":              
    app.run(host="localhost", port=5000, use_reloader=False, debug=True)
