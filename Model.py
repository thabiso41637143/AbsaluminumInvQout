import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import threading


#Invoice Qoutation class
class InvQouteUI:
    def __init__(self, tax_rate = 0.15, deposite_rate = 0.7):
        self.abs_db = sqlite3.connect("AbsDatabase.db")
        self.abs_cursor = self.abs_db.cursor()

        self.tables = ["""
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
        for query in self.tables:
            self.abs_cursor.execute(query)
        self.abs_db.commit()

        self.TAX_RATE = tax_rate
        self.DEPOSITE_RATE = deposite_rate

    def cust_details(self):
        st.write("**Customer Details**")
        self.inv_to = st.text_input("Invoiced To", key="Invto")
        self.cust_email = st.text_input("Client Email", key="email")
        self.cust_cont = st.text_input("Contact Numbers", key="contnumb")
        self.cust_addr = st.text_area("Client Address", key="adr")

    def totals(self, subtot = 0.00, add_totals = [0.00, 0.00, 0.00, 0.00]):
        st.write("**TOTALS**")
        self.sub_total = st.number_input("Sub Total",format="%0.2f", key="sub_tot", min_value=0.00, disabled=True, value=float(subtot))
        self.tot_less_disc = st.number_input("Total Less Discount",format="%0.2f", min_value=0.00, disabled=True, key="less_disc", value=float(subtot - add_totals[1]))
        self.tot_inc_tax = st.number_input("Total Amount Inc Tax",format="%0.2f", min_value=0.00, disabled=True, key="tax_amount", value=float(add_totals[0]))
        self.tot_balance = st.number_input("Total Balance",format="%0.2f", min_value=0.00,disabled=True, key="tot_bal", value=float(self.tot_less_disc + self.tot_inc_tax + add_totals[3]))

    def additional_totals(self, subtot):
        self.tax_input, self.discount_input, self.deposite_input, self.inst_cost_input = [0.00, 0.00, 0.00, 0.00]

        st.write("**ADDITIONAL TOTALS**")

        self.discount = st.checkbox("Add Discount", value=False, key="add_disc")
        if self.discount:
            self.discount_input = st.number_input("**Discount**",format="%0.2f", min_value=self.discount_input, max_value=float(subtot), key="discount_input")

        self.inst_cost = st.checkbox("Add Installation Cost", value=True, key="add_inst")
        if self.inst_cost:
            self.inst_cost_input = st.number_input("**Installation Cost**",format="%0.2f", min_value=self.inst_cost_input, value=float((st.session_state.get("sub_tot", 0.0) - st.session_state.get("discount_input", 0.0)) * 0.1), key="inst_cost_input")
        
        self.tax = st.checkbox("Add Tax Rate", value=False, key="add_tax", disabled=True)
        if self.tax:
            self.tax_input = st.number_input("**Tax Rate**",format="%0.2f", min_value=self.tax_input, disabled=True, value=float(((st.session_state.get("sub_tot", 0.0) + self.inst_cost_input) - st.session_state.get("discount_input", 0.0)) * self.TAX_RATE), key="tax_input")
        
        self.deposite = st.checkbox("Add Deposit", value=True, key="add_dep")
        if self.deposite:
            self.total_am = float(st.session_state.get("tot_bal", 0.0) + st.session_state.get("inst_cost_input", 0.0) + st.session_state.get("tax_input", 0.0))#
            self.deposite_input = st.number_input("**Deposit**",format="%0.2f", min_value=self.deposite_input,max_value=self.total_am, value=(self.total_am * self.DEPOSITE_RATE), key="dep_input")

        return [self.tax_input, self.discount_input, self.deposite_input, self.inst_cost_input]

    def add_items_validator(self, item_descr, item_unit_price):
        self.valid = []
        if item_descr == None or item_descr.strip(" ") == "":
            self.valid.append(f"Please add the description of the item first on the **Descriptions** section.")

        if not item_unit_price > 0:
            self.valid.append(f"Please set the price of the product on **Unit Price** section")

        if st.session_state.get("custtype", None) == None:
            self.valid.append(f"Please make sure that you **select customer** first")
        
        if len(self.valid) > 0:
            self.validate_dilog(self.valid)
        return self.valid

    def add_items(self, item_descr, item_unit_price, item_qty, item_total_price):

        self.add_valid = self.add_items_validator(item_descr, item_unit_price)
        if len(self.add_valid) == 0:
            self.abs_cursor.execute("""Insert into materials(invoiceNumber, description, unit_price, qty, total_amount) values(?,?,?,?,?)"""
                                , (st.session_state.get("Invnumb", '0'),item_descr, item_unit_price, item_qty, item_total_price,))
            st.session_state["current_status"] = "Reset"
            self.abs_db.commit()

    def capture_items(self):
        st.write("**MATERIALS**")
        if st.session_state.get("current_status", "") == "Reset":
            self.descr, self.unit_price, self.qty_value = None, 0.00, 1
            st.session_state["current_status"] = ""
        else:
            self.descr, self.unit_price, self.qty_value = st.session_state.get("descr", None), st.session_state.get("unit_price", 0.00), st.session_state.get("qty", 1)
            
        self.item_descr = st.text_area("Descriptions", key="descr", value=self.descr)

        up, qty, tp = st.columns(3)

        with up:
            self.abs_db.commit()
            self.item_unit_price = st.number_input("Unit Price",format="%0.2f", min_value=0.00,value=float(self.unit_price), key="unit_price")

        with qty:
            self.abs_db.commit()
            self.item_qty = st.number_input("Quantity", min_value=1, key="qty", value=int(self.qty_value))

        if self.item_unit_price > 0 or self.item_qty > 1:
            st.session_state.total_price = self.item_qty * self.item_unit_price

        with tp:
            self.item_total_price = st.number_input("Total Price", format="%0.2f", key="total_price", disabled=True)

        if st.button("**Add Item**"):
            self.add_items(self.item_descr, self.item_unit_price, self.item_qty, self.item_total_price)

        self.abs_cursor.execute("select * from materials")
        table_data = self.abs_cursor.fetchall()
        if len(table_data):
            df = pd.DataFrame(table_data, columns=["Item Number", "invoice Number", "Description", "Unit price", "Quantity", "Total amount"])
            df["Total amount"] = df["Total amount"].apply(lambda x: f"R {x:.2f}")
            df["Unit price"] = df["Unit price"].apply(lambda x: f"R {x:.2f}")
            st.write("**List of items**")
            st.table(df)
        self.abs_cursor.execute("SELECT COALESCE(SUM(total_amount), 0.00) AS total_value FROM materials")
        self.sub_total = self.abs_cursor.fetchall()[0][0]

        left, right = st.columns(2, border=True)
        with left:
            self.add_totals = self.additional_totals(subtot=self.sub_total)

        with right:
            self.tot = self.totals(subtot=self.sub_total, add_totals=self.add_totals)

    def gen_ui(self, gen_message=""):
        left, right = st.columns(2, border=True)
        with left:
            customer = self.cust_details()

        with right:
            invoice = self.inv_details()
        
        mat = st.columns(1, border=True)
        with mat[0]:
            self.capture_items()
        
        if st.session_state.get("current_status", "") == "Reset":
            st.rerun()
        
        if st.button(gen_message):
            self.abs_cursor.execute("select * from materials")
            self.finalise_inv_qout(self.abs_cursor.fetchall())
            self.abs_db.close()

    def inv_details(self, cust_type = ""):
        cust_type = ["Other", "ALW Properties", "Houghton"]
        st.write("**Invoice Details**")
        self.cust_selection = st.selectbox("Select Customer", cust_type,index=None, placeholder="Select customer", key="custtype")

        self.inv_no = st.text_input("Inv Number",disabled=True, key="Invnumb")
        self.inv_date = st.date_input("Inv Date", datetime.today(), format="DD-MM-YYYY", key="date")
        future_date  = self.inv_date + timedelta(days=30)
        self.in_due_date = st.date_input("Inv Due Date", format="DD-MM-YYYY", value=future_date, key="duedate")

        return [self.inv_no, self.inv_date.strftime("%d %b %Y"), self.in_due_date.strftime("%d %b %Y")]
        
    def warning_validator(self):
        self.warnings = []

        if st.session_state.get("email", "").strip(" ") == "":
            self.warnings.append(f"Email not filled!")

        if st.session_state.get("contnumb", "").strip(" ") == "":
            self.warnings.append(f"You didn't capture the client contact numbers!")

        if st.session_state.get("adr", "").strip(" ") == "":
            self.warnings.append(f"Client address was not added!")
        
        for w in self.warnings:
            st.warning(w)

    def finalise_inv_qout(self, mat_data):
        self.input_validator = []

        if not len(mat_data) > 0:
            self.input_validator.append(f"Please Please add 1 product first")

        if st.session_state.get("Invto", "").strip(" ") == "":
            self.input_validator.append(f"Please Fill in the **Invoice to**")
        
        if st.session_state.get("custtype", None) == None:
            self.input_validator.append(f"Please make sure that you **select customer**")
        
        if len(self.input_validator) > 0:
            st.write(self.input_validator)
            self.validate_dilog(self.input_validator)
        else:
            self.warning_validator()
            st.write(mat_data)
            self.abs_cursor.execute("DELETE FROM materials")
            self.abs_db.commit()

    @st.dialog("Invoice To")
    def validate_dilog(self, message):
        for m in message:
            st.write(m)

        if st.button("OKAY"):
            st.rerun()

    def __str__(self):
        return "Details of the user interface"

#Get data class
class  LoadStaffData:
    def __init__(self):
        self.load_trips_status = False
        self.load_cust_type_status = False
    
    def load_staff_tables(self):
        threading.Thread(target=self.get_staff_tables()).start()
        self.load_staff_tables = "Inprogress..."
        return st.session_state.get('tables error')

    def get_staff_tables(self):
        try:
            api_conne = requests.get("https://script.google.com/macros/s/AKfycbyZeOUxL5wj-shkOiysBLaLstwqNf2xRbz5r7MJNHBvdkR2qb2M_GEhxOg09hn-FIeRXg/exec?option=dataReader&menue=passdb")
            staff_tables = json.loads(api_conne.text)
            st.session_state['tables'] = staff_tables
            st.session_state["load_table_status"] = True
            self.load_staff_tables = "Completed"
            st.session_state['tables error'] = False
        except Exception as ex:
            print(ex)
            st.error("Failed to connect to the server and load tables")
            st.session_state['tables error'] = True

    def load_staff_trips(self):
        threading.Thread(target=self.get_staff_trips()).start()
        self.load_staff_trips = "Inprogress..."
        return st.session_state.get('trips error')
    
    def get_staff_trips(self):
        try:
            api_conne = requests.get("https://script.google.com/macros/s/AKfycbyZeOUxL5wj-shkOiysBLaLstwqNf2xRbz5r7MJNHBvdkR2qb2M_GEhxOg09hn-FIeRXg/exec?option=dataReader&menue=getabsstaff")
            staff_trips = json.loads(api_conne.text)
            st.session_state['trips'] = staff_trips
            st.session_state["load_trips_status"] = True
            self.load_staff_trips = "Completed"
            st.session_state['trips error'] = False
        except Exception as ex:
            print(ex)
            st.error("Failed to connect to the server and load days for the staff")
            st.session_state['trips error'] = True

    def load_staff(self):
        self.load_staff_tables()
        self.load_staff_trips()
        if st.session_state.get('tables error') or st.session_state['trips error']:
            return True
        return False

#Staff Class
class StaffData:
    def __init__(self):
        self.staff_data = LoadStaffData()
        self.staff_db = sqlite3.connect("staffDatabase.db")
        self.staff_cursor = self.staff_db.cursor()
        self.data_success = not self.set_days()

    def run_query_list(self, query_list = []):
        try:
            for query in query_list:
                self.staff_cursor.execute(query)
            self.staff_db.commit()
        except Exception:
            st.error(f"An error occured while running the query list{query_list}", icon="🚨")

    def set_tables(self):
        error_status = False
        if not st.session_state.get("load_table_status"):
            error_status = self.staff_data.load_staff()
        if not error_status:
            if st.session_state.get("load_table_status"):
                self.run_query_list(st.session_state.get("tables", {}).get('create tables', [])) 

        return error_status           

    def set_days(self):
        error_status = self.set_tables()
        if not error_status:
            if not st.session_state.get("load_trips_status"):
                self.staff_data.load_staff_trips()
            
            if st.session_state.get("load_table_status"):
                self.run_query_list(st.session_state.get('trips', {}).get("deleteData",[]))
                self.run_query_list(st.session_state.get('trips', {}).get("query",[]))
        return error_status

    def get_user(self, staff_id):
        if self.data_success:
            self.staff_cursor.execute("SELECT * FROM USER WHERE UPPER(userId) = ?",(staff_id,))
            return self.staff_cursor.fetchall()
        return []

    def get_staff_summary(self, staff_id):
        if self.data_success:
            return f"""
\nSalary: R
\nRate: R 
\nTotal number of days: {self.get_user_numdays(staff_id)} 
\n"""
        return f"failed to load staff summary data."

    def get_user_numdays(self, staff_id):
        if self.data_success:
            self.staff_cursor.execute("SELECT COUNT(*) FROM TRIPS WHERE UPPER(passid) = ?",(staff_id,))
            return self.staff_cursor.fetchone()[0]
        return 0

    def get_all_user(self):
        if self.data_success:
            self.staff_cursor.execute("SELECT * FROM USER")
            return self.staff_cursor.fetchall()
        return []
    
    def get_staff_dates(self, staff_id):
        if self.data_success:
            self.staff_cursor.execute("SELECT tripDate FROM TRIPS WHERE UPPER(passid) = ?",(staff_id,))
            return pd.DataFrame(self.staff_cursor.fetchall(), columns=["Date"])
        return f"No dates found"
    
    def get_staff_profile(self, staff_id):
        if self.data_success:
            data = self.get_user(staff_id)[0]
            return f"""**Staff ID:** {data[0]}
\n**Name:** {data[2]}
\n**Contacts:** {data[3]}
\n**Residential Address:** {data[5]}
\n**Company Name:** {data[6]}
"""
        return f"Staff data not found."

    #still under construction
    def get_staff_loan(self, staff_id): 
        return f"No loan is found"
    
    def get_all_staff_names(self):
        data = [(staff[0], staff[2])for staff in self.get_all_user()]
        return data

#Staff summary
class staffSummary:
    def __init__(self):
        self.staff_summary = StaffData()
        self.staff_cursor = self.staff_summary.staff_cursor
        self.data_success = self.staff_summary.data_success

    def get_staff_summary(self):
        if self.data_success:
            self.staff_cursor.execute("SELECT COUNT(*) FROM USER")
            numb_staff = self.staff_cursor.fetchone()[0]
            self.staff_cursor.execute("SELECT COUNT(*) FROM TRIPS")
            numb_days = self.staff_cursor.fetchone()[0]

            return f"""Total number of staff: {numb_staff}
    \nTotal number of days: {numb_days}"""
        return f"Failed to load staff data from the server."
