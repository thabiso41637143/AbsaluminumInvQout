import streamlit as st
from Model import StaffData

abs_icon = open("Images/AbsAppIcon.png", "rb").read()
st.set_page_config(page_title="Absaluminum".upper(), page_icon=abs_icon)

def show_staff():
    try:
        for user in staff.get_all_user():
            st.header(user[2])
            st.subheader("SUMMARY")
            st.write(staff.get_staff_summary(user[0]))
            col1, col2, col3 = st.columns(3, border=False)
            with col1:
                st.button("View Days", key=user[0] + "view_days")
            with col2:
                st.button("View Loans", key=user[0] + "view_loans")
            with col3:
                st.button("View Profile", key=user[0] + "view_profile")
            if st.session_state.get(user[0] + "view_days"):
                st.write(staff.get_staff_dates(user[0]))
            elif st.session_state.get(user[0] + "view_profile"):
                st.write(staff.get_staff_profile(user[0]))
            elif st.session_state.get(user[0] + "view_loans"):
                st.write(staff.get_staff_loan(user[0]))

            st.divider()
    except Exception:
        st.error("Unable to show staff information.", icon="🚨")

def staff_register():
    selected_staff = []
    for st_id, st_name in staff.get_all_staff_names():
        if st.checkbox(st_name):
            selected_staff.append((st_id, st_name))
    
    if len(selected_staff) > 0:
        st.markdown(
    """
    <hr style="border: 4px dotted red;">
    """,
    unsafe_allow_html=True
)
        st.subheader("**List of staff that come to work**")
        for st_id, st_name in selected_staff:
            st.write(st_name)
        
        if st.button("Capture Staff"):
            capture_staff(selected_staff)
        st.markdown(
    """
    <hr style="border: 4px dotted red;">
    """,
    unsafe_allow_html=True
)

def capture_staff(selected_staff):
    st.write("Send to the database")
    print(selected_staff)
    st.session_state["show register"] = False
    st.rerun()

st.title("Staff Members")
staff = StaffData()
st.divider()
left, right = st.columns(2, border=False)

with left:
    st.button("View Staff Summary", key="staff_summary")
    if st.session_state.get("staff_summary"):
        st.session_state["show staff"] = True
        st.session_state["show register"] = False
        
with right:
    st.button("Staff Register", key= "staff_register")
    if st.session_state.get("staff_register"):
        st.session_state["show staff"] = False
        st.session_state["show register"] = True

if st.session_state.get("show staff"):
    show_staff()
elif st.session_state.get("show register"):
    staff_register()