import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

def cust_details():
    st.write("**Customer Details**")
    inv_to = st.text_input("Invoiced To", key="Invto")
    email = st.text_input("Client Email", key="email")
    contact = st.text_input("Contact Numbers", key="contnumb")
    address = st.text_area("Client Address", key="adr")

    return [inv_to, email, contact, address]

def inv_details(cust_type = ""):
    cust_type = ["Other", "ALW Properties", "Houghton"]
    st.write("**Invoice Details**")
    #Still under construction
    cust_selection = st.selectbox("Select Customer", cust_type,index=None, placeholder="Select customer", key="custtype")

    inv_no = st.text_input("Inv Number",disabled=True, key="Invnumb")
    inv_date = st.date_input("Inv Date", datetime.today(), format="DD-MM-YYYY", key="date")
    future_date  = inv_date + timedelta(days=30)
    in_due_date = st.date_input("Inv Due Date", format="DD-MM-YYYY", value=future_date, key="duedate")

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

    discount = st.checkbox("Add Discount", value=False, key="add_disc")
    if discount:
        discount_input = st.number_input("**Discount**",format="%0.2f", min_value=discount_input, max_value=float(subtot), key="discount_input")

    inst_cost = st.checkbox("Add Installation Cost", value=True, key="add_inst")
    if inst_cost:
        inst_cost_input = st.number_input("**Installation Cost**",format="%0.2f", min_value=inst_cost_input, value=float((st.session_state.get("sub_tot", 0.0) - st.session_state.get("discount_input", 0.0)) * 0.1), key="inst_cost_input")
    
    tax = st.checkbox("Add Tax Rate", value=False, key="add_tax", disabled=True)
    if tax:
        tax_input = st.number_input("**Tax Rate**",format="%0.2f", min_value=tax_input, disabled=True, value=float(((st.session_state.get("sub_tot", 0.0) + inst_cost_input) - st.session_state.get("discount_input", 0.0)) * TAX_RATE), key="tax_input")
    
    deposite = st.checkbox("Add Deposit", value=True, key="add_dep")
    if deposite:
        total_am = float(st.session_state.get("tot_bal", 0.0) + st.session_state.get("inst_cost_input", 0.0) + st.session_state.get("tax_input", 0.0))#
        deposite_input = st.number_input("**Deposit**",format="%0.2f", min_value=deposite_input,max_value=total_am, value=(total_am * DEPOSITE_RATE), key="dep_input")
    
    return [tax_input, discount_input, deposite_input, inst_cost_input]

def add_items_validator(item_descr, item_unit_price):
    valid = []
    if item_descr == None or item_descr.strip(" ") == "":
        valid.append(f"Please add the description of the item first on the **Descriptions** section.")

    if not item_unit_price > 0:
        valid.append(f"Please set the price of the product on **Unit Price** section")

    if st.session_state.get("custtype", None) == None:
        valid.append(f"Please make sure that you **select customer** first")
    
    if len(valid) > 0:
        validate_dilog(valid)
    return valid


def add_items(item_descr, item_unit_price, item_qty, item_total_price):

    add_valid = add_items_validator(item_descr, item_unit_price)
    if len(add_valid) == 0:
        abs_cursor.execute("""Insert into materials(invoiceNumber, description, unit_price, qty, total_amount) values(?,?,?,?,?)"""
                            , (st.session_state.get("Invnumb", '0'),item_descr, item_unit_price, item_qty, item_total_price,))
        st.session_state["current_status"] = "Reset"
        abs_db.commit()

def capture_items():
    st.write("**MATERIALS**")
    if st.session_state.get("current_status", "") == "Reset":
        descr, unit_price, qty_value = None, 0.00, 1
        st.session_state["current_status"] = ""
    else:
        descr, unit_price, qty_value = st.session_state.get("descr", None), st.session_state.get("unit_price", 0.00), st.session_state.get("qty", 1)
        
    item_descr = st.text_area("Descriptions", key="descr", value=descr)

    up, qty, tp = st.columns(3)

    with up:
        abs_db.commit()
        item_unit_price = st.number_input("Unit Price",format="%0.2f", min_value=0.00,value=float(unit_price), key="unit_price")

    with qty:
        abs_db.commit()
        item_qty = st.number_input("Quantity", min_value=1, key="qty", value=int(qty_value))

    if item_unit_price > 0 or item_qty > 1:
        st.session_state.total_price = item_qty * item_unit_price

    with tp:
        item_total_price = st.number_input("Total Price", format="%0.2f", key="total_price", disabled=True)

    if st.button("**Add Item**"):
        add_items(item_descr, item_unit_price, item_qty, item_total_price)

    abs_cursor.execute("select * from materials")
    table_data = abs_cursor.fetchall()
    if len(table_data):
        df = pd.DataFrame(table_data, columns=["Item Number", "invoice Number", "Description", "Unit price", "Quantity", "Total amount"])
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

def gen_qout_inv(gen_message=""):
    left, right = st.columns(2, border=True)
    with left:
        customer = cust_details()

    with right:
        invoice = inv_details()
    
    mat = st.columns(1, border=True)
    with mat[0]:
        capture_items()
    
    if st.session_state.get("current_status", "") == "Reset":
        st.rerun()
    
    if st.button(gen_message):
        abs_cursor.execute("select * from materials")
        finalise_inv_qout(abs_cursor.fetchall())
        abs_db.close()
        # st.rerun()

@st.dialog("Invoice To")
def validate_dilog(message):
    for m in message:
        st.write(m)

    if st.button("OKAY"):
        st.rerun()

def warning_validator():
    warnings = []

    if st.session_state.get("email", "").strip(" ") == "":
        warnings.append(f"Email not filled!")

    if st.session_state.get("contnumb", "").strip(" ") == "":
        warnings.append(f"You didn't capture the client contact numbers!")

    if st.session_state.get("adr", "").strip(" ") == "":
        warnings.append(f"Client address was not added!")
    
    for w in warnings:
        st.warning(w)

def finalise_inv_qout(mat_data):
    input_validator = []

    if not len(mat_data) > 0:
        input_validator.append(f"Please Please add 1 product first")

    if st.session_state.get("Invto", "").strip(" ") == "":
        input_validator.append(f"Please Fill in the **Invoice to**")
    
    if st.session_state.get("custtype", None) == None:
        input_validator.append(f"Please make sure that you **select customer**")
    
    if len(input_validator) > 0:
        st.write(input_validator)
        validate_dilog(input_validator)
    else:
        warning_validator()
        st.write(mat_data)
        abs_cursor.execute("DELETE FROM materials")
        abs_db.commit()

def gen_qoutation():
    st.title("Generate new qoutation".upper())
    gen_qout_inv(gen_message="**Generate Qoutation**")
    
def gen_invoice():
    st.title("Generate new invoice".upper())
    gen_qout_inv(gen_message="**Generate Invoice**")


abs_db = sqlite3.connect("AbsDatabase.db")
abs_cursor = abs_db.cursor()

tables = ["""
CREATE TABLE IF NOT EXISTS materials (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoiceNumber VARCHAR(255),
    description VARCHAR(255),
    unit_price DECIMAL(10, 2),
    qty INT,
    total_amount DECIMAL(12, 2)
)
"""
]
for query in tables:
    abs_cursor.execute(query)
abs_db.commit()

TAX_RATE = 0.15
DEPOSITE_RATE = 0.7

qoutation = st.radio("**Select an option below**",["**Qoutation**", "**Invoice**"])

if qoutation.casefold() == "**Qoutation**".casefold():
    gen_qoutation()
elif qoutation.casefold() == "**Invoice**".casefold():
    gen_invoice()
# elif qoutation.casefold() == "Edit Qoutation".casefold():
#     edit_qoutation()
# elif qoutation.casefold() == "Edit Invoice".casefold():
#     edit_invoice()



