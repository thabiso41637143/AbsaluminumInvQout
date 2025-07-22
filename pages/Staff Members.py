import streamlit as st
import requests
import json
import sqlite3
import pandas as pd

def createTable():
    try:
        api_conne = requests.get("https://script.google.com/macros/s/AKfycbyZeOUxL5wj-shkOiysBLaLstwqNf2xRbz5r7MJNHBvdkR2qb2M_GEhxOg09hn-FIeRXg/exec?option=dataReader&menue=passdb")
        staff_tables = json.loads(api_conne.text)
        
        if staff_tables.get('create tables'):
            for query in staff_tables.get('create tables'):
                staff_cursor.execute(query)
            staff_db.commit()
            loadStaff()
        else:
            st.warning("Failed to load tables")
    except ConnectionError:
        st.error(" Failed to connect to the server", icon="🚨")
    except Exception:
        st.error(" An error ocured while trying to connect to the server", icon="🚨")

def loadStaff():
    api_conne = requests.get("https://script.google.com/macros/s/AKfycbyZeOUxL5wj-shkOiysBLaLstwqNf2xRbz5r7MJNHBvdkR2qb2M_GEhxOg09hn-FIeRXg/exec?option=dataReader&menue=getabsstaff")
    staff_data = json.loads(api_conne.text)

    for query in staff_data.get("deleteData",[]):
        staff_cursor.execute(query)

    for query in staff_data.get("query",[]):
        staff_cursor.execute(query)
    
    st.session_state["Staff Update"] = 1

def show_staff_table(staff_days):
    # st.write(staff_days)
    df = pd.DataFrame(staff_days, columns=["Date", "Amount"])
    df["Amount"] = df["Amount"].apply(lambda x: f"R {x:.2f}")
    st.table(df)

def show_staff():
    staff_cursor.execute("SELECT * FROM USER")
    user_details = staff_cursor.fetchall()
    for user in user_details:
        st.divider()
        st.header(user[2])
        st.subheader("SUMMARY")
        st.write(f"""
\nSalary: 
\nDays Absent: 
\nDays Present: 
\n""")
        if st.session_state.get(user[0]):
            staff_cursor.execute("SELECT TRIPS.tripDate, TRIPS.tripAmount FROM TRIPS, USER WHERE UPPER(USER.userId) = ? and USER.userId = TRIPS.passid",(user[0],))
            show_staff_table(staff_cursor.fetchall())

        st.button("View Days", key=user[0])
    # st.write(user_details)
    # st.write(st.session_state)


st.title("Staff Members")
# if st.session_state.get("Staff Update", False) == True:
staff_db = sqlite3.connect("staffDatabase.db")
staff_cursor = staff_db.cursor()
createTable()

show_staff()