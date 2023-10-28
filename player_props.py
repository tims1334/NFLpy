import nfl_data_py as nfl
import streamlit as st
import plotly.figure_factory as ff
import pandas as pd
import scipy

# Get Data
data = pd.DataFrame()

@st.cache_data
def get_plays(YEARS, data):
    data = nfl.import_pbp_data(years=YEARS, downcast=False, cache=False)
    return data
@st.cache_data
def get_rosters(years):
    data = nfl.import_seasonal_rosters(years)
    return data

# styler
def make_pretty(styler):
    styler.background_gradient(axis=1, cmap="BuGn")
    return styler

### Choose Seasons and Weeks

years = []
years.extend(range(int(2010), int(2023)+1))
choose_years = st.sidebar.multiselect("Select Years:", years, default=2023)

weeks = list(range(1,23)) 
chose_weeks = st.sidebar.multiselect("Choose Weeks:", weeks,weeks)

df = get_plays(choose_years, data)

tab1, tab2, tab3 = st.tabs(["Passing Props","Rushing Props","Receiving Props"])
col1, col2 = st.columns(2)

### Passing Props
passing_attempt = df.loc[df['pass']==1].groupby(['passer','game_id']).agg(pass_attempt=('pass_attempt','sum'),
                                                                           pass_touchdown=('pass_touchdown','sum'),
                                                                           complete_pass=('complete_pass','sum'),
                                                                           yards_gained=('yards_gained','sum'),
                                                                           longest_completion=('yards_gained','max')
                                                                           ).reset_index()
passing_attempts = passing_attempt.groupby('passer').agg(games=('game_id','nunique'), 
                                                        att_avg=('pass_attempt','mean'),
                                                        att_med=('pass_attempt','median'),
                                                        pass_td_avg=('pass_touchdown','mean'),
                                                        pass_td_med=('pass_touchdown','median'),
                                                        complete_pass_avg=('complete_pass','mean'),
                                                        complet_pass_med=('complete_pass','median'),
                                                        yards_gained_avg=('yards_gained','mean'),
                                                        yards_gained_med=('yards_gained','median'),
                                                        yards_gained_max=('longest_completion','max')
                                                        )
tab1.dataframe(passing_attempts)

passing_players = passing_attempts.reset_index()['passer']
choose_passer = tab1.selectbox("Choose your Passer", passing_players)
choose_stat = tab1.selectbox("Choose stat:", ['pass_attempt','pass_touchdown','complete_pass','yards_gained','longest_completion'])
choose_number = tab1.number_input("Choose the O/U number: ",0.0,500.0,25.0,0.5)
passing_player_stats = passing_attempt.loc[passing_attempt['passer']==choose_passer]
x1 = [passing_player_stats[choose_stat]]
gl1 = [choose_stat]
fig1 = ff.create_distplot(x1,group_labels=gl1, bin_size=1)
tab1.plotly_chart(fig1)
over_prob = passing_player_stats.loc[passing_player_stats[choose_stat]>choose_number][choose_stat].count()/passing_player_stats[choose_stat].count()
under_prob = passing_player_stats.loc[passing_player_stats[choose_stat]<choose_number].count()/passing_player_stats[choose_stat].count()
tab1.header(f'{over_prob*100.00:.2f}% {choose_passer} goes over {choose_stat}.')
tab1.write(passing_player_stats)

### Rushing Props
rushing_attempt = df.loc[df['rush']==1].groupby(['rusher_player_name','game_id']).agg(rush_attempt=('rush','sum'),
                                                                           rush_touchdown=('rush_touchdown','sum'),
                                                                           yards_gained=('yards_gained','sum'),
                                                                           longest_run=('yards_gained','max')
                                                                           ).reset_index()
rushing_attempts = rushing_attempt.groupby('rusher_player_name').agg(games=('game_id','nunique'), 
                                                        att_avg=('rush_attempt','mean'),
                                                        att_med=('rush_attempt','median'),
                                                        rush_td_avg=('rush_touchdown','mean'),
                                                        rush_td_med=('rush_touchdown','median'),
                                                        yards_gained_avg=('yards_gained','mean'),
                                                        yards_gained_med=('yards_gained','median'),
                                                        yards_gained_max=('longest_run','max')
                                                        )
tab2.dataframe(rushing_attempts)

rushing_players = rushing_attempts.reset_index()['rusher_player_name']
choose_rusher = tab2.selectbox("Choose your Rusher", rushing_players)
choose_stat_rush = tab2.selectbox("Choose rushing stat:", ['rush_attempt','rush_touchdown','yards_gained','longest_run'])
choose_number_rush = tab2.number_input("Choose the rushing O/U number: ",0.0,500.0,25.0,0.5)
rushing_player_stats = rushing_attempt.loc[rushing_attempt['rusher_player_name']==choose_rusher]
x2 = [rushing_player_stats[choose_stat_rush]]
gl2 = [choose_stat_rush]
fig2 = ff.create_distplot(x2,group_labels=gl2, bin_size=1)
tab2.plotly_chart(fig2)
over_prob_rush = rushing_player_stats.loc[rushing_player_stats[choose_stat_rush]>choose_number_rush][choose_stat_rush].count()/rushing_player_stats[choose_stat_rush].count()
under_prob_rush = rushing_player_stats.loc[rushing_player_stats[choose_stat_rush]<choose_number_rush].count()/rushing_player_stats[choose_stat_rush].count()
tab2.header(f'{over_prob_rush*100.00:.2f}% {choose_rusher} goes over {choose_stat_rush}.')
tab2.write(rushing_player_stats)

### Receiving Props
rec_attempt = df.loc[df['pass']==1].groupby(['receiver_player_name','game_id']).agg(targets=('pass_attempt','sum'),
                                                                            catches=('complete_pass','sum'),
                                                                           rec_touchdown=('touchdown','sum'),
                                                                           yards_gained=('yards_gained','sum'),
                                                                           longest_catch=('yards_gained','max')
                                                                           ).reset_index()
rec_attempts = rec_attempt.groupby('receiver_player_name').agg(games=('game_id','nunique'), 
                                                        target_avg=('targets','mean'),
                                                        target_med=('targets','median'),
                                                        rec_td_avg=('rec_touchdown','mean'),
                                                        rec_td_med=('rec_touchdown','median'),
                                                        yards_gained_avg=('yards_gained','mean'),
                                                        yards_gained_med=('yards_gained','median'),
                                                        yards_gained_max=('longest_catch','max')
                                                        )
tab3.dataframe(rec_attempts)

rec_players = rec_attempts.reset_index()['receiver_player_name']
choose_receiver = tab3.selectbox("Choose your Receiver", rec_players)
choose_stat_rec = tab3.selectbox("Choose receiving stat:", ['targets','catches','rec_touchdown','yards_gained','longest_catch'])
choose_number_rec = tab3.number_input("Choose the receiving O/U number: ",0.0,500.0,25.0,0.5)
receiving_player_stats = rec_attempt.loc[rec_attempt['receiver_player_name']==choose_receiver]
x3 = [receiving_player_stats[choose_stat_rec]]
gl3 = [choose_stat_rec]
fig3 = ff.create_distplot(x3,group_labels=gl3, bin_size=1)
tab3.plotly_chart(fig3)
over_prob_rec = receiving_player_stats.loc[receiving_player_stats[choose_stat_rec]>choose_number_rec][choose_stat_rec].count()/receiving_player_stats[choose_stat_rec].count()
under_prob_rec = receiving_player_stats.loc[receiving_player_stats[choose_stat_rec]<choose_number_rec].count()/receiving_player_stats[choose_stat_rec].count()
tab3.header(f'{over_prob_rec*100.00:.2f}% {choose_receiver} goes over {choose_stat_rec}.')
tab3.write(receiving_player_stats)
