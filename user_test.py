import json
import time
import random
import datetime
import openpyxl
import requests
import numpy as np
import pandas as pd
import streamlit as st
from streamlit.web.server.server import Server
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx as get_report_ctx
import matplotlib.pyplot as plt
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from PIL import Image
from io import BytesIO
from github import Github
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""  
    use_data=user_data_read('user_data.csv')
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] in use_data['手机号'].astype(str).to_list():
            st.session_state["password_correct"] = True
            pass1=st.session_state["password"]
            if 'pass0' not in st.session_state:
                st.session_state.pass0=pass1
            else:
                st.session_state.pass0=pass1
            #del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
    # Show input for password.
    if st.session_state.get("password_correct", False):
        return True 
        
    st.text_input(
        "Password", type="password", on_change=password_entered,key="password")    

    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
        return False


def up_datefile():
    repo_owner = 'fangqx'
    repo_name = 'my_streamlit_app'
    file_path = 'share-study-room.xlsx'
    token = st.secrets["TOKEN"]
    commit_message = 'Update CSV file'
    github = Github(token)
    repo = github.get_user(repo_owner).get_repo(repo_name)
    url = f'https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/{file_path}'
    #url=f'https://github.com/{repo_owner}/{repo_name}/blob/master/test.csv'
    #response = requests.get(url)
    #st.write(response.content)
    df = pd.read_excel(url,sheet_name='basic',usecols="A:N")
    df['test_col'] = "12345"
    df.to_csv('tem.txt', index=False)
    
    with open('tem.txt', 'rb') as f:
        contents = f.read()

    all_files = []
    all = repo.get_contents("")
    while all:
        file_content = all.pop(0)
        if file_content.type == "dir":
            all.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
    #st.write(all_files)
    git_file="new_data.csv"
    if git_file in all_files:
        content = repo.get_contents(git_file)
        repo.update_file(content.path, commit_message,contents, content.sha)
    else:
        repo.create_file(git_file, "init commit", contents)
    #content = repo.get_contents("new_data.csv")
    #repo.delete_file("new_file.csv", "delete commit", content.sha)
    #repo.create_file("new_file.csv", "init commit", contents)
    #content = repo.get_contents(file_path)
    #repo.update_file(file_path, commit_message,contents, content.sha)
    return df

def user_data_read(file_path):
    repo_owner = 'fangqx'
    repo_name = 'my_streamlit_app'
    file_path = file_path
    token = st.secrets["TOKEN"]
    commit_message = 'create file'
    github = Github(token)
    repo = github.get_user(repo_owner).get_repo(repo_name)
    url = f'https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/{file_path}'
    #url=f'https://github.com/{repo_owner}/{repo_name}/blob/master/test.csv'
    #response = requests.get(url)
    #st.write(response.content)  
    all_files = []
    all = repo.get_contents("")
    while all:
        file_content = all.pop(0)
        if file_content.type == "dir":
            all.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
    #st.write(all_files)
    git_file=file_path
    if git_file in all_files:
        content = repo.get_contents(git_file)
        df0 = pd.read_csv(url)
        #df0=df0._append(df)
        #df0.to_csv('tem.txt', index=False)       
        #with open('tem.txt', 'rb') as f:
        #    contents = f.read()        
        #repo.update_file(content.path, commit_message,contents, content.sha)
        return df0
    else:
        df= pd.DataFrame()
        return df
    

def user_data_write(df,file_path):
    repo_owner = 'fangqx'
    repo_name = 'my_streamlit_app'
    file_path = file_path
    token = st.secrets["TOKEN"]
    commit_message = 'create file'
    github = Github(token)
    repo = github.get_user(repo_owner).get_repo(repo_name)
    url = f'https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/{file_path}'
    #url=f'https://github.com/{repo_owner}/{repo_name}/blob/master/test.csv'
    #response = requests.get(url)
    #st.write(response.content)  
    all_files = []
    all = repo.get_contents("")
    while all:
        file_content = all.pop(0)
        if file_content.type == "dir":
            all.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
    #st.write(all_files)
    git_file=file_path
    if git_file in all_files:
        content = repo.get_contents(git_file)
        df0 = pd.read_csv(url)
        df=df0._append(df)
        df.to_csv('tem.txt', index=False)       
        with open('tem.txt', 'rb') as f:
            contents = f.read()        
        repo.update_file(content.path, commit_message,contents, content.sha)
    else:
        df.to_csv('tem.txt', index=False)       
        with open('tem.txt', 'rb') as f:
            contents = f.read()                
        repo.create_file(git_file, "init commit", contents)
    return df



def main():    
    if not check_password():
        st.stop()
    st.title('自主学习--提高效率:heart:')
    use_data=user_data_read('user_data.csv')
    #st.write(use_data['手机号'].astype(str).to_list())
    your_data=use_data[use_data['手机号'].astype(str)==st.session_state.pass0]
    #st.dataframe(your_data)
    data=up_datefile()
    #st.set_page_config(page_title="自主学习",page_icon=":rainbow:",layout="wide",initial_sidebar_state="auto")
    st.session_state.date_time=datetime.datetime.now() + datetime.timedelta(hours=8) # Streamlit Cloud的时区是UTC，加8小时即北京时间
    if 'new_data' not in st.session_state:
        st.session_state.new_data = pd.DataFrame(columns=['姓名','手机号','学习卡', '日期', '时间段', '学习桌','预约次数'])
    col_xxk1,col_xxk2,col_xxk3=st.columns(3)
    xxk=your_data['学习卡'].astype(str).to_list()[0]
    xxt0=your_data['开始日期'].astype(str).to_list()[0]
    xxt1=your_data['结束日期'].astype(str).to_list()[0]
    xxn=your_data['姓名'].astype(str).to_list()[0]
    xxh=your_data['手机号'].astype(str).to_list()[0]
    if 'name' not in st.session_state:
        st.session_state.name = xxn
    else:
        st.session_state.name = xxn       
    if 'phone_num' not in st.session_state:
        st.session_state.phone_num = xxh
    else:
        st.session_state.phone_num = xxh         
    if 'card_type' not in st.session_state:
        st.session_state.card_type=xxk
    else:
        st.session_state.card_type=xxk
    
    with col_xxk1:
        x0=col_xxk1.markdown(f'###### 您的学习卡类型:  {xxk}')
    with col_xxk2:
        x1=col_xxk2.markdown(f'###### 您的开始日期:  {xxt0}')
    with col_xxk3:
        x2=col_xxk3.markdown(f'###### 您的结束日期:  {xxt1}')

    card_time=data[data['名称']==st.session_state.card_type].dropna(axis=1)        
    times_sel=card_time[card_time.columns[7:-1]].values.tolist()[0]
    cls1,cls2,cls3=st.columns(3)
    with cls1:
        tem=card_time['预约次数'].to_list()[0]
        xx0=cls1.markdown(f'###### 您的预约次数:  {tem}')
    with cls2:
        tem=card_time['有效期'].to_list()[0]      
        xx1=cls2.markdown(f'###### 您的有效期:  {tem}')
    with cls3:
        tem=card_time['预约时段是否可变'].to_list()[0]    
        xx2=cls3.markdown(f'###### 您的桌号:  {tem}')
    st.markdown(f'#### 请预约您的自修时间')
    with st.expander("学习时间选择",expanded=False):
        cols1,cols2=st.columns(2)
        ini_date=xxt0.split('-')
        end_date=xxt1.split('-')
        with cols1:
            sel_date=st.date_input('日期',value=datetime.date(int(ini_date[0]),int(ini_date[1]),int(ini_date[2])),min_value =datetime.date(int(ini_date[0]),int(ini_date[1]),int(ini_date[2])),max_value=datetime.date(int(end_date[0]),int(end_date[1]),int(end_date[2])))
            if sel_date !=None:
                if 'date_sel' not in st.session_state:
                    st.session_state.date_sel = sel_date
                else:
                    st.session_state.date_sel = sel_date 
            else:
                st.write('请选择学习日期!!!')
            #st.write(sel_new,card_name[:])
        with cols2:
            times=cols2.radio('时间段',times_sel)
            if 'times' not in st.session_state:
                st.session_state.times = times
            else:
                st.session_state.times = times     
        
    with st.expander("学习桌选择",expanded=False):
        desk_num=['桌号: 1','桌号: 2','桌号: 3','桌号: 5','桌号: 6','桌号: 7','桌号: 8','桌号: 9','桌号: 10','桌号: 11','桌号: 12','桌号: 13','桌号: 15','桌号: 16','桌号: 17']  #data['桌号'].dropna().unique().tolist()
        #col1, col2,col3 = st.columns(3)       
        #desk_ch1 = col1.radio(f"### 沉浸式课桌1-5", ['Option']+desk_num[:5],index=1,captions=['No Selection','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧'])
        #desk_ch2 = col2.radio(f"### 沉浸式课桌6-10",  ['Option']+desk_num[5:10],index=0,captions=['No Selection','靠走廊外侧','靠走廊外侧','靠走廊外侧','靠走廊外侧','靠走廊外侧'])
        #desk_ch3 = col3.radio(f"### 沉浸式课桌11-15",  ['Option']+desk_num[10:],index=0,captions=['No Selection','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧'])
        #sel0 =  [desk_ch1,desk_ch2,desk_ch3]
        #sel_new0=[]
        #for item in sel0:
        #    if item!='Option':
        #        sel_new0.append(item)               
        #if len(sel_new0)==1:
        #    st.write('您选择的是: ', sel_new0[0])
        #    if 'desk' not in st.session_state:
        #        st.session_state.desk = sel_new0[0]
        #    else:
        #        st.session_state.desk = sel_new0[0]       
        #else:                
        #    st.write('请重新选择桌号,您可能选择了一个以上的桌号')

        sel_new0= st.radio("沉浸式课桌1-15",desk_num[:],index=0,captions=['靠墙内侧(100cm)','靠墙内侧(100cm)','靠墙内侧(100cm)','靠墙内侧(100cm)','靠墙内侧(100cm)','靠走廊外侧(80cm)','靠走廊外侧(80cm)','靠走廊外侧(80cm)','靠走廊外侧(80cm)','靠走廊外侧(80cm)','靠墙内侧(80cm)','靠墙内侧(80cm)','靠墙内侧(80cm)','靠墙内侧(80cm)','靠墙内侧(80cm)'])

        st.write('您选择的是: ', sel_new0)
        if 'desk' not in st.session_state:
            st.session_state.desk = sel_new0
        else:
            st.session_state.desk = sel_new0
            
    user_file='user_schedule.csv'
    user_data = user_data_read(user_file)
    #st.write(user_data)
    if len(user_data)>=1:
        num0=user_data.shape[0]
        book_num=user_data[user_data['手机号']==st.session_state.phone_num].shape[0]
        #check time and desk
        other_user=user_data[user_data['手机号'].astype(str)!=st.session_state.phone_num]
        #st.write(other_user['日期'].astype(str))
        day_check=other_user[other_user['日期'].astype(str)==str(st.session_state.date_sel)]
        #st.write(day_check)
        time_check=day_check[day_check['时间'].astype(str)==st.session_state.times]
        #st.write(time_check)
        desk_check=time_check[time_check['学习桌'].astype(str)==st.session_state.desk]
        #st.write(desk_check)
        your_sel=user_data[user_data['手机号'].astype(str)==st.session_state.phone_num]
        your_sel=your_sel[your_sel['学习卡'].astype(str)==st.session_state.card_type]
        your_sel_time=your_sel.shape[0]
        your_time_check=your_sel[your_sel['日期'].astype(str)==str(st.session_state.date_sel)]
        your_time_check=your_time_check[your_time_check['时间'].astype(str)==st.session_state.times]    
    else:
        your_sel_time=0
        num0=0
    if 'your_sel_time' not in st.session_state:
        st.session_state.your_sel_time = your_sel_time
    else:
        st.session_state.your_sel_time = your_sel_time   
        
    if (len(user_data)>=1) and (desk_check.shape[0]>=1):
        st.markdown(f'##### 您选择的时间和桌号与他人冲突，请重新选择')
    elif(len(user_data)>=1) and (your_time_check.shape[0]>=1):
        st.markdown(f'##### 您选择的时间和上次选择的时间重合，请重新选择')
            
    else:    
        df_new = pd.DataFrame({'Date':st.session_state.date_time,'姓名':st.session_state.name,'手机号':st.session_state.phone_num,'学习卡': st.session_state.card_type,'日期': st.session_state.date_sel,'时间': st.session_state.times,'学习桌': st.session_state.desk,'预约次数':st.session_state.your_sel_time+1},index=[num0+1])   
        with st.expander("确认学习计划",expanded=False):            
            st.dataframe(df_new)     
            def disable():
                st.session_state.disabled = True
            
            # Initialize disabled for form_submit_button to False
            if "disabled" not in st.session_state:
                st.session_state.disabled = False
            
            with st.form("myform"):
                # Assign a key to the widget so it's automatically in session state
                submit_button = st.form_submit_button(
                    "确认正确", on_click=disable, disabled=st.session_state.disabled
                )
            
                if submit_button:
                    user_data_write(df_new,user_file) 
                    
    with st.expander("您的学习计划预约",expanded=False):
            new_user_data=user_data_read(user_file)
            your_all_data=user_data[user_data['手机号'].astype(str)==st.session_state.phone_num]
            st.dataframe(your_all_data,hide_index=True)


if __name__ == '__main__':

    main()
