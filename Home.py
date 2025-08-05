import streamlit as st

#page = st.sidebar.selectbox("Select a page", ["Home", "Qoute and Invoice", "Staff Members", "View Invoice and Qoute"])
abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

st.image("Images/Heading_Letter_head.png")

st.title("Absaluminum (PTY) LTD".upper())
st.markdown("Welcome to the official quotation and invoice generator for **Absaluminum Projects**.")

st.divider()

st.header("Invoice Summary")


st.divider()

st.header("Quotation Summary")

st.divider()

st.header("Staff Summary")
