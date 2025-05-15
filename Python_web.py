#!/usr/bin/env python
# coding: utf-8

# In[4]:


import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Sample data
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]

# --- Option 1: Using Matplotlib ---
st.subheader("Bar Chart using Matplotlib")
fig, ax = plt.subplots()
ax.bar(categories, values, color='skyblue')
ax.set_title("Sample Bar Chart")
ax.set_xlabel("Categories")
ax.set_ylabel("Values")
st.pyplot(fig)

# --- Option 2: Using Streamlit's Built-in Chart ---
st.subheader("Bar Chart using Streamlit's Built-in Chart")
data = pd.DataFrame({
    'Categories': categories,
    'Values': values
})
st.bar_chart(data.set_index('Categories'))


# In[ ]:




