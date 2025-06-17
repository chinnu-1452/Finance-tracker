import streamlit as st
import pandas as pd
from datetime import datetime
from db import *

# Initialize DB
init_db()

# Login System
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Expense Tracker")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            success = register_user(new_username, new_password)
            if success:
                st.success("Account created successfully!")
            else:
                st.error("Username already exists")

else:
    user_id = get_user_id(st.session_state['username'])
    st.sidebar.title(f"Welcome, {st.session_state['username']} 👋")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
    st.sidebar.write("Manage your expenses efficiently!")
    st.sidebar.write("Track your spending, categorize expenses, and analyze your financial habits.")

    # Main App
    st.title("Expense Tracker")

    # Add Expense
    st.header("Add Expense")
    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.today())
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0, step=0.5)
        if st.form_submit_button("Add"):
            add_expense(user_id, date.strftime("%Y-%m-%d"), category, amount)
            st.success("Expense Added!")

    # View Expenses with Filter
    st.header("View Expenses")

    expenses = get_expenses(user_id)
    if expenses:
        df = pd.DataFrame(expenses, columns=['ID', 'Date', 'Category', 'Amount'])
        df['Date'] = pd.to_datetime(df['Date'])

        # Date filter
        col1, col2 = st.columns(2)
        from_date = col1.date_input("From Date", df['Date'].min())
        to_date = col2.date_input("To Date", df['Date'].max())

        mask = (df['Date'] >= pd.to_datetime(from_date)) & (df['Date'] <= pd.to_datetime(to_date))
        filtered_df = df.loc[mask]

        st.dataframe(filtered_df.drop(columns='ID', axis=1), use_container_width=True)
        
        st.write(f"Total for selected period: ${filtered_df['Amount'].sum():.2f}")

        # Edit & Delete Section
        st.subheader("Edit Expenses in selected period")

        for index, row in filtered_df.iterrows():
            with st.expander(f"Expense ID {row['Date'].strftime('%Y-%m-%d')} - {row['Category']}"):
                edit_date = st.date_input("Edit Date", row['Date'], key=f"date_{row['ID']}")
                edit_category = st.text_input("Edit Category", row['Category'], key=f"cat_{row['ID']}")
                edit_amount = st.number_input("Edit Amount", value=row['Amount'], key=f"amt_{row['ID']}")

                col1, col2 = st.columns(2)
                if col1.button("Update", key=f"update_{row['ID']}"):
                    update_expense(row['ID'], edit_date.strftime("%Y-%m-%d"), edit_category, edit_amount)
                    st.success("Updated successfully!")
                    st.rerun()

                if col2.button("Delete", key=f"delete_{row['ID']}"):
                    delete_expense(row['ID'])
                    st.success("Deleted successfully!")
                    st.rerun()

        # Summary charts
        with st.expander("Monthly Breakdown"):
            st.write("---")
            df['Month'] = df['Date'].dt.to_period("M")
            monthly_total = df.groupby('Month')['Amount'].sum()
            st.subheader("Monthly Summary")
            st.write(monthly_total)

        with st.expander("Category Breakdown"):
            st.write("---")
            df['Category'] = df['Category'].str.strip().str.title()
            category_total = df.groupby('Category')['Amount'].sum()
            st.subheader("Category Breakdown")
            st.write(category_total)
    else:
        st.info("No expenses found.")
