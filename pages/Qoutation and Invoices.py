import streamlit as st
from Model import InvQouteUI

abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

def gen_qoutation():
    st.title("Generate new qoutation".upper())
    qout_ui = InvQouteUI()
    qout_ui.gen_ui(gen_message="**Generate Qoutation**")
    
def gen_invoice():
    st.title("Generate new invoice".upper())
    inv_ui = InvQouteUI()
    inv_ui.gen_ui(gen_message="**Generate Invoice**")

qoutation = st.radio("**Select an option below**",["**Qoutation**", "**Invoice**"])

if qoutation.casefold() == "**Qoutation**".casefold():
    gen_qoutation()
elif qoutation.casefold() == "**Invoice**".casefold():
    gen_invoice()
