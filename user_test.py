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

def check_password(user_data):
    """Returns `True` if the user had the correct password."""    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] in user_data['手机号'].astype(str).to_list():
            st.session_state["password_correct"] = True
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
    else:
        st.write('个人信息不存在')
    return df0

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
        repo.create_file(content.path, "init commit", contents)
    return df



def main():    
    use_data=user_data_read('user_data.csv')
    st.write(use_data['手机号'].astype(str).to_list())
    if not check_password(use_data):
        st.stop()
    st.title('自主学习--提高效率:heart:')
    your_data=use_data[use_data['手机号'].astype(str)==st.session_state["password"]]
    st.dataframe(your_data)
    data=up_datefile()
    #st.set_page_config(page_title="自主学习",page_icon=":rainbow:",layout="wide",initial_sidebar_state="auto")
   
    st.session_state.date_time=datetime.datetime.now() + datetime.timedelta(hours=8) # Streamlit Cloud的时区是UTC，加8小时即北京时间
    
    if 'new_data' not in st.session_state:
        st.session_state.new_data = pd.DataFrame(columns=['姓名','手机号','学习卡', '日期', '时间段', '学习桌',])
    col_xxk1,col_xxk2,col_xxk3=st.columns(3)
    xxk=your_data['学习卡'].astype(str).to_list()[0]
    xxt0=your_data['开始日期'].astype(str).to_list()[0]
    xxt1=your_data['结束日期'].astype(str).to_list()[0]
    
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

    with st.expander("学习时间选择",expanded=True):
        cols1,cols2=st.columns(2)
        ini_date=xxt0.split('-')
        end_date=xxt1.split('-')
        with cols1:
            sel_date=st.date_input('开始日期',value=None,min_value =datetime.date(int(ini_date[0]),int(ini_date[1]),int(ini_date[2])),max_value=datetime.date(int(end_date[0]),int(end_date[1]),int(end_date[2])))
        #st.write(sel_new,card_name[:])
        with cols2:
            times=cols2.radio('时间段',times_sel)

        if 'date_sel1' not in st.session_state:
            st.session_state.date0 = date_sel1
        else:
            st.session_state.date0 = date_sel1     
            
        if 'times' not in st.session_state:
            st.session_state.date0 = times
        else:
            st.session_state.date0 = times     
        
    with st.expander("学习桌选择",expanded=True):
        desk_num=['桌号: 1','桌号: 2','桌号: 3','桌号: 5','桌号: 6','桌号: 7','桌号: 8','桌号: 9','桌号: 10','桌号: 11','桌号: 12','桌号: 13','桌号: 15','桌号: 16','桌号: 17']  #data['桌号'].dropna().unique().tolist()
        col1, col2,col3 = st.columns(3)       
        desk_ch1 = col1.radio(f"### 沉浸式课桌1-5", ['Option']+desk_num[:5],index=0,captions=['No Selection','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧'])
        desk_ch2 = col2.radio(f"### 沉浸式课桌6-10",  ['Option']+desk_num[5:10],index=0,captions=['No Selection','靠走廊外侧','靠走廊外侧','靠走廊外侧','靠走廊外侧','靠走廊外侧'])
        desk_ch3 = col3.radio(f"### 沉浸式课桌11-15",  ['Option']+desk_num[10:],index=0,captions=['No Selection','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧','靠墙内侧'])
        sel0 =  [desk_ch1,desk_ch2,desk_ch3]
        sel_new0=[]
        for item in sel0:
            if item!='Option':
                sel_new0.append(item)               
        if len(sel_new0)==1:
            st.write('您选择的是: ', sel_new0[0])
            if 'desk' not in st.session_state:
                st.session_state.desk = sel_new0[0]
            else:
                st.session_state.desk = sel_new0[0]       
        else:                
            st.write('请重新选择桌号')
            
    user_file='user_schedule.csv'
    user_data = user_data_read(user_file)
    check2 =  any(item in sel0 for item in desk_num[:])
    if (check1) and (len(sel_date)>=1):    
        df_new = pd.DataFrame({'姓名':st.session_state.name,'手机号':st.session_state.phone,'学习卡': st.session_state.card,'日期': sel_date,'时间': st.session_state.times,'学习桌': st.session_state.desk,},index=[st.session_state.new_data.shape[0]+1])   
        with st.expander("确认学习计划",expanded=True):            
            st.dataframe(df_new)     
            form0 = st.form('selection0')
            submitted0 = form0.form_submit_button("确认正确")
            if submitted0:
                user_data_write(df_new,user_file)    
                
                #st.session_state.new_data = st.data_editor(df_new0,num_rows='dynamic')
        with st.expander("修改学习计划",expanded=True):
            df_new0=st.session_state.new_data
            st.write('00',df_new0)
            st.session_state.edited_df1 = st.data_editor(df_new0, num_rows="dynamic")  
            form = st.form('selection')
            def save_edits0():
                st.session_state.df1 = st.session_state.edited_df1.copy()
            #st.session_state.edited_df1 = st.session_state.new_data.copy()                
            submitted = form.form_submit_button("修改计划",on_click=save_edits0)                 
            if submitted:
                df2=st.session_state.new_data
                user_data_save(df2,'user_data_old.csv')
                df1 = st.session_state.df1   
                st.dataframe(df1)
                user_data_save(df1,'user_data.csv')
                st.session_state.new_data=df1
                st.write(st.session_state.new_data)

                              
    
   

if __name__ == '__main__':

    main()
