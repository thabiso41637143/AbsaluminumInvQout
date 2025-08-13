from Model import InvQouteUI
import streamlit as st


abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

def edit_invoice():
    qout_ui = InvQouteUI()
    qout_ui.gen_ui("Update Invoice")

def invoice_list():
    st.header("List of Invoices")

st.title("Invoices")

if st.session_state.get("inv_cancel") or not st.session_state.get("edit_inv"):
    invoice_list()

if st.button("Edit Invoice", key="edit_inv"):
    st.button("Cancel", key="inv_cancel")
    edit_invoice()


