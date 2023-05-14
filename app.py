import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time
from plotly.subplots import make_subplots

pio.templates["myname"] = go.layout.Template(
    layout=go.Layout(
        colorway=['rgb(103,0,31)', 'rgb(159,45,32)', 'rgb(253,219,199)',
                  'rgb(186,186,186)', 'rgb(77,77,77)', 'rgb(26,26,26)']
    ))
pio.templates.default = 'myname'
#template = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
template = "none"
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

def app_layout():
    pricing = pd.read_csv('Diploma1/milp/pricing.csv') 
    results_RBC = pd.read_csv('Diploma1/milp/results_RBC.csv') 
    results_RBC['method'] = ['RBC']*len(results_RBC)
    sim_results_RBC = pd.read_csv('Diploma1/milp/sim_results_RBC.csv')
    sim_results_RBC['method'] = ['RBC']*len(sim_results_RBC)
    results_RL = pd.read_csv('Diploma1/milp/results_RL.csv') 
    results_RL['method'] = ['RL']*len(results_RL)
    sim_results_RL = pd.read_csv('Diploma1/milp/sim_results_RL.csv')
    sim_results_RL['method'] = ['RL']*len(sim_results_RL)
    df1 =  pd.merge(results_RBC, sim_results_RBC)
    df1['date'] = pd.date_range(start='2022-01-01', freq='1h', periods=len(df1))
    
    df1 =  pd.merge(results_RL, sim_results_RL)
    df1['date'] = pd.date_range(start='2022-01-01', freq='1h', periods=len(df1))
    
    
    a = np.insert(np.array(df1['electrical_storage_soc']),0,0)
    a1 =a[1:]
    a = a[:-1]
    df1['electrical_storage'] = a - a1

    df1['electric_consumption']=-df1[['electric_consumption_cooling',
                                  'electric_consumption_dhw',
                                  'electric_consumption_cooling_storage',
                                  'electric_consumption_dhw_storage',
                                  'electrical_storage_electric_consumption',
                                  'non_shiftable_load']].sum(axis=1)
    df1['PGU'] = -df1[['electric_consumption','solar_gen','net_electric_consumption','electrical_storage']].sum(axis=1)
    df1.loc[(df1.PGU < 0), ('PGU')] = 0
    df1['net_electric_consumption'] = df1['net_electric_consumption']-df1[['electric_consumption','solar_gen','net_electric_consumption','electrical_storage','PGU']].sum(axis=1)
    df1['dhw_consumption'] = -df1['dhw_demand']
    df1['PGU_TERMAL'] = df1['dhw_heating_device_to_building'] + df1['PGU']/10#df1['dhw_heating_device_to_building']
    a = np.insert(np.array(df1['dhw_storage_soc']),0,0)
    a1 =a[1:]
    a = a[:-1]
    df1['termal_storage'] = a - a1
    df1['Boiler'] = -df1[['dhw_consumption','PGU_TERMAL','termal_storage']].sum(axis=1)
    df1.loc[(df1.Boiler < 0), ('Boiler')] = 0
    
    st.title("Система энергетического менеджмента")
    placeholder = st.empty()
    for seconds in range(0, len(df1) - 96*2):
        currentdata = df1.iloc[seconds]
        previous96data = df1.iloc[:seconds].tail(24)
        next96data = df1.iloc[seconds:seconds + 24]
        pricing_previous = pricing.iloc[:seconds].tail(24)
        pricing_previous.rename(columns = {'Electricity Pricing [$]' : 'Цены на электроэнергию [$]'}, inplace = True)
        pricing_currentdata = pricing.iloc[seconds]
        with placeholder.container():
            st.write('Текущая дата',currentdata['date'])
            dat = currentdata[['electric_consumption',
                                'solar_gen','net_electric_consumption','electrical_storage','PGU']]
            dat = {'электропотребление':[currentdata['electric_consumption']],
                   'теплопотребление':[currentdata['dhw_consumption']],
                   'солнечная генерация':[currentdata['solar_gen']],
                   'сетевое электропотребление':[currentdata['net_electric_consumption']],
                   'электроэнергия PGU':[currentdata['PGU']],
                   'теплоэнергия PGU':[currentdata['PGU_TERMAL']],
                   'бойлер':[currentdata['Boiler']],
                   'Тариф':[pricing_currentdata['Electricity Pricing [$]']],
                   
                  }
            DAT = pd.DataFrame(dat)
            st.dataframe(DAT.rename(index={0:currentdata['date'].hour}),use_container_width= True) 
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write('Состояние заряда электрического хранилища')
                p = 100*currentdata['electrical_storage_soc']/max(df1['electrical_storage_soc'])
                if p < 1:
                    st.image('Diploma1/milp/bat_0.png', width=200,use_column_width = 'auto')
                
                elif 1 <= p < 16:
                    st.image('Diploma1/milp/bat_16.png', width=200,use_column_width = 'auto')
                    
                elif 16 <= p < 33:
                    st.image('Diploma1/milp/bat_33.png', width=200,use_column_width = 'auto')
                    
                elif 33 <= p < 60:
                    st.image('Diploma1/milp/bat_50.png', width=200,use_column_width = 'auto')
                    
                elif 60 <= p < 80:
                    st.image('Diploma1/milp/bat_66.png', width=200,use_column_width = 'auto')
                    
                elif 80 <= p < 95:
                    st.image('Diploma1/milp/bat_83.png', width=200,use_column_width = 'auto')
                else:
                    st.image('Diploma1/milp/bat_100.png', width=200,use_column_width = 'auto')
                st.write(p,'%')
            with col2:
                st.write('Состояние заряда теплового хранилища')
                p = 100*currentdata['dhw_storage_soc']/max(df1['dhw_storage_soc'])
                if p < 1:
                    st.image('Diploma1/milp/bat_0.png', width=200,use_column_width = 'auto')
                
                elif 1 <= p < 16:
                    st.image('Diploma1/milp/bat_16.png', width=200,use_column_width = 'auto')
                    
                elif 16 <= p < 33:
                    st.image('Diploma1/milp/bat_33.png', width=200,use_column_width = 'auto')
                    
                elif 33 <= p < 60:
                    st.image('Diploma1/milp/bat_50.png', width=200,use_column_width = 'auto')
                    
                elif 60 <= p < 80:
                    st.image('Diploma1/milp/bat_66.png', width=200,use_column_width = 'auto')
                    
                elif 80 <= p < 95:
                    st.image('Diploma1/milp/bat_83.png', width=200,use_column_width = 'auto')
                else:
                    st.image('Diploma1/milp/bat_100.png', width=200,use_column_width = 'auto')
                st.write(p,'%')
            col1, col2 = st.columns([1, 1])
            with col1:
                
                st.write('Тариф на электроэнергию')
                fig = px.line(pricing_previous, y="Цены на электроэнергию [$]")
                fig.update_layout(width=1700, height=300, barmode="relative")
                st.plotly_chart(fig,use_container_width=True)
            with col2:
                st.write('Затраты на покупку энергоресурсов')
                d = pd.DataFrame({'Затраты на электроэнергию [$]':previous96data['net_electric_consumption']*pricing_previous['Цены на электроэнергию [$]']})
                fig = px.line(d, y="Затраты на электроэнергию [$]")
                fig.update_layout(width=1700, height=300, barmode="relative")
                st.plotly_chart(fig,use_container_width=True)
            
            st.title("Анализ работы контроллера")
            #st.write('Профили энергопотребления')
            col1, col2 = st.columns([1, 1])
            with col1:
                dat = previous96data[previous96data.method == 'RL'][['electric_consumption',
                                'solar_gen','net_electric_consumption','electrical_storage','PGU']]

                st.write('Профиль электрического баланса')
            
                fig = px.bar(data_frame=dat)

                fig.update_layout(width=1700, height=350, barmode="relative")
                newnames = {'electric_consumption':'электропотребление','solar_gen':'производство солнечной энергии',
                'net_electric_consumption':'сетевое электропотребление',
                'electrical_storage':'мощность электрического накопителя','PGU':'электроэнергия когенерации'}
                fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
            
                st.write('Профиль теплового баланса')
            
                dat = previous96data[previous96data.method == 'RL'][['dhw_consumption','PGU_TERMAL','termal_storage','Boiler']]
                fig = px.bar(data_frame=dat)
                fig.update_layout(width=1700, height=350, barmode="relative")
                newnames = {'dhw_consumption':'теплопотребление','Boiler':'бойлер',
                'net_electric_consumption':'сетевое электропотребление',
                'termal_storage':'мощность теплового накопителя','PGU_TERMAL':'теплоэнергия когенерации'}
                fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                st.plotly_chart(fig, use_container_width=True)
            
            #st.write('Состояние заряда накопительных элементов')
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write('Электрическое хранилище')
                dat = previous96data[previous96data.method == 'RL'][['electrical_storage_soc']]
                fig = px.bar(data_frame=dat)
                newnames = {'electrical_storage_soc':'заряд электрического накопителя'}
                fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                fig.update_layout(width=1700, height=300, barmode="relative")
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.write('Тепловое хранилище')
                dat = previous96data[previous96data.method == 'RL'][['dhw_storage_soc']]
                fig = px.bar(data_frame=dat)
                newnames = {'dhw_storage_soc':'заряд теплового накопителя'}
                fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                fig.update_layout(width=1700, height=300, barmode="relative")
                st.plotly_chart(fig, use_container_width=True)
        
            
            
            time.sleep(0.3)
            
            
            
            
if __name__=='__main__':
    app_layout()

