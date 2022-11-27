import streamlit as st
import numpy as np
import pandas as pd
import os
import calendar # used to convert numbers between 1 and 12 to month names
import matplotlib.pyplot as plt # creating subplots and formating figures

import warnings        
warnings.filterwarnings("ignore") # ignores warnings


st.set_page_config(page_title="RFM Analysis", page_icon="📈")

st.markdown("""# RFM Analysis
RFM is a method used for analyzing customer value. 
It is commonly used in database marketing and direct marketing and 
has received particular attention in retail and professional services industries.
""")

st.sidebar.header("RFM Analysis")
st.sidebar.markdown("""
    ### Based on rfm column we can segment customers based on a simple rule:

- Best → RFM = 144

- Almost Lost → RFM = 344

- Lost Big Spenders → RFM = 444

- Lost Cheap → RFM = 441

- Loyal → RFM = ?4?

- Big Spenders → RFM = ??4

- Normal → RFM dosen't belong to any top groups

Note 1: ? could be 1 or 2 or 3.

Note 2: If a rfm belongs to more than one group, it belongs the group with lowest order.

""")

data = pd.read_csv("C:/Users/Suparno Victus/ADT_Project/pages/Online_Retail.csv")

data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])

data['Total'] = data['Quantity'] * data['UnitPrice']

monetary = data.groupby('CustomerID')['Total'].sum()
monetary = pd.DataFrame(monetary).reset_index()
monetary.head()

#Frequency means the number of inovices for each customer. 
#We should get the number of unique inovice for each customer because each inovice has repeated many times for each stocks of itself.

freq = data.drop_duplicates(subset=['InvoiceNo']).groupby('CustomerID')['InvoiceNo'].count()
freq = pd.DataFrame(freq).reset_index()
freq.head()

def recency_cerrection(recency):
    ans = str(recency).split(' ')[0]
    return(int(ans))

data['Date'] = pd.to_datetime(data['InvoiceDate'])

today = data['Date'].max()

#Recency means the number of days after last payment. I use rank method to mark the most recent payment of each customer as 1

data['rank'] = data.sort_values(['CustomerID','Date']).groupby(['CustomerID'])['Date'].rank(method='min').astype(int)

recency = data[data['rank'] == 1]
recency['recency'] = pd.to_datetime('2011-12-10') - recency['Date']

recency['recency'] = recency['recency'].apply(recency_cerrection)

recency = recency[['CustomerID','recency']]
recency = recency.drop_duplicates()
recency.head()

#merging RFM
final_data = freq.merge(monetary, on='CustomerID').merge(recency, on='CustomerID')
final_data.columns = ['CustomerId', 'freq', 'monetary', 'recency']
final_data.head()

def get_group(Q1, Q2, Q3, value):
    if value <= Q1:
        return '1'
    elif Q1 < value <= Q2:
        return '2'
    elif Q2 < value <= Q3:
        return '3'
    elif Q3 < value:
        return '4'

#Compute  Q1,Q2,Q3  for frequency, recency and monetary
freq_Q1, freq_Q2, freq_Q3 = final_data['freq'].quantile([0.25,0.5,0.75])
rece_Q1, rece_Q2, rece_Q3 = final_data['recency'].quantile([0.25,0.5,0.75])
mone_Q1, mone_Q2, mone_Q3 = final_data['monetary'].quantile([0.25,0.5,0.75])

#Get group of each freuency with the help of get_group() and similarly with others
freq_group = []

for i in range(len(final_data)):
    freq = final_data.iloc[i]['freq']
    freq_group.append(get_group(freq_Q1, freq_Q2, freq_Q3, freq)) 

final_data['freq_group'] = freq_group

monetary_group = []

for i in range(len(final_data)):
    monetary = final_data.iloc[i]['monetary']
    monetary_group.append(get_group(mone_Q1, mone_Q2, mone_Q3, monetary)) 

final_data['monetary_group'] = monetary_group

recency_group = []

for i in range(len(final_data)):
    recency = final_data.iloc[i]['recency']
    recency_group.append(get_group(rece_Q1, rece_Q2, rece_Q3, recency)) 

final_data['recency_group'] = recency_group

final_data['rfm'] = final_data['recency_group'] + final_data['freq_group'] + final_data['monetary_group']

def get_group(rfm):
    if rfm == '144':
        return 'Best'
    elif rfm == '344':
        return 'Almost Lost'
    elif rfm == '444':
        return 'Lost Big Spenders'
    elif rfm == '441':
        return 'Lost Cheap'
    elif rfm[1] == '4':
        return 'Loyal'
    elif rfm[2] == '4':
        return 'Big Spenders'
    else:
        return 'Normal'

final_data['Segment'] = final_data['rfm'].apply(get_group)

data_customer_segments = final_data[['CustomerId', 'Segment']]


selectedOption = st.selectbox("Select a Customer ID", data_customer_segments['CustomerId'].head(10).tolist())

segment_group = data_customer_segments.groupby('Segment').count()
segment_group = segment_group.reset_index()
segment_group.columns = ['Segment', 'Count']
segment_group.head()

def findCustomerSegmentForID(): 
    df_row = final_data[final_data['CustomerId'] == selectedOption]
    numberOfPurchasesMade = df_row.iloc[0]['freq']
    avgPurchase = df_row.iloc[0]['monetary']
    duration = df_row.iloc[0]['recency']
    segment = df_row.iloc[0]['Segment']

    col1, col2, col3 = st.columns(3)
    col1.metric("Customer ID", selectedOption)
    col2.metric("Segment", segment)
    col3.metric("Total Purchases", numberOfPurchasesMade)
    col1.metric("Days since last purchase", duration)
    col2.metric("Average Purchase Amount", avgPurchase)


findCustomerSegmentForID()

plt.style.use('dark_background')

fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
#plt.bar(segment_group['Segment'], segment_group['Count'], color='orangered', alpha=0.8);
plt.title("Customer Segments")
ax.bar(segment_group['Segment'], segment_group['Count'])

st.pyplot(fig)

