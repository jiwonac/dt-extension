import pandas as pd
from dt import *
import pickle

df = pd.read_csv('data/flights.csv')
split_df = df.groupby(['MKT_UNIQUE_CARRIER'])
carriers = set(df['MKT_UNIQUE_CARRIER'])
states = set(df['ORIGIN_STATE_NM'])
states_dict = {
 'Alabama': 0,
 'AL': 0,
 'Alaska': 1,
 'AK': 1,
 'Arizona': 2,
 'AZ': 2,
 'Arkansas': 3,
 'AR': 3,
 'California': 4,
 'CA': 4,
 'Colorado': 5,
 'CO': 5,
 'Connecticut': 6,
 'CT': 6,
 'Florida': 7,
 'FL': 7,
 'Georgia': 8,
 'GA': 8,
 'Hawaii': 9,
 'HI': 9,
 'Idaho': 10,
 'ID': 10,
 'Illinois': 11,
 'IL': 11,
 'Indiana': 12,
 'IN': 12,
 'Iowa': 13,
 'IA': 13,
 'Kansas': 14,
 'KS': 14,
 'Kentucky': 15,
 'KY': 15,
 'Louisiana': 16,
 'LA': 16,
 'Maine': 17,
 'ME': 17,
 'Maryland': 18,
 'MD': 18,
 'Massachusetts': 19,
 'MA': 19,
 'Michigan': 20,
 'MI': 20,
 'Minnesota': 21,
 'MN': 21,
 'Mississippi': 22,
 'MS': 22,
 'Missouri': 23,
 'MO': 23,
 'Montana': 24,
 'MT': 24,
 'Nebraska': 25,
 'NE': 25,
 'Nevada': 26,
 'NV': 26,
 'New Hampshire': 27,
 'NH': 27,
 'New Jersey': 28,
 'NJ': 28,
 'New Mexico': 29,
 'NM': 29,
 'New York': 30,
 'NY': 30,
 'North Carolina': 31,
 'NC': 31,
 'North Dakota': 32,
 'ND': 32,
 'Oklahoma': 33,
 'OK': 33,
 'Oregon': 34,
 'OR': 34,
 'Ohio': 35,
 'OH': 35,
 'Pennsylvania': 36,
 'PA': 36,
 'Puerto Rico': 37,
 'PR': 37,
 'Rhode Island': 38,
 'RI': 38,
 'South Carolina': 39,
 'SC': 39,
 'South Dakota': 40,
 'SD': 40,
 'Tennessee': 41,
 'TN': 41,
 'Texas': 42,
 'TX': 42,
 'Utah': 43,
 'UT': 43,
 'Vermont': 44,
 'VT': 44,
 'Virginia': 45,
 'VA': 45,
 'Washington': 46,
 'WA': 46,
 'West Virginia': 47,
 'WV': 47,
 'Wisconsin': 48,
 'WI': 48,
 'Wyoming': 49,
 'WY': 49,
 'U.S. Pacific Trust Territories and Possessions': 50,
 'TT': 50,
 'U.S. Virgin Islands': 50,
 'VI': 50,
}

def create_sources():
    sources = []
    for carrier in carriers:
        source = RealSource(51, 1.0)
        carrier_df = split_df.get_group(carrier)
        for index, row in carrier_df.iterrows():
            group = states_dict[row['ORIGIN_STATE_NM']]
            data = index
            point = DataPoint(group, data)
            source.add_point(point)
            print(str(index), end="\r")
        sources.append(source)
        print(str(carrier), end="\r")
    return sources

sources = create_sources()

with open("data/flights_sources.pickle", "wb") as f:
    pickle.dump(sources, f)