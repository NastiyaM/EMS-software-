import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def data_send(now):
    df = pd.read_csv('RL_system/static/data.csv', index_col=0)
    df['current_time'] = pd.to_datetime(df['current_time'].apply(lambda x: x[:-5]))
    diff = (pd.to_datetime(now).round('min') - pd.to_datetime('2014-08-28 21:30')).days - 1
    df['current_time'] = df['current_time'] + datetime.timedelta(days=diff)
    temp_df = df[df['current_time'] < pd.to_datetime(datetime.datetime.now())]
    last_index = temp_df.index.max()
    data = dict(temp_df.loc[last_index])
    df_plot = temp_df[-96::]

    metrics_show = ['actual_consumption', 'actual_pv', 'price_buy', 'price_sell', 'grid_energy', 'current_charge']
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for Metric in metrics_show:
        if Metric in ('price_buy', 'price_sell'):
            axes_y = True
        else:
            axes_y = False
        fig.add_trace(
            go.Scatter(
                x=df_plot['current_time'],
                y=df_plot[Metric],
                mode='lines',
                name=Metric
            ),
            secondary_y=axes_y
        )

    fig.update_layout(
        title_text="Распределение метрик"
    )
    fig.update_xaxes(title_text="Время")
    fig.update_yaxes(title_text="€/kW", secondary_y=True)
    fig.update_yaxes(title_text="kW", secondary_y=False)

    graph = fig.to_html(full_html=False, default_height=600, default_width=1200)
    data['graph'] = graph
    return data
