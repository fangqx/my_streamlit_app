import json
import time
import random
import datetime
import openpyxl
import requests
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_echarts import st_echarts
from streamlit.web.server.server import Server
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx as get_report_ctx
import pydeck as pdk
import matplotlib.pyplot as plt
from pyecharts.charts import *
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from PIL import Image
from io import BytesIO
from github import Github
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
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
    df = pd.read_excel(url,sheet_name='all')
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

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    
    if not check_password():
        st.stop()
    data=up_datefile()
    st.set_page_config(page_title="自主学习",page_icon=":rainbow:",layout="wide",initial_sidebar_state="auto")
    st.title('自主学习--提高效率:heart:')
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    charts_mapping={
        'Line':'line_chart','Bar':'bar_chart','Area':'area_chart','Hist':'pyplot','Altair':'altair_chart',
        'Map':'map','Distplot':'plotly_chart','Pdk':'pydeck_chart','Graphviz':'graphviz_chart','PyEchart':''
    }
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit=True
    else:
        st.session_state.first_visit=False
    # 初始化全局配置
    if st.session_state.first_visit:
        # 在这里可以定义任意多个全局变量，方便程序进行调用
        st.session_state.date_time=datetime.datetime.now() + datetime.timedelta(hours=8) # Streamlit Cloud的时区是UTC，加8小时即北京时间
        st.session_state.random_chart_index=random.choice(range(len(charts_mapping)))
        st.session_state.my_random=MyRandom(random.randint(1,1000000))
        st.session_state.city_mapping,st.session_state.random_city_index=get_city_mapping()
        # st.session_state.random_city_index=random.choice(range(len(st.session_state.city_mapping)))
        #st.balloons()
        #st.snow()
    study_sel=['自习卡类型','自习时间','自习位置']
    self_study=st.sidebar.radio('自习计划选择',study_sel,index=0)
    
    if 'new_data' not in st.session_state:
        st.session_state.new_data = pd.DataFrame(columns=['学习卡', '开始日期', '结束日期', '开始时间', '结束时间'])
    
    if self_study==study_sel[0]:
        with st.container():
            card_name=data['名称'].dropna().unique().tolist()
            card_price0=data['价格'].dropna().unique().tolist()
            card_price=['--价格: '+str(x)+' 元' for x in card_price0]
            #card_name = [a+b for a, b in zip(card_name, card_price)]
            
            with st.expander("学习卡选择"):
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
                        
                else:                
                    st.write('请重新选择')
    
            with st.expander("学习时间选择"):
                #st.write(sel_new,card_name[:])
                check =  any(item in sel_new for item in card_name[:])
                if check is True:
                    st.markdown(sel_new[0])
                    
                    cols=st.columns(2)
                    col0=cols[0].date_input('开始日期',st.session_state.date_time)
                    col1=cols[1].date_input('结束日期',st.session_state.date_time,)
                    cols=st.columns(2)
                    col2=cols[0].time_input('开始时间',value=None,step=3600)
                    col3=cols[1].time_input('结束时间',value=None,step=3600)
                    st.write(col3)

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
                
                df_new = pd.DataFrame({'学习卡': st.session_state.card,'开始日期': st.session_state.date0,'结束日期': st.session_state.date1,'开始时间': st.session_state.time0,'结束时间': st.session_state.time1})   
                st.write('请确认您的自习卡',df_new)
                form = st.form('selection')
                submitted = form.form_submit_button("确定")
                if submitted:
                    st.session_state.new_data = pd.concat([st.session_state.new_data, df_new], axis=0)
                    st.dataframe(st.session_state.new_data)
                    st.write(st.session_state.new_data)
                #form = st.form('时间选择')
                #submitted = form.form_submit_button("确定")
                
                    
                                        
    
    d=st.sidebar.date_input('Date',st.session_state.date_time.date())
    t=st.sidebar.time_input('Time',st.session_state.date_time.time())
    t=f'{t}'.split('.')[0]
    st.sidebar.write(f'The current date time is {d} {t}')
    
    chart=st.sidebar.selectbox('Select Chart You Like',charts_mapping.keys(),index=st.session_state.random_chart_index)
    city=st.sidebar.selectbox('Select City You Like',st.session_state.city_mapping.keys(),index=st.session_state.random_city_index)
    color = st.sidebar.color_picker('Pick A Color You Like', '#520520')
    st.sidebar.write('The current color is', color)

    with st.container():
        st.markdown(f'### {city} Weather Forecast')
        forecastToday,df_forecastHours,df_forecastDays=get_city_weather(st.session_state.city_mapping[city])
        col1,col2,col3,col4,col5,col6=st.columns(6)
        col1.metric('Weather',forecastToday['weather'])
        col2.metric('Temperature',forecastToday['temp'])
        col3.metric('Body Temperature',forecastToday['realFeel'])
        col4.metric('Humidity',forecastToday['humidity'])
        col5.metric('Wind',forecastToday['wind'])
        col6.metric('UpdateTime',forecastToday['updateTime'])
        c1 = (
            Line()
            .add_xaxis(df_forecastHours.index.to_list())
            .add_yaxis('Temperature', df_forecastHours.Temperature.values.tolist())
            .add_yaxis('Body Temperature', df_forecastHours['Body Temperature'].values.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="24 Hours Forecast"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
                )
            .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
        )

        c2 = (
            Line()
            .add_xaxis(xaxis_data=df_forecastDays.index.to_list())
            .add_yaxis(series_name="High Temperature",y_axis=df_forecastDays.Temperature.apply(lambda x:int(x.replace('°C','').split('~')[1])))
            .add_yaxis(series_name="Low Temperature",y_axis=df_forecastDays.Temperature.apply(lambda x:int(x.replace('°C','').split('~')[0])))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="7 Days Forecast"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
                )
            .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
        )

        t = Timeline(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width='1200px'))
        t.add_schema(play_interval=10000,is_auto_play=True)
        t.add(c1, "24 Hours Forecast")
        t.add(c2, "7 Days Forecast")
        components.html(t.render_embed(), width=1200, height=520)
        with st.expander("24 Hours Forecast Data"):
            st.table(df_forecastHours.style.format({'Temperature':'{}°C','Body Temperature':'{}°C','Humidity':'{}%'}))
        with st.expander("7 Days Forecast Data",expanded=True):
            st.table(df_forecastDays)

    st.markdown(f'### {chart} Chart')
    df=get_chart_data(chart,st.session_state.my_random)
    eval(f'st.{charts_mapping[chart]}(df{",use_container_width=True" if chart in ["Distplot","Altair"] else ""})' if chart != 'PyEchart' else f'st_echarts(options=df)')

    st.markdown('### Animal Pictures')
    pictures=get_pictures(st.session_state.my_random)
    if pictures:
        col=st.columns(len(pictures))
        for idx,(name,img) in enumerate(pictures.items()):
            eval(f"col[{idx}].image(img, caption=name,use_column_width=True)")
    else:
        st.warning('Get pictures fail.')

    st.markdown('### Some Ads Videos')
    session_id = get_report_ctx().session_id
    sessions = Server.get_current()._session_info_by_id
    session_ws = sessions[session_id].ws
    st.sidebar.info(f'当前在线人数：{len(sessions)}')
    col1,col2=st.columns(2)
    video1,video2=get_video_bytes()
    col1.video(video1, format='video/mp4', start_time=2)
    col2.video(video2, format='video/mp4')
    # if session_ws is not None:
    #     session_headers = session_ws.request.headers
    #     if 'Windows' not in session_headers['User-Agent']:
    #         st.info(f"Sorry!!!  \nOnly show videos on PC")
    #     else:
    #         col1,col2=st.columns(2)
    #         video1=get_video_bytes('开不了口')
    #         col1.video(video1)
    #         video2=get_video_bytes('最长的电影')
    #         col2.video(video2, format='video/mp4')
    # else:
    #     st.info('Please refresh the page.')

    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('### About Me')
    with open('README.md','r') as f:
        readme=f.read()
    st.markdown(readme)

    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    with st.expander("View Code"):
        with open('my_streamlit.py','r') as f:
            code=f.read()
        with open('my_streamlit0.py','w') as f:
            f.write(code)
        st.code(code,language="python")

