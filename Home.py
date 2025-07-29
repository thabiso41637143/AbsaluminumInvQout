import streamlit as st

#page = st.sidebar.selectbox("Select a page", ["Home", "Qoute and Invoice", "Staff Members", "View Invoice and Qoute"])
abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

st.image("Images/Heading_Letter_head.png")

st.title("📄 Absaluminum Quotation App")
st.markdown("Welcome to the official quotation generator for **Absaluminum Projects**.")

st.divider()

st.header("Client Details")
st.text_input("Client Name")
st.text_input("Contact Number")

st.divider()

st.header("Quotation Information")
st.number_input("Total Price", min_value=0.0)
st.date_input("Quotation Date")