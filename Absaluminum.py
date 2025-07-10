import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def cust_details():
    st.write("**Customer Details**")
    inv_to = st.text_input("Invoiced To")
    email = st.text_input("Client Email")
    contact = st.text_input("Contact Numbers")
    address = st.text_area("Client Adress")

    return [inv_to, email, contact, address]

def inv_details(cust_type = ""):
    cust_type = ["Other", "ALW Properties", "Houghton"]
    st.write("**Invoice Details**")
    #Still under construction
    cust_selection = st.selectbox("Select Customer", cust_type,index=None, placeholder="Select customer")

    inv_no = st.text_input("Inv Number",disabled=True)
    inv_date = st.date_input("Inv Date", datetime.today(), format="DD-MM-YYYY")
    future_date  = inv_date + timedelta(days=30)
    in_due_date = st.date_input("Inv Due Date", format="DD-MM-YYYY", value=future_date)

    return [inv_no, inv_date.strftime("%d %b %Y"), in_due_date.strftime("%d %b %Y")]

def totals(subtot = 0.00, add_totals = [0.00, 0.00, 0.00, 0.00]):
    st.write("**TOTALS**")
    sub_total = st.number_input("Sub Total",format="%0.2f", key="sub_tot", min_value=0.00, disabled=True, value=float(subtot))
    tot_less_disc = st.number_input("Total Less Discount",format="%0.2f", min_value=0.00, disabled=True, key="less_disc", value=float(subtot - add_totals[1]))
    tot_inc_tax = st.number_input("Total Amount Inc Tax",format="%0.2f", min_value=0.00, disabled=True, key="tax_amount", value=float(add_totals[0]))
    tot_balance = st.number_input("Total Balance",format="%0.2f", min_value=0.00,disabled=True, key="tot_bal", value=float(tot_less_disc + tot_inc_tax + add_totals[3]))

    return [sub_total, tot_less_disc, tot_inc_tax, tot_balance]

def additional_totals(subtot):
    tax_input, discount_input, deposite_input, inst_cost_input = [0.00, 0.00, 0.00, 0.00]

    st.write("**ADDITIONAL TOTALS**")

    discount = st.checkbox("Add Discount", value=False)
    if discount:
        discount_input = st.number_input("**Discount**",format="%0.2f", min_value=discount_input, max_value=float(subtot), key="discount_input")

    inst_cost = st.checkbox("Add Installation Cost", value=True)
    if inst_cost:
        inst_cost_input = st.number_input("**Installation Cost**",format="%0.2f", min_value=inst_cost_input, value=float(subtot * 0.1), key="inst_cost_input")
    
    tax = st.checkbox("Add Tax Rate", value=False)
    if tax:
        tax_input = st.number_input("**Tax Rate**",format="%0.2f", min_value=tax_input, disabled=True, value=float(((subtot + inst_cost_input) - discount_input) * TAX_RATE), key="tax_input")
    
    deposite = st.checkbox("Add Deposit", value=True)
    if deposite:
        total_am = float(subtot + inst_cost_input + tax_input)
        deposite_input = st.number_input("**Deposit**",format="%0.2f", min_value=deposite_input,max_value=total_am, value=(total_am * DEPOSITE_RATE), key="dep_input")
    
    return [tax_input, discount_input, deposite_input, inst_cost_input]

def capture_items():
    st.write("**MATERIALS**")
    item_descr = st.text_area("Descriptions")
    up, qty, tp = st.columns(3)

    with up:
        item_unit_price = st.number_input("Unit Price",format="%0.2f", min_value=0.00,value=0.00)

    with qty:
        item_qty = st.number_input("Quantity", min_value=1)

    if item_unit_price > 0 or item_qty > 1:
        st.session_state.total_price = item_qty * item_unit_price

    with tp:
        item_total_price = st.number_input("Total Price", format="%0.2f", key="total_price", disabled=True)

    if st.button("**Add Item**"):
        if item_descr == None or item_descr.strip(" ") == "" or not item_unit_price > 0:
            st.warning("Please fill the Description of the Item.")
        else:
            abs_cursor.execute("""Insert into materials(description, unit_price, qty, total_amount) values(?,?,?,?)"""
                               , (item_descr, item_unit_price, item_qty, item_total_price,))
            abs_db.commit()
    abs_cursor.execute("select * from materials")
    df = pd.DataFrame(abs_cursor.fetchall(), columns=["Item Number", "Description", "Unit price", "Quantity", "Total amount"])
    df["Total amount"] = df["Total amount"].apply(lambda x: f"R {x:.2f}")
    df["Unit price"] = df["Unit price"].apply(lambda x: f"R {x:.2f}")
    st.write("**List of items**")
    st.table(df)
    abs_cursor.execute("SELECT COALESCE(SUM(total_amount), 0.00) AS total_value FROM materials")
    sub_total = abs_cursor.fetchall()[0][0]

    left, right = st.columns(2, border=True)

    with left:
        add_totals = additional_totals(subtot=sub_total)

    with right:
        tot = totals(subtot=sub_total, add_totals=add_totals)

    

def gen_qoutation():
    st.write("**Generate new qoutation**")
    

    left, right = st.columns(2, border=True)
    with left:
        customer = cust_details()

    with right:
        invoice = inv_details()
    
    mat = st.columns(1, border=True)
    with mat[0]:
        capture_items()

    
    
    if st.button("Generate Qoutation"):
        abs_cursor.execute("DELETE FROM materials")
        abs_db.commit()
        abs_cursor.execute("select * from materials")
        st.write(abs_cursor.fetchall())
        abs_db.close()
        st.rerun()
    
def gen_invoice():
    st.write("Generate new invoice")

def edit_qoutation():
    st.write("Edit qoutaion")


def edit_invoice():
    st.write("Edit invoice")

abs_db = sqlite3.connect("AbsDatabase.db")
abs_cursor = abs_db.cursor()
tables = """
CREATE TABLE IF NOT EXISTS materials (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255),
    unit_price DECIMAL(10, 2),
    qty INT,
    total_amount DECIMAL(12, 2)
);
"""
abs_cursor.execute(tables)
TAX_RATE = 0.15
DEPOSITE_RATE = 0.7
st.title("ABSALUMINUM LTD (PTY) COMPANY")

qoutation = st.radio("Select an option below",["Qoutation", "Invoice", "Edit Qoutation", "Edit Invoice"])

if qoutation.casefold() == "Qoutation".casefold():
    gen_qoutation()
elif qoutation.casefold() == "Invoice".casefold():
    gen_invoice()
elif qoutation.casefold() == "Edit Qoutation".casefold():
    edit_qoutation()
elif qoutation.casefold() == "Edit Invoice".casefold():
    edit_invoice()