class MyRandom:
    def __init__(self,num):
        self.random_num=num

def my_hash_func(my_random):
    num = my_random.random_num
    return num


@st.cache(hash_funcs={MyRandom: my_hash_func},suppress_st_warning=True,ttl=3600)
def get_pictures(my_random):
    def _get_one(url,what):
        try:
            img=Image.open(BytesIO(requests.get(requests.get(url,timeout=15).json()[what]).content))
            return img
        except Exception as e:
            if 'cannot identify image file' in str(e):
                return _get_one(url,what)
            else:
                return False
    imgs={}
    mapping={
        'https://aws.random.cat/meow':{'name':'A Cat Picture','what':'file'},
        'https://random.dog/woof.json':{'name':'A Dog Picture','what':'url'},
        'https://randomfox.ca/floof/':{'name':'A Fox Picture','what':'image'},
    }
    for url,url_map in mapping.items():
        img=_get_one(url,url_map['what'])
        if img:
            imgs[url_map['name']]=img

    return imgs

@st.cache(ttl=3600)
def get_city_mapping():
    url='https://h5ctywhr.api.moji.com/weatherthird/cityList'
    r=requests.get(url)
    data=r.json()
    city_mapping=dict()
    guangzhou=0
    flag=True
    for i in data.values():
        for each in i:
            city_mapping[each['name']]=each['cityId']
            if each['name'] != '广州市' and flag:
                guangzhou+=1
            else:
                flag=False

    return city_mapping,guangzhou

@st.cache(ttl=3600)
def get_city_weather(cityId):
    url='https://h5ctywhr.api.moji.com/weatherDetail'
    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    data={"cityId":cityId,"cityType":0}
    r=requests.post(url,headers=headers,json=data)
    result=r.json()

    # today forecast
    forecastToday=dict(
        humidity=f"{result['condition']['humidity']}%",
        temp=f"{result['condition']['temp']}°C",
        realFeel=f"{result['condition']['realFeel']}°C",
        weather=result['condition']['weather'],
        wind=f"{result['condition']['windDir']}{result['condition']['windLevel']}级",
        updateTime=(datetime.datetime.fromtimestamp(result['condition']['updateTime'])+datetime.timedelta(hours=8)).strftime('%H:%M:%S')
    )

    # 24 hours forecast
    forecastHours=[]
    for i in result['forecastHours']['forecastHour']:
        tmp={}
        tmp['PredictTime']=(datetime.datetime.fromtimestamp(i['predictTime'])+datetime.timedelta(hours=8)).strftime('%H:%M')
        tmp['Temperature']=i['temp']
        tmp['Body Temperature']=i['realFeel']
        tmp['Humidity']=i['humidity']
        tmp['Weather']=i['weather']
        tmp['Wind']=f"{i['windDesc']}{i['windLevel']}级"
        forecastHours.append(tmp)
    df_forecastHours=pd.DataFrame(forecastHours).set_index('PredictTime')

    # 7 days forecast
    forecastDays=[]
    day_format={1:'昨天',0:'今天',-1:'明天',-2:'后天'}
    for i in result['forecastDays']['forecastDay']:
        tmp={}
        now=datetime.datetime.fromtimestamp(i['predictDate'])+datetime.timedelta(hours=8)
        diff=(st.session_state.date_time-now).days
        festival=i['festival']
        tmp['PredictDate']=(day_format[diff] if diff in day_format else now.strftime('%m/%d')) + (f' {festival}' if festival != '' else '')
        tmp['Temperature']=f"{i['tempLow']}~{i['tempHigh']}°C"
        tmp['Humidity']=f"{i['humidity']}%"
        tmp['WeatherDay']=i['weatherDay']
        tmp['WeatherNight']=i['weatherNight']
        tmp['WindDay']=f"{i['windDirDay']}{i['windLevelDay']}级"
        tmp['WindNight']=f"{i['windDirNight']}{i['windLevelNight']}级"
        forecastDays.append(tmp)
    df_forecastDays=pd.DataFrame(forecastDays).set_index('PredictDate')
    return forecastToday,df_forecastHours,df_forecastDays

@st.experimental_singleton
def get_audio_bytes(music):
    audio_file = open(f'music/{music}-周杰伦.mp3', 'rb')
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes

@st.experimental_singleton
def get_video_bytes():
    video_file = open(f'video/开不了口-广告曲.mp4', 'rb')
    video_bytes1 = video_file.read()
    video_file.close()
    video_file = open(f'video/最长的电影-广告曲.mp4', 'rb')
    video_bytes2 = video_file.read()
    video_file.close()
    return video_bytes1,video_bytes2

if __name__ == '__main__':

    main()
