import streamlit as st
from Model import InvQouteUI

abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

def edit_qoutation():
    qout_ui = InvQouteUI()
    qout_ui.gen_ui("Update Qoutation")

def qoutation_list():
    st.header("List of Qoutation")

st.title("Qoutations")

if st.session_state.get("qout_cancel") or not st.session_state.get("edit_qout"):
    qoutation_list()

if st.button("Edit Qoutation", key="edit_qout"):
    st.button("Cancel", key="qout_cancel")
    edit_qoutation()

