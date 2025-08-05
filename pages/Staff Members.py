import streamlit as st
import requests
import json
import sqlite3
import pandas as pd

abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

def run_query_list(query_list = []):
    for query in query_list:
        staff_cursor.execute(query)
    staff_db.commit()

def createTable():

    try:
        if not st.session_state.get('tables'):
            api_conne = requests.get("https://script.google.com/macros/s/AKfycbyZeOUxL5wj-shkOiysBLaLstwqNf2xRbz5r7MJNHBvdkR2qb2M_GEhxOg09hn-FIeRXg/exec?option=dataReader&menue=passdb")
            staff_tables = json.loads(api_conne.text)
            st.session_state['tables'] = staff_tables
           
        run_query_list(st.session_state.get('tables', {}).get('create tables', []))
        loadStaff()
    except ConnectionError:
        st.error(" Failed to connect to the server", icon="🚨")
    except Exception:
        st.error(" An error ocured while trying to connect to the server", icon="🚨")

def loadStaff():
    
    if not st.session_state.get('trips'):
        api_conne = requests.get("https://script.google.com/macros/s/AKfycbyZeOUxL5wj-shkOiysBLaLstwqNf2xRbz5r7MJNHBvdkR2qb2M_GEhxOg09hn-FIeRXg/exec?option=dataReader&menue=getabsstaff")
        staff_data = json.loads(api_conne.text)
        st.session_state['trips'] = staff_data

    run_query_list(st.session_state.get('trips', {}).get("deleteData",[]))
    run_query_list(st.session_state.get('trips', {}).get("query",[]))

def show_staff_table(staff_days):

    df = pd.DataFrame(staff_days, columns=["Date"])
    st.table(df)

def show_staff():
    staff_cursor.execute("SELECT * FROM USER")
    user_details = staff_cursor.fetchall()
    for user in user_details:
        st.divider()
        st.header(user[2])
        staff_cursor.execute("SELECT COUNT(*) FROM TRIPS WHERE UPPER(passid) = ?",(user[0],))
        num_days = staff_cursor.fetchone()
        st.subheader("SUMMARY")
        st.write(f"""
\nSalary: R
\nRate: R 
\nTotal number of days: {num_days[0]} 
\n""")
        if st.session_state.get(user[0]):
            staff_cursor.execute("SELECT tripDate FROM TRIPS WHERE UPPER(passid) = ?",(user[0],))
            show_staff_table(staff_cursor.fetchall())
        else:
            st.button("View Days", key=user[0])

st.title("Staff Members")
staff_db = sqlite3.connect("staffDatabase.db")
staff_cursor = staff_db.cursor()

createTable()
show_staff()
