import streamlit as st
import os
import numpy as np
import pandas as pd

st.set_page_config(page_title="Recommendations", page_icon="📈")

st.markdown("# E-Commerce Recommendation System")
st.sidebar.header("Recommendation System")

df = pd.read_csv("C:/Users/Suparno Victus/ADT_Project/pages/Online_Retail.csv")


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)

# Read dataframe from csv 
#st.write(df.head())

def check_df(dataframe, head=5, tail=5, quan=False):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(head))
    print("##################### Tail #####################")
    print(dataframe.tail(tail))
    print("##################### Sum of Missing #####################")
    print(dataframe.isnull().sum())
    print("##################### Percantage of Missing #####################")
    print(100 * dataframe.isnull().sum() / len(dataframe))

    if quan:
        print("##################### Quantiles #####################")
        print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

#Print out our data frame information
#check_df(df, quan=True)

df_uk= df[df["Country"]=="Germany"]
df_uk.head()

selectedOption = st.selectbox("Select the product purchased", df_uk.head(5)['StockCode'].tolist())
productName = df_uk[df_uk['StockCode'] == selectedOption].head(1).iloc[0]['Description']
st.write(productName)
rec_count = st.selectbox("Select the number of recommendations you would like", (1,2,3,4,5))

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True) #I dropped the missing values 
    dataframe = dataframe[~dataframe["InvoiceNo"].str.contains("C", na=False)] #I dropped the cancelled invoices 
    dataframe = dataframe[dataframe["Quantity"] > 0] # I dropped the observations of quantity variable that less than 0 
    dataframe = dataframe[dataframe["UnitPrice"] > 0] #I dropped the observations of price variable that less than 0 
    replace_with_thresholds(dataframe, "Quantity") #Outlier Analyses
    replace_with_thresholds(dataframe, "UnitPrice") #Outlier Analyses
    return dataframe

df_uk = retail_data_prep(df_uk)
#st.write(df_uk.head())

def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(['InvoiceNo', "StockCode"])['Quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)


inv_pro_df = create_invoice_product_df(df_uk, id=True)
#st.write(inv_pro_df.head())

from mlxtend.frequent_patterns import apriori, association_rules
frequent_itemsets = apriori(inv_pro_df, min_support=0.01, use_colnames=True)
frequent_itemsets.head()

frequent_itemsets.sort_values("support", ascending=False).head()

rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
#st.write(rules.head())

rules.sort_values("support", ascending=False).head()

rules.sort_values("lift", ascending=False).head()

def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list = []

    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))

    recommendation_list = list({item for item_list in recommendation_list for item in item_list})

    return recommendation_list[:rec_count]

def findProductNames(recommendation_ids):
    names = []
    st.header("Results")
    for item in recommendation_ids:
        df_row = df_uk[df_uk['StockCode'] == item].head(1)
        names.append(item +" - "+ df_row.iloc[0]['Description'])
        st.metric(label=item, value=df_row.iloc[0]['Description'])
    if(len(names)==0):
        st.write("No results found. Select a different product ID")

recommendations_ids = arl_recommender(rules, selectedOption ,rec_count)
findProductNames(recommendations_ids)
#st.write(recommendations_ids)