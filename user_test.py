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
    df = pd.read_excel(url,sheet_name='basic')
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

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Save edits by copying edited dataframes to "original" slots in session state


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
    
    study_sel=['自习卡类型','自习时间','自习位置']
    self_study=st.sidebar.radio('自习计划选择',study_sel,index=0)
    
    if 'new_data' not in st.session_state:
        st.session_state.new_data = pd.DataFrame(columns=['姓名','手机号','日期','学习卡', '开始日期', '结束日期', '开始时间', '结束时间','学习桌','价格','折扣','最终价格'])
    
    st.markdown(f'### 您的学习卡类型:')
    st.write(your_data['学习卡'])
    if self_study==study_sel[0]:
        with st.container():
            card_name=data['名称'].tolist()
            card_price0=data['价格'].tolist()
            card_price=['--价格: '+str(x)+' 元' for x in card_price0]
            #card_name = [a+b for a, b in zip(card_name, card_price)]
            
            with st.expander("学习卡选择",expanded=True):
                #st.markdown(f'### 学习计划')
                col1, col2,col3 = st.columns(3)       
                col1_choice = col1.radio(f"### 单次卡", ['Option']+card_name[:4],index=0,captions=['No Selection']+card_price[:4])
                col2_choice = col2.radio(f"### 多次卡",  ['Option']+card_name[4:9],index=0,captions=['No Selection']+card_price[4:9])
                col3_choice = col3.radio(f"### 长期卡",  ['Option']+card_name[9:],index=0,captions=['No Selection']+card_price[9:])
                #card=st.radio('study',data['名称'].dropna().unique().tolist())
                sel =  [col1_choice,col2_choice,col3_choice]
                sel_new=[]
                for item in sel:
                    if item!='Option':
                        sel_new.append(item)               
                if len(sel_new)==1:
                    st.write('您选择的是: ', sel_new[0])
                    if 'card' not in st.session_state:
                        st.session_state.card = sel_new[0]
                    else:
                        st.session_state.card = sel_new[0]
                    if 'price_sel0' not in st.session_state:
                        st.session_state.price_sel0 = data[data['名称']==st.session_state.card]
                    else:
                        st.session_state.price_sel0 = data[data['名称']==st.session_state.card]   
                else:                
                    st.write('请重新选择')
                
            
            with st.expander("学习时间选择",expanded=True):
                #st.write(sel_new,card_name[:])
                check =  any(item in sel_new for item in card_name[:])
                if check is True:
                    st.markdown(sel_new[0])
                    
                    cols=st.columns(2)
                    col0=cols[0].date_input('开始日期',st.session_state.date_time)
                    col1=cols[1].date_input('结束日期',st.session_state.date_time,)
                    cols=st.columns(2)
                    col2=cols[0].time_input('开始时间',value='now',step=3600)
                    col3=cols[1].time_input('结束时间',value='now',step=3600)
                    if 'date0' not in st.session_state:
                        st.session_state.date0 = col0
                    else:
                        st.session_state.date0 = col0     

                    if 'date1' not in st.session_state:
                        st.session_state.date1 = col1
                    else:
                        st.session_state.date1 = col1                         

                    if 'time0' not in st.session_state:
                        st.session_state.time0 = col2
                    else:
                        st.session_state.time0 = col2                         
                    if 'time1' not in st.session_state:
                        st.session_state.time1 = col3
                    else:
                        st.session_state.time1 = col3   
                    if (col0<=col1) and (col2<=col3):
                        st.write('您选择的是: ', '开始日期', col0, '结束日期', col1, '开始时间', col2, '结束时间', col3)    
                    else:                
                        st.write('请重新选择时间段')

            
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
                    
            with st.expander("个人信息输入",expanded=True):
                if "visibility" not in st.session_state:
                    st.session_state.visibility = "visible"
                    st.session_state.disabled = False
                
                col10, col20, col30 = st.columns(3)                
                with col10:
                    text_input0 = st.text_input(
                        "您的姓名 👇",
                        label_visibility=st.session_state.visibility,
                        disabled=st.session_state.disabled,
                    )
                    if text_input0:
                        st.write("You entered: ", text_input0)
                        if 'name' not in st.session_state:
                            st.session_state.name = text_input0
                        else:
                            st.session_state.name = text_input0   
                with col20:
                    text_input1 = st.text_input(
                        "您的手机号 👇",
                        label_visibility=st.session_state.visibility,
                        disabled=st.session_state.disabled,
                    )
                
                    if text_input1:
                        st.write("You entered: ", text_input1)
    
                        if 'phone' not in st.session_state:
                            st.session_state.phone = text_input1
                        else:
                            st.session_state.phone = text_input1          
                with col30:
                    text_input2 = st.text_input(
                        "折扣：100-50 👇", value=100
                        
                    )
                    if text_input2:
                        st.write("You entered: ", text_input2)
                        if 'percent' not in st.session_state:
                            st.session_state.percent = text_input2
                        else:
                            st.session_state.percent = text_input2                      
              
            check1 =  any(item in sel for item in card_name[:])
            check2 =  any(item in sel0 for item in desk_num[:])
            if (check1) and (check2) and (text_input0) and (text_input1) and (text_input2):
                if 'final_price' not in st.session_state:
                    st.session_state.final_price = float(st.session_state.percent)*float(st.session_state.price_sel0['价格'].to_list()[0])*0.01
                else:
                    st.session_state.final_price = float(st.session_state.percent)*float(st.session_state.price_sel0['价格'].to_list()[0])*0.01              
                df_new = pd.DataFrame({'姓名':st.session_state.name,'手机号':st.session_state.phone,'日期':st.session_state.date_time,'学习卡': st.session_state.card,'开始日期': st.session_state.date0,'结束日期': st.session_state.date1,'开始时间': st.session_state.time0,'结束时间': st.session_state.time1,'学习桌': st.session_state.desk,'价格':st.session_state.price_sel0['价格'].to_list()[0],'折扣':st.session_state.percent,'最终价格':st.session_state.final_price},index=[st.session_state.new_data.shape[0]+1])   
                with st.expander("确认学习计划",expanded=True):
                    st.dataframe(df_new)
                    form0 = st.form('selection0')
                    submitted0 = form0.form_submit_button("确认正确")
                    if submitted0:
                        st.session_state.new_data = pd.concat([st.session_state.new_data, df_new], axis=0)
                        st.dataframe(st.session_state.new_data)                        
                        
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

                              
    
    d=st.sidebar.date_input('Date',st.session_state.date_time.date())
    t=st.sidebar.time_input('Time',st.session_state.date_time.time())
    t=f'{t}'.split('.')[0]
    st.sidebar.write(f'The current date time is {d} {t}')
    
   

if __name__ == '__main__':

    main()
