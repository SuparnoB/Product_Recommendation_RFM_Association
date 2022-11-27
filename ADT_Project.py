import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

st.title('RFM Analysis and Recommnendation System')

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Product recommendations during online shopping help increase average order value, 
    click-through and conversions from email by intelligently predicting what your customers 
    are likely to buy next. With the help of big data and data mining, this project focuses
     on building an online product recommendation engine which predicts products a customer 
     is most likely to buy based on the customer’s most recent purchase. In addtion, this project 
     performs customer market segmentation based on customer purchase history.

    **👈 Select a page from the sidebar** to see our app's usecases.
    
    #### Resources Used
    - [UCI Dataset](https://archive.ics.uci.edu/ml/datasets/online+retail) 
    - [streamlit.io](https://streamlit.io)

    #### Authors
    - [Kevin Jacob](https://github.com/kevinPJdev)
    - [Suparno Bhatta](https://www.linkedin.com/in/suparnobhatta/)
    - [Harmanjot Singh Suri](https://www.linkedin.com/in/harmanjot-s-7689a7128/)
"""
)