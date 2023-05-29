import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.express.colors import sample_colorscale
from datetime import datetime, timedelta

#🛑 Code to set the Dashboard format to wide (the content will fill the entire width of the page instead of having wide margins)
def do_stuff_on_page_load():
    st.set_page_config(layout="wide")
do_stuff_on_page_load()

#Set Header
#🛑 Code to set the header
st.header('Lego Sets Explorer', anchor=None)

#Set Sidebar Elements
#🛑 Code to set the Sidebar
with st.sidebar:
    st.header('Filters', anchor=None)
    values = st.slider(
        'Select the Start and End Years',
        1950, 2017, (1950, 2017))
    min_year = values[0]
    max_year = values[1]
    st.write('Date Range: '+str(values[0])+'-01-01 to '+str(values[1])+'-01-01')

#🛑 Code to import the dataset
df = pd.read_csv('https://miles-become-a-data-scientist.s3.us-east-2.amazonaws.com/J3/M2/df_combined_lego.csv')

#🛑 Code to persist the DataFrame between pages of the same Dashboard. Without this, any other page would need to re import the DataFrame and save it to df again.
st.session_state['df'] = df 

#Apply the minimum and maximum year filter of the side panel. Store in a filtered dataframe
df_filtered = df[(df.year >= values[0]) & (df.year <= values[1])]

#Cards with Number of New Master Themes, Themes, Sets and Parts
#👇 Create 4 columns here using the apropriate Streamlit object. Save them as col1, col2, col3 and col4. 
#👇 Reference material can be found here: https://docs.streamlit.io/library/api-reference/layout/st.columns
col1, col2, col3, col4 = st.columns(4)
metric_new_master_themes = df.groupby('parent_theme_name').year.min().reset_index()
metric_new_master_themes = metric_new_master_themes[(metric_new_master_themes.year >= min_year) & (metric_new_master_themes.year<= max_year)]
metric_new_master_themes = metric_new_master_themes.parent_theme_name.nunique()
#👇 Use col1.metric(title,value) to produce a column with the metric_new_master_themes metric. Set the title to "New Master Themes"
col1.metric('New Masters Themes',metric_new_master_themes)

#New Themes (considering first year of appearance)
metric_new_themes = df.groupby('theme_name').year.min().reset_index()
metric_new_themes = metric_new_themes[(metric_new_themes.year >= min_year) & (metric_new_themes.year<= max_year)]
metric_new_themes = metric_new_themes.theme_name.nunique()
#👇 Create a metric with the metric_new_themes and set it to col2. Give it the title "New Themes". The procedure is similar to the one you performed before
col2.metric('New Themes',metric_new_themes)

#New Sets (considering first year of appearance)
metric_new_sets = df.groupby('set_name').year.min().reset_index()
metric_new_sets = metric_new_sets[(metric_new_sets.year >= min_year) & (metric_new_sets.year<= max_year)]
metric_new_sets = metric_new_sets.set_name.nunique()
#👇 Create a metric with the metric_new_sets and set it to col3. Give it the title "New Sets". The procedure is similar to the one you performed before
col3.metric('New Sets',metric_new_sets)

#New Pars of Sets (considering first year of appearance)
metric_new_sets_parts = df.groupby(['set_name','num_parts']).year.min().reset_index()
metric_new_sets_parts = metric_new_sets_parts[(metric_new_sets_parts.year >= min_year) & (metric_new_sets_parts.year<= max_year)]
metric_new_sets_parts = int(metric_new_sets_parts.num_parts.sum())
#👇 Create a metric with the metric_new_sets_parts and set it to col4. Give it the title "Parts of New Sets". The procedure is similar to the one you performed before
col4.metric('New SEts Parts',metric_new_sets_parts)

#Get Top N Themes
#👇 Paste the code to create a slider input widget with possible values between 1 and 20. Set default value to 10 and save the output to a new variable called filt_n_themes
#👇 You can find the documentation here - https://docs.streamlit.io/library/api-reference/widgets/st.slider
filt_n_themes =st.slider('Top 10 Master Thems', min_value = 1, max_value=20, value=10)

#👇 Create an expander container widget with title "New Sets of the Top Master Themes".
#👇 You can find the documentation here - https://docs.streamlit.io/library/api-reference/layout/st.expander.
with st.expander("New Sets of the Top {filt_n_themes} Master Themes", expanded=True):
    #Prepare sample of colors
    colors_scaled = ["#1F78C8","#ff0000","#33a02c","#6A33C2","#ff7f00","#565656",
        "#FFD700","#a6cee3","#FB6496","#b2df8a","#CAB2D6","#FDBF6F",
        "#999999","#EEE685","#C8308C","#FF83FA","#C814FA","#0000FF",
        "#36648B","#00E2E5","#00FF00","#778B00","#BEBE00","#8B3B00",
        "#A52A3C"]

    #👇 Paste the code created in activity 1.2 to produce a DataFrame with the top N Master Themes as measured by number of new sets.
    sets_theme_parts = df_filtered.groupby('parent_theme_name')['set_name'].nunique().reset_index()
    sets_theme_parts = sets_theme_parts.rename(columns={'set_name': 'nbr_sets'})
    sets_per_parent_theme = sets_theme_parts
    sets_per_parent_theme = sets_per_parent_theme.sort_values(by='nbr_sets', ascending=False).reset_index()
    sets_per_parent_theme = sets_per_parent_theme[:filt_n_themes]
    nbr_sets_remained = sets_theme_parts.sort_values(by='nbr_sets', ascending=False).reset_index()[filt_n_themes:].nbr_sets.sum()
    dict_colors = dict(zip(sets_per_parent_theme.parent_theme_name.sort_values().tolist(),colors_scaled)) #This line is supplied for you
    sets_per_parent_theme ['colors'] = sets_per_parent_theme.parent_theme_name.map(dict_colors)
    df_single_row = pd.DataFrame({'parent_theme_name':'Remainder',
            'nbr_sets':nbr_sets_remained,
            'colors':'#808080'},
            index=[filt_n_themes])
    sets_per_parent_theme = pd.concat((sets_per_parent_theme , df_single_row))

    #👇 Paste the code created in activity 1.2 to create the visualization of the sets_per_parent_theme DataFrame
    #👇 Important! If you had previously used fig_parent_theme.show() at the end to display the plotly graph, you now don't want to do so.
    fig_parent_theme = px.bar(
        sets_per_parent_theme, 
        x='nbr_sets', 
        y='parent_theme_name', 
        color='parent_theme_name',
        color_discrete_sequence=sets_per_parent_theme.colors,
        title= f'Parent Theme Name (TOP {filt_n_themes})'
    )

    fig_parent_theme.update_layout(
        xaxis_title='Number of Sets',
        yaxis_title = "",
    )
    #👇 Use a plotly widget from Streamlit to visualize the fig_parent_theme plot. Pass the parameter use_container_width =True to ensure the visualization expands to the container width.
    #👇 You can find the documentation here - https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart
    st.plotly_chart(fig_parent_theme, use_container_width=True)

#👇 Create an expander container widget with title "New Sets of the Top Master Themes"
with st.expander('Number of New Sets TOP {filt_n_themes} MASTER TEAMS', expanded= True):
    #👇 Paste the code created in activity 1.3 to produce a DataFrame with the number of new Sets per Year by Master Theme.
    sets_master_themes_per_first_year = df_filtered[['parent_theme_name', 'set_name', 'year']].groupby(['parent_theme_name' , 'set_name']).min('year').reset_index()
    sets_per_year_master_theme = sets_master_themes_per_first_year.groupby(['parent_theme_name' , 'year']).nunique('set_name').reset_index()
    top_10_parent_themes = sets_per_parent_theme.head(10)['parent_theme_name'].tolist()
    sets_per_year_master_theme_top = sets_per_year_master_theme[sets_per_year_master_theme['parent_theme_name'].isin(top_10_parent_themes)].sort_values('parent_theme_name')
    sets_per_year_master_theme_top['colors'] = sets_per_year_master_theme_top['parent_theme_name'].map(dict_colors)
    sets_per_year_master_theme_remainder = sets_per_year_master_theme[~sets_per_year_master_theme['parent_theme_name'].isin(top_10_parent_themes)].copy()
    sets_per_year_master_theme_remainder = sets_per_year_master_theme_remainder.groupby('year').sum('set_name').reset_index()
    sets_per_year_master_theme_remainder['parent_theme_name'] = 'Remainder'
    sets_per_year_master_theme_remainder['colors'] = '#808080'
    sets_per_year_master_theme = pd.concat([sets_per_year_master_theme_top, sets_per_year_master_theme_remainder], ignore_index=True)
    #👇 Paste the code created in activity 1.3 to create the visualization of the sets_per_year_master_theme DataFrame
    fig_sets_per_master = px.bar(sets_per_year_master_theme, 
            x="year", 
            y="set_name", 
            color='parent_theme_name',
            title=f'New Sets per Year for Top {filt_n_themes} Parent Themes',
            color_discrete_sequence=colors_scaled[:filt_n_themes]+['#808080'])
    fig_sets_per_master.update_layout(xaxis_title='Years', 
                yaxis_title='Number of Sets')
    
    #👇 Use a plotly widget from Streamlit to visualize the fig_sets_per_master plot. Pass the parameter use_container_width =True to ensure the visualization expands to the container width.
    st.plotly_chart(fig_sets_per_master, use_container_width=True)
#Get Largest Lego Set per Year
#👇 Create an expander container widget with title "Largest Lego Set per Year".
with st.expander('Get Largest Lego Set per Year', expanded= True):
    #👇 Paste the code created in activity 1.4 to produce a DataFrame with the largest Set per Year and with Master Theme information.
    df_sets_to_theme = df_filtered [['year','parent_theme_name','theme_name', 'set_name','num_parts']].drop_duplicates()
    df_sets_to_theme['theme_set']= df_sets_to_theme['theme_name'] + ' - ' + df_sets_to_theme['set_name']
    df_sets_to_theme_group = df_sets_to_theme.groupby(['year', 'parent_theme_name', 'theme_set'])['num_parts'].sum().reset_index()
    df_sets_to_theme_group.sort_values(by='num_parts' , ascending=False)
    df_sets_to_theme_group['rank'] = df_sets_to_theme_group.groupby('year')['num_parts'].rank(ascending=False)
    largest_set_year = df_sets_to_theme_group[df_sets_to_theme_group['rank'] == 1]

    #👇 Paste the code created in activity 1.4 to create the visualization of the largest_set_year DataFrame
    fig = px.bar(largest_set_year, x='year', y='num_parts', color='parent_theme_name', color_discrete_sequence = sets_per_parent_theme.colors)

    #👇 Use a plotly widget from Streamlit to visualize the fig_largest_set_year plot. Pass the parameter use_container_width =True to ensure the visualization expands to the container width.
    st.plotly_chart(fig, use_container_width=True)
#Free table explorer
#👇 Create an expander container widget with title "Free Table Explorer".
with st.expander('Free table explorer', expanded= True):
    #👇 Paste the code created in activity 1.5 to produce a DataFrame with details to year, parent_theme_name, theme_name, set_name and num_parts.
    df_table = df_filtered[['year', 'parent_theme_name', 'theme_name', 'set_name', 'num_parts']].drop_duplicates()
    #👇 Use a plotly widget from Streamlit to output an interactive table with df_table. Pass the parameter use_container_width =True to ensure the visualization expands to the container width.
    #👇 You can find the documentation here - https://docs.streamlit.io/library/api-reference/data/st.dataframe
    st.dataframe(df_table)
