import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image 
from reporter import generate_pdf_reports


def categorize_status(status):
    categories = ['resolved', 'closed', 'assigned', 'delayed', 'feedback', 'inprogress']
    return status if status in categories else 'other'

def add_percentage_column(status_counts, total):
    percentages = (status_counts / total * 100).round(2).astype(str) + '%'
    return pd.DataFrame({'Status': status_counts.index, 'Count': status_counts.values, 'Percentage': percentages})

def create_entity_folder(entity_name):
    entities_folder = './entities'
    if not os.path.exists(entities_folder):
        os.makedirs(entities_folder)
    folder_path = os.path.join(entities_folder, entity_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def save_to_csvs(entity, assigned_table, reported_table):
    folder_path = create_entity_folder(entity)

    assigned_file_name = f'{folder_path}/{entity}_assigned_tickets.csv'
    reported_file_name = f'{folder_path}/{entity}_reported_tickets.csv'

    assigned_table.to_csv(assigned_file_name, index=False)
    reported_table.to_csv(reported_file_name, index=False)
    st.success('Data saved successfully for both assigned and reported tickets!')

def save_work_hours_to_csv(entity, work_hours, avg_hours_assigned, avg_hours_reported):
    folder_path = create_entity_folder(entity)
    work_hours_file = f'{folder_path}/{entity}_work_hours.csv'

    data = {
        'Metric': ['Total work hours', 'Average hours per assigned ticket', 'Average hours per reported ticket'],
        'Hours': [work_hours, avg_hours_assigned, avg_hours_reported],
        'Days': [work_hours / 8, avg_hours_assigned / 8, avg_hours_reported / 8]  # Convert hours to workdays
    }
    df = pd.DataFrame(data)
    df.to_csv(work_hours_file, index=False)
    st.success('Work hours data saved successfully!')

def calculate_work_hours(start_date, end_date):
    start = np.datetime64(datetime.strptime(start_date, '%Y-%m-%d'), 'D')
    end = np.datetime64(datetime.strptime(end_date, '%Y-%m-%d'), 'D')
    total_days = np.busday_count(start, end + np.timedelta64(1, 'D'))
    return total_days * 8  # 8 hours per day

def calculate_average_hours(total_hours, count):
    return total_hours / count if count > 0 else 0

def generate_and_save_charts(entity, assigned_table, reported_table, work_hours_data):
    folder_path = create_entity_folder(entity)

    # Generate and save pie chart for assigned tickets
    assigned_pie_fig, assigned_ax = plt.subplots()
    assigned_percentages = assigned_table[:-1]['Percentage'].str.rstrip('%').astype(float)
    assigned_labels = assigned_table[:-1]['Status']
    assigned_colors = plt.cm.tab20(np.linspace(0, 1, len(assigned_labels)))
    assigned_ax.pie(assigned_percentages, labels=assigned_labels, colors=assigned_colors, autopct='%1.1f%%')
    assigned_ax.axis('equal')
    assigned_pie_filename = f'{folder_path}/{entity}_assigned_pie_chart.png'
    assigned_pie_fig.savefig(assigned_pie_filename)

    # Generate and save pie chart for reported tickets
    reported_pie_fig, reported_ax = plt.subplots()
    reported_percentages = reported_table[:-1]['Percentage'].str.rstrip('%').astype(float)
    reported_labels = reported_table[:-1]['Status']
    reported_colors = plt.cm.tab20(np.linspace(0, 1, len(reported_labels)))
    reported_ax.pie(reported_percentages, labels=reported_labels, colors=reported_colors, autopct='%1.1f%%')
    reported_ax.axis('equal')
    reported_pie_filename = f'{folder_path}/{entity}_reported_pie_chart.png'
    reported_pie_fig.savefig(reported_pie_filename)

    # Generate and save bar chart for work hours data
    work_hours_fig, work_hours_ax = plt.subplots()
    filtered_data = work_hours_data[work_hours_data['Metric'] != 'Total work hours']
    work_hours_ax.bar(filtered_data['Metric'], filtered_data['Days'], color=plt.cm.Paired(np.arange(len(filtered_data))))
    work_hours_ax.set_xlabel('Metric')
    work_hours_ax.set_ylabel('Days')
    work_hours_ax.set_title('Work Hours Data (in days)')
    work_hours_bar_filename = f'{folder_path}/{entity}_work_hours_bar_chart.png'
    work_hours_fig.savefig(work_hours_bar_filename)

def add_data():
    st.title("Add Data to CSV")
    
    # Check if bulk upload is needed
    is_bulk_upload = st.checkbox('Bulk Upload')
    uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=is_bulk_upload)

    def process_file(uploaded_file):
        data = pd.read_csv(uploaded_file)
        entity = data['Reporter'].iloc[0]

        # Check if the expected columns are in the CSV
        if 'Assigned To' not in data.columns or 'Reporter' not in data.columns:
            st.error(f"The uploaded file {uploaded_file.name} does not contain the required columns.")
            return

        entity = data['Reporter'].iloc[0]

        # Processing 'Assigned To' data
        assigned_data = data[data['Assigned To'] == entity]
        assigned_categorized_statuses = assigned_data['Status.1'].apply(categorize_status)
        assigned_status_counts = assigned_categorized_statuses.value_counts()
        assigned_total = assigned_status_counts.sum()
        assigned_status_counts.loc['Total'] = assigned_total
        assigned_table = add_percentage_column(assigned_status_counts, assigned_total)


        # Processing 'Reported By' data
        reported_data = data[data['Reporter'] == entity]
        reported_categorized_statuses = reported_data['Status'].apply(categorize_status)
        reported_status_counts = reported_categorized_statuses.value_counts()
        reported_total = reported_status_counts.sum()
        reported_status_counts.loc['Total'] = reported_total
        reported_table = add_percentage_column(reported_status_counts, reported_total)

        # Extract and calculate work hours
        start_date_str, end_date_str = data.iloc[0, -2:]
        work_hours = calculate_work_hours(start_date_str, end_date_str)

        # Calculate average hours and days per ticket
        avg_hours_assigned = calculate_average_hours(work_hours, assigned_status_counts.get('resolved', 0))
        avg_hours_reported = calculate_average_hours(work_hours, reported_status_counts.get('resolved', 0))

        # Saving the analysis to CSVs and generating charts
        save_to_csvs(entity, assigned_table, reported_table)
        save_work_hours_to_csv(entity, work_hours, avg_hours_assigned, avg_hours_reported)
        generate_and_save_charts(entity, assigned_table, reported_table, pd.DataFrame({
            'Metric': ['Total work hours', 'Average hours per assigned ticket', 'Average hours per reported ticket'],
            'Hours': [work_hours, avg_hours_assigned, avg_hours_reported],
            'Days': [work_hours / 8, avg_hours_assigned / 8, avg_hours_reported / 8]
        }))
        st.success(f"Processed {entity}")
            
        save_to_csvs(entity, assigned_table, reported_table)
        save_work_hours_to_csv(entity, work_hours, avg_hours_assigned, avg_hours_reported)
        generate_and_save_charts(entity, assigned_table, reported_table, pd.DataFrame({
            'Metric': ['Total work hours', 'Average hours per assigned ticket', 'Average hours per reported ticket'],
            'Hours': [work_hours, avg_hours_assigned, avg_hours_reported],
            'Days': [work_hours / 8, avg_hours_assigned / 8, avg_hours_reported / 8]
        }))

    if uploaded_files:
        if not is_bulk_upload:
            uploaded_files = [uploaded_files]  # Wrap single file into list

        for uploaded_file in uploaded_files:
            process_file(uploaded_file)  # Process each uploaded file

        st.success('All files have been processed.')

        # After processing all files, generate PDF reports
        entities_folder = './entities'
        output_folder = './reports'
        template_name = 'report_template.html'
        generate_pdf_reports(entities_folder, output_folder, template_name)
        st.success('PDF reports generated.')

