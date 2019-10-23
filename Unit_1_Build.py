import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import re
import seaborn as sns

path = r'..\Unit_1_Build'
os.chdir(path)

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows',   100)
pd.set_option('display.width',      500)

# What I want:
#  - I want to gather death data on the US
#    - All states
#    - All possible years
#    - Sorted by year, state, county, age, cause of death
#  - Then I want to be able to see all the data in a clickable, sortable way
#  - All alive vs all dead, chunked groups of trauma vs medical, homicide vs suicide, etc.
#  - I also want it to be interactable
#  - Plot everythng along the US by state and county hallucinogens
#    - Heat maps
#    - Time slider, maybe allow a segment of time to view across?

# How to get there:
#  [-] Dataframe of the whole US
#      [X] California 1999 - 2014
#  [ ] Ask and answer a question
#      [ ] I know that medical deaths are far more common than those by crime,
#          cardiac arrest alone is 800k per year iirc while all firearm deaths
#          combined, even including suicides is barely 25k. Without suicides
#          it's a third of that. I want to visualize this
#  [ ] Make 3 different visualizations
#      [ ] Overall
#      [ ] Plot and Donut
#      [ ] California County Map
# [ ] Connect this project to github.io
#
# train_features.profile_report() # Need to look at this later

# ------------------------------ Data Cleaning ------------------------------ #
# Data pulled from the CDC website. Had to merge once for each year at minimum
# The data was very clean, though in working through the project I've had a few
# minor things to change still


df = pd.read_csv(r'dataframes\CDC Mortality Dataframe California 1999 - 2016.csv', low_memory = False)

df                              = df.drop(['Year Code'], axis = 1)

df                              = df.replace({'Population':                'Not Applicable'
                                             ,'Crude Rate':                'Not Applicable'
                                             ,'Crude Rate Standard Error': 'Not Applicable'}
                                             ,np.NaN)

df['Population']                = df['Population'].fillna(method = 'ffill', limit = 1).astype('int64')
df['Crude Rate']                = df['Crude Rate'].str.strip(' (Unreliable)').astype('float')
df['Crude Rate Standard Error'] = df['Crude Rate Standard Error'].astype('float')

df['Age Group'] = df['Age Group'].replace({'1-4 years':   '1 - 4 years'
                                          ,'5-9 years':   '5 - 9 years'
                                          ,'10-14 years': '10 - 14 years'
                                          ,'15-19 years': '15 - 19 years'
                                          ,'20-24 years': '20 - 24 years'
                                          ,'25-34 years': '25 - 34 years'
                                          ,'35-44 years': '35 - 44 years'
                                          ,'45-54 years': '45 - 54 years'
                                          ,'55-64 years': '55 - 64 years'
                                          ,'65-74 years': '65 - 74 years'
                                          ,'75-84 years': '75 - 84 years'
                                          })

# df.to_csv(r'dataframes\CDC Mortality Dataframe California 1999 - 2016 CLEANED.csv')

# ------------------------------ Data Cleaning ------------------------------ #




# ----------------------------------- Work ----------------------------------- #
# I need a way to filter based on arbitrary stats, e.g. County, Age Group, etc.

# The default values for ALL RESULTS
years        = range(1999, 2017, 1)
states       = range(   1,   51, 1)
counties     = range(6001, 6116, 1)
age_groups   = ['< 1 year'
               ,'1 - 4 years'
               ,'5 - 9 years'
               ,'10 - 14 years'
               ,'15 - 19 years'
               ,'20 - 24 years'
               ,'25 - 34 years'
               ,'35 - 44 years'
               ,'45 - 54 years'
               ,'55 - 64 years'
               ,'65 - 74 years'
               ,'75 - 84 years'
               ,'85+ years'
               ,'Not Stated'
               ]
causes       = df['Cause of death'].unique().tolist()
causes_codes = df['Cause of death Code'].unique().tolist()

default      = [years
               ,states
               ,counties
               ,age_groups
               ,causes
               ,causes_codes]



# Dictionaries that allow me to replace the compact codes with their values
cause_code_dict  = dict(df[['Cause of death Code', 'Cause of death']].values.tolist())
county_code_dict = dict(df[['County Code', 'County']].values.tolist())


# This prevents errors in the other functions for not passing a list
# Just makes it simpler for me
def error_prev(some_list):

    # Converts the input into lists for use, if it's not already a list
    iterator = -1
    for choice in some_list:
        iterator += 1

        if type(choice) != list and type(choice) != range:
            some_list[iterator] = [some_list[iterator]]
    # If there's blank values, replaces them with the default
    iterator = -1
    for choice in some_list:
        iterator += 1
        if choice[0] == '':
            some_list[iterator] = default[iterator]

    return some_list




# This function is specifically for making a graph that projects
def df_graphing(choices):

    choices            = error_prev(choices)
    death_sums_by_year = []

    for year in choices[0]:
        choice = [year
                 ,choices[1]
                 ,choices[2]
                 ,choices[3]
                 ,choices[4]
                 ,choices[5]
                 ]
        death_sums_by_year.append(df_filter(choice)['Deaths'].sum())

    plotting_df = np.array([choices[0], death_sums_by_year]).T
    plotting_df = pd.DataFrame(plotting_df
                              ,columns = ['Year', 'Deaths'])

    return plotting_df




def df_filter(choices):
    choices = error_prev(choices)

    # Any choices must be put in lists, else .isin() can't function
    filter = [['Year',                choices[0]]
             ,['State Code',          choices[1]]
             ,['County Code',         choices[2]]
             ,['Age Group',           choices[3]]
             ,['Cause of death',      choices[4]]
             ,['Cause of death Code', choices[5]]
             ]

    # From right to left
    # This checks our specified filters against what's in the dataframe, then
    # for each part of the filter, top to bottom, it weeds out the False values.
    # Any value which includes a list of all possible values will pass through
    # that entire chunk of the dataframe.

    # Can't think of a less chunky version of this. It needs to save over prior
    # data to make the dataframe correctly.
    filtered_df = df
    filtered_df = filtered_df[filtered_df[filter[0][0]].isin(filter[0][1])]
    filtered_df = filtered_df[filtered_df[filter[1][0]].isin(filter[1][1])]
    filtered_df = filtered_df[filtered_df[filter[2][0]].isin(filter[2][1])]
    filtered_df = filtered_df[filtered_df[filter[3][0]].isin(filter[3][1])]
    filtered_df = filtered_df[filtered_df[filter[4][0]].isin(filter[4][1])]
    filtered_df = filtered_df[filtered_df[filter[5][0]].isin(filter[5][1])]

    return filtered_df




# ----------------------------------- Work ----------------------------------- #





# ---------------------------------- Output ---------------------------------- #

choice = [1999
         ,6
         ,6073
         ,'85+ years'
         ,''
         ,''
         ]


# ---------------------------------- Output ---------------------------------- #

# ---------- Graph ---------- #
# For each year, add up the deaths by age group

plotting_df = df_graphing(choice)


plt.plot(plotting_df['Year'], plotting_df['Deaths'])
plt.xticks(rotation = 45)
plt.xlim(choice[0][0], choice[0][-1])


if len(choice[0]) == 1:
    plt.title('All deaths for ages ' +
              str(choice[3][0]) +
              ' for ' +
              str(choice[0][0])
             )
else:
    plt.title('All deaths for ages ' +
              choice[3][0] +
              ' from ' +
              str(choice[0][0]) +
              ' to ' +
              str(choice[0][-1])
             )


plt.show()
# ---------- Graph ---------- #

# ---------- Donut Plot ---------- #

filtered_df = df_filter(choice)

# Total dead of a given age group vs total population of a given age group
# This gives us the total left living, for a given age group
total_pop = filtered_df['Population'].iloc[0]
alive     = filtered_df['Population'].iloc[0] - filtered_df['Deaths'].sum()
dead      = filtered_df['Deaths'].sum()



# This is the outer ring of the donut chart showing the living vs the dead for
# a given subset of the dataframe
group_names    = ['Alive', 'Deceased']
group_size     = [alive, dead]


# This is the inner ring showing the 4 most common causes with a misc 5th cause
# that includes all the others that were missed. Then it makes the list of the
# 5 groups going into the donut chart
subgroup_names = filtered_df.sort_values(by = ['Deaths'], ascending = False)[:5]
subgroup_size  = filtered_df.sort_values(by = ['Deaths'], ascending = False)[:5]
subgroup_names = subgroup_names['Cause of death Code'].tolist()
subgroup_size  = subgroup_size['Deaths'].tolist()



# Very messy complicated thing that literally only adds in a consolidated misc
# category if we go over the top 5 causes of death
if len(filtered_df['Deaths'].sort_values(ascending = False)[5:]) != 0:
    subgroup_names.append(str(len(filtered_df['Deaths'].sort_values(ascending = False)[5:])) + ' others\ncombined')
    subgroup_size.append(filtered_df['Deaths'].sort_values(ascending = False)[5:].sum())



# Create colors
a, d = [plt.cm.Greens, plt.cm.Reds]


# First Ring (outside)
fig, ax = plt.subplots()

ax.axis('equal')

mpl.rcParams['font.size'] = 9.0

pie, text, perc = ax.pie(group_size
                        ,radius        = 1.5
                        ,startangle    = 320
                        ,labels        = group_names
                        ,labeldistance = 1.1
                        ,autopct       = '%1.2f%%'
                        ,pctdistance   = 0.87
                        ,colors        = [a(0.6)
                                         ,d(0.6)
                                         ]
                        )
text[0].set_fontsize(15)
text[1].set_fontsize(15)

perc[0].set_fontsize(12)
perc[1].set_fontsize(12)

plt.setp(pie
        ,width = 0.4
        ,edgecolor = 'white')


# Second Ring (Inside)
pie2, text2, perc2 = ax.pie(subgroup_size
                           ,radius        = 1.5 - 0.4
                           ,labels        = subgroup_names
                           ,rotatelabels  = True
                           ,counterclock  = False
                           ,labeldistance = 0.8
                           ,autopct       = '%1d%%'
                           ,pctdistance   = 0.45
                           ,colors        = [d(0.9)
                                            ,d(0.8)
                                            ,d(0.7)
                                            ,d(0.6)
                                            ,d(0.5)
                                            ,d(0.4)
                                            ]
                           )
plt.setp(pie2
        ,width = 0.4
        ,edgecolor = 'white'
        )

plt.setp(text2
        ,rotation_mode = "anchor"
        ,ha            = "center"
        ,va            = "center")

for txt in text2:
    rotation = tx.get_rotation()
    txt.set_rotation(rotation + 90 + (1 - rotation // 180) * 180)

for number in range(0, len(subgroup_size), 1):
    text2[number].set_fontsize(13)
    perc2[number].set_fontsize(10)


plt.margins(0, 0)


if len(choice[0]) == 1:
    plt.title(str(county_code_dict[choice[2][0]]) +
              ' ' +
              str(choice[0][0]) +
              '\n' +
              'Ages ' +
              choice[3][0]
             ,fontsize = 18
             ,y = 1.15)
else:
    plt.title(str(county_code_dict[choice[2][0]]) +
              ' ' +
              str(choice[0][0]) +
              ' - ' +
              str(choice[0][-1]) +
              '\n' +
              'Ages ' +
              choice[3][0]
             ,fontsize = 18
             ,y = 1.15)


legend_list = []

for thing in subgroup_names:
    if re.match('[0-9]+ others\ncombined', thing):
        continue
    legend_list.append(fill(str(thing) + ': ' + str(cause_code_dict[thing])
                           ,width = 50))

plt.legend(pie2
          ,legend_list
          ,bbox_to_anchor = (0.9, 1))

plt.show()

# ---------- Donut Plot ---------- #


# ---------- Seaborn Plot ---------- #

choice      =          [''
                       ,6
                       ,''
                       ,''
                       ,''
                       ]

filtered_df = df_filter(choice)

target   = filtered_df['Deaths']
features = filtered_df.drop(['State'
                            ,'State Code'
                            ,'County Code'
                            ,'Age Group Code'
                            ,'Population'
                            ,'Cause of death Code'
                            ,'Crude Rate'
                            ,'Crude Rate Standard Error'], axis = 1)

# plt.figure(figsize = (20, 10))
sns.pairplot(features)
# plt.xticks(rotation = 90)
# plt.xlim(-1, 53)
# plt.ylim(0, 3500)

plt.show()

# ---------- Seaborn Plot ---------- #


# ---------- California County Map Plot ---------- #
# import geopandas as geo
#
# world = geo.read_file(geo.datasets.get_path('naturalearth_lowres'))
# cities = geo.read_file(geo.datasets.get_path('naturalearth_cities'))
# world.head()
# world.plot();
#
# world = world[(world.pop_est>0) & (world.name!="Antarctica")]
#
# world['gdp_per_cap'] = world.gdp_md_est / world.pop_est
#
# world.plot(column='gdp_per_cap');


# ---------- California County Map Plot ---------- #

# ---------------------------------- Output ---------------------------------- #

# ---------------------------------- Output ---------------------------------- #
