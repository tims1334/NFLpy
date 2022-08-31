import nfl_data_py as nfl
import pandas as pd
import streamlit as st
import altair as alt

st.sidebar.header('Choose Seasons')
year_min = st.sidebar.number_input('First Season',min_value=2018, max_value=2022,value=2021)
year_max = st.sidebar.number_input('Last Season',min_value=2018, max_value=2022,value=2021)
chosen_years = []
chosen_years.extend(range(int(year_min), int(year_max)+1))
st.sidebar.header('Choose Air Yards Range')
ay_max = st.sidebar.number_input('Max Air Yards', min_value=-10, max_value=80, value=20)
ay_min = st.sidebar.number_input('Min Air Yards', min_value=-10, max_value=80, value=5)
min_att = st.sidebar.number_input('Minimum Number of Attempts', min_value=1, max_value=2000, value = 15)
binsize = st.sidebar.number_input('Bin Size', min_value=5, max_value=100, value = 20)

@st.cache
def get_data():
    data = nfl.import_pbp_data(years=chosen_years,downcast=False,cache=False)
    return data

data = get_data()

qbs = data.drop_duplicates('passer')
qb_list = qbs.passer.to_list()
qb_options = st.sidebar.multiselect('Pick QBs to compare',qb_list,default='T.Tagovailoa')
passes = data.loc[data.passer.isin(qb_options)]

# Group passers

air_passes = passes[['air_yards','air_wpa','air_epa','yards_gained','cp','cpoe','epa','passer','pass_touchdown','interception']]
air_passes = air_passes.loc[(air_passes['air_yards']>=ay_min)&(air_passes['air_yards']<=ay_max)]
metrics = air_passes.columns.to_list()
metric = st.sidebar.selectbox('Pick Metric',metrics)

### Layouts
tab1, tab2, tab3 = st.tabs(["QB Charts","QB Table","WR Charts"])
col1, col2 = st.columns(2)

### Passer Charts
tab1.header("QB Charts")

c = alt.Chart(air_passes[['passer',metric]]).mark_bar(
opacity=0.3,
binSpacing=0
).encode(
alt.X(metric, bin=alt.Bin(maxbins=binsize)),
    alt.Y('count()',
    stack=None),
    alt.Color('passer'))

### Counts
tab1.header('Counts')
tab1.altair_chart(c, use_container_width=True)

### Percentages
tab1.header('Percentage')
cb = alt.Chart(air_passes[['passer',metric]]).transform_joinaggregate(
    total='count(*)',
    groupby=['passer']
).transform_calculate(
    pct='1 / datum.total'
).mark_bar(
opacity=0.3,
binSpacing=0
).encode(
    alt.X(metric, bin=alt.Bin(maxbins=binsize)),
    alt.Y('sum(pct):Q', axis=alt.Axis(format='%'),stack=None),
    alt.Color('passer'))
tab1.altair_chart(cb, use_container_width=True)


### WRs
tab3.header("WR Charts")

wrs = data.loc[(data['pass_attempt']==1)]

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

cw = alt.Chart(wrsdf[['receiver',metrics_w]]).mark_bar(
opacity=0.3,
binSpacing=0
).encode(
alt.X(metrics_w, bin=alt.Bin(maxbins=binsize)),
    alt.Y('count()',
    stack=None),
    alt.Color('receiver'))
### Counts
tab3.subheader('Counts')
tab3.altair_chart(cw, use_container_width=True)
### Percentages
tab3.subheader('Percentage')
cbw = alt.Chart(wrsdf[['receiver',metrics_w]]).transform_joinaggregate(
    total='count(*)',
    groupby=['receiver']
).transform_calculate(
    pct='1 / datum.total'
).mark_area(
opacity=0.3,
binSpacing=0
).encode(
    alt.X(metrics_w, bin=alt.Bin(maxbins=binsize)),
    alt.Y('sum(pct):Q', axis=alt.Axis(format='%'),stack=None),
    alt.Color('receiver'))
tab3.altair_chart(cbw, use_container_width=True)

### QB Table
tab2.header("QB Table")
qbdf = data.loc[(data['air_yards'] >= ay_min) & (data['air_yards'] <= ay_max)]
qbdf['plays'] = 1
qbdf = qbdf.groupby(['passer']).agg(mean_epa=('epa','mean'),
                                    total_epa=('epa','sum'),
                                    mean_air_epa=('air_epa','mean'),
                                    total_air_epa=('air_epa','sum'),
                                    ints = ('interception','sum'),
                                    tds = ('pass_touchdown','sum'),
                                    completion_probability_mean = ('cp','mean'),
                                    completion_percent_over_expected_mean = ('cpoe','mean'),
                                    total_plays=('plays','sum')).reset_index()
qbdf = qbdf.loc[qbdf['total_plays']>=min_att]
tab2.dataframe(qbdf.sort_values('total_plays', ascending=False))