def display_dashboard():
    st.title("Dashboard")
    entities_folder = './entities'
    reports_folder = './reports'  # Folder where PDF reports are stored
    entities = [folder for folder in os.listdir(entities_folder) if os.path.isdir(os.path.join(entities_folder, folder))]
    selected_entity = st.selectbox("Select Entity", entities)
    data_type = st.selectbox("Select Data Type", ["Assigned Tickets", "Reported Tickets", "Work Hours Data"])

    if selected_entity and data_type:
        entity_folder = os.path.join(entities_folder, selected_entity)
        csv_file_name = os.path.join(entity_folder, f"{selected_entity}_{data_type.lower().replace(' ', '_')}.csv")
        chart_file_name = ''
        
        if data_type == "Assigned Tickets":
            chart_file_name = os.path.join(entity_folder, f"{selected_entity}_assigned_pie_chart.png")
        elif data_type == "Reported Tickets":
            chart_file_name = os.path.join(entity_folder, f"{selected_entity}_reported_pie_chart.png")
        elif data_type == "Work Hours Data":
            chart_file_name = os.path.join(entity_folder, f"{selected_entity}_work_hours_bar_chart.png")

        if os.path.exists(csv_file_name):
            data = pd.read_csv(csv_file_name)
            st.write(f"{data_type} Overview:")
            st.dataframe(data)

        if os.path.exists(chart_file_name):
            image = Image.open(chart_file_name)
            st.image(image, caption=f'{data_type} Chart', use_column_width=True)

        # Check for the existence of the PDF report and provide a download link
        pdf_report = os.path.join(reports_folder, f"{selected_entity}_report.pdf")
        if os.path.exists(pdf_report):
            with open(pdf_report, "rb") as file:
                btn = st.download_button(
                    label="Download PDF Report",
                    data=file,
                    file_name=f"{selected_entity}_report.pdf",
                    mime="application/octet-stream"
                )
        else:
            st.error("PDF report not found. Please generate the report.")




def main():
    st.set_page_config(page_title="Ticketer", page_icon="📊")
    st.markdown("""
        <style>
        .css-18e3th9 {
            background-color: #f0f2f6;
            color: #4f8bf9;
        }
        .st-bx {
            color: #4f8bf9;
        }
        .st-ae {
            color: #4f8bf9;
        }
        </style>
        """, unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page", ["Dashboard", "Add Data"])
    if page == "Dashboard":
        display_dashboard()
    else:
        add_data()

if __name__ == "__main__":
    main()