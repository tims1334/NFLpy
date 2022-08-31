import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

#Enter desired years of data
year = st.sidebar.number_input('years', min_value=2018, max_value=2021, value=2021)
ay_max = st.sidebar.number_input('max air yards', min_value=-10, max_value=80, value=20)
ay_min = st.sidebar.number_input('min air yards', min_value=-10, max_value=80, value=5)
YEARS = [year]

data = pd.DataFrame()

@st.cache(allow_output_mutation=True)
def loadyears(YEARS, data):
    for i in YEARS:
        low_memory=False #eliminates a warning
        i_data = pd.read_csv('https://github.com/guga31bb/nflfastR-data/blob/master/data/' \
                         'play_by_play_' + str(i) + '.csv.gz?raw=True',
                         compression='gzip', low_memory=False)

    #sort=True eliminates a warning and alphabetically sorts columns
        data = data.append(i_data, sort=True)
    return data

data = loadyears(YEARS, data)


# Select QB
qbs = data.drop_duplicates('passer')
qb_list = qbs.passer.to_list()
qb_options = st.sidebar.multiselect('Pick QBs to compare',qb_list,default='T.Tagovailoa')
passes = data.loc[data.passer.isin(qb_options)]

# Group passers, mean stats
full_mean = passes.groupby('passer').mean()

air_passes = passes[['air_yards','air_wpa','air_epa','yards_gained','cp','cpoe','epa','passer']]
air_passes = air_passes.loc[(air_passes['air_yards']>=ay_min)&(air_passes['air_yards']<=ay_max)]
metrics = air_passes.columns.to_list()

st.header('Averages for each stat in NFLfastR')
st.dataframe(full_mean)


metric = st.sidebar.selectbox('Pick Metric',metrics)

#for i in range(len(qb_options)):
#    df[qb_options[i]] = air_passes.loc[air_passes['air_yards']==qb_options[i]]

c= alt.Chart(air_passes[['passer',metric]]).mark_bar(
opacity=0.3,
binSpacing=0
).encode(
alt.X(metric, bin=alt.Bin(maxbins=20)),
    alt.Y('count()',
    stack=None),
    alt.Color('passer'))
st.header('Counts')
st.altair_chart(c, use_container_width=True)
st.header('Percentage')
cb = alt.Chart(air_passes[['passer',metric]]).transform_joinaggregate(
    total='count(*)',
    groupby=['passer']
).transform_calculate(
    pct='1 / datum.total'
).mark_bar(
opacity=0.3,
binSpacing=0
).encode(
    alt.X(metric, bin=alt.Bin(maxbins=20)),
    alt.Y('sum(pct):Q', axis=alt.Axis(format='%'),stack=None),
    alt.Color('passer'))
st.altair_chart(cb, use_container_width=True)

wrs = data.loc[(data['pass_attempt']==1)]
st.write(len(wrs))

wr_stats = ['receiver','receiving_yards','touchdown',
            'xyac_epa','xyac_mean_yardage','yac_epa','yards_after_catch',
            'yards_gained', 'epa','cpoe', 'comp_yac_epa','complete_pass','cp',
            'air_yards','air_epa']

wrsdf = wrs[wr_stats]
wrs = wrsdf.groupby('receiver').mean()
metrics_w = wrs.columns.to_list()

wr_selection = wrs.index.drop_duplicates()
wr_selection = wr_selection.to_list()
wr_selections = st.sidebar.multiselect("Pick receivers", wr_selection, default='J.Waddle')
wrsd = wrs.loc[wrs.index.isin(wr_selections)]
wrsd = wrsd.reset_index()


metrics_w = st.sidebar.selectbox('Pick Metric',metrics_w)

wrsdf = wrsdf.loc[wrsdf['receiver'].isin(wr_selections)]

cw= alt.Chart(wrsdf[['receiver',metrics_w]]).mark_bar(
opacity=0.3,
binSpacing=0
).encode(
alt.X(metrics_w, bin=alt.Bin(maxbins=100)),
    alt.Y('count()',
    stack=None),
    alt.Color('receiver'))
st.header('Counts')
st.altair_chart(cw, use_container_width=True)
st.header('Percentage')
cbw = alt.Chart(wrsdf[['receiver',metrics_w]]).transform_joinaggregate(
    total='count(*)',
    groupby=['receiver']
).transform_calculate(
    pct='1 / datum.total'
).mark_area(
opacity=0.3,
binSpacing=0
).encode(
    alt.X(metrics_w, bin=alt.Bin(maxbins=50)),
    alt.Y('sum(pct):Q', axis=alt.Axis(format='%'),stack=None),
    alt.Color('receiver'))
st.altair_chart(cbw, use_container_width=True)