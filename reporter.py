import os
import pandas as pd
import base64
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

def img_to_base64_str(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def generate_pdf_reports(entities_folder, output_folder, template_name):
    # Ensure the entities folder exists
    if not os.path.exists(entities_folder):
        os.makedirs(entities_folder)
    # Ensure the entities folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_name)

    for entity in os.listdir(entities_folder):
        entity_path = os.path.join(entities_folder, entity)
        
        # Skip if it's not a directory
        if not os.path.isdir(entity_path):
            continue

        # Load data from CSV and images
        try:
            assigned_df = pd.read_csv(os.path.join(entity_path, f'{entity}_assigned_tickets.csv'))
            reported_df = pd.read_csv(os.path.join(entity_path, f'{entity}_reported_tickets.csv'))
            work_hours_df = pd.read_csv(os.path.join(entity_path, f'{entity}_work_hours.csv'))
        except FileNotFoundError as e:
            print(f"CSV file not found for {entity}: {e}")
            continue

        # Convert DataFrames to HTML tables
        assigned_table = assigned_df.to_html(index=False, classes="table")
        reported_table = reported_df.to_html(index=False, classes="table")
        work_hours_table = work_hours_df.to_html(index=False, classes="table")

        # Get the total work hours and days
        total_hours = work_hours_df['Hours'][0]
        total_days = work_hours_df['Days'][0]

        # Convert images to base64 strings
        assigned_chart_base64 = img_to_base64_str(os.path.join(entity_path, f'{entity}_assigned_pie_chart.png'))
        reported_chart_base64 = img_to_base64_str(os.path.join(entity_path, f'{entity}_reported_pie_chart.png'))
        work_hours_chart_base64 = img_to_base64_str(os.path.join(entity_path, f'{entity}_work_hours_bar_chart.png'))

        # Render the HTML content
        html_content = template.render(
            entity_name=entity,
            assigned_table=assigned_table,
            reported_table=reported_table,
            work_hours_table=work_hours_table,
            total_hours=total_hours,
            total_days=total_days,
            assigned_chart=f'data:image/png;base64,{assigned_chart_base64}',
            reported_chart=f'data:image/png;base64,{reported_chart_base64}',
            work_hours_chart=f'data:image/png;base64,{work_hours_chart_base64}'
        )

        # Create PDF with A4 page size
        HTML(string=html_content).write_pdf(
            os.path.join(output_folder, f'{entity}_report.pdf'),
            stylesheets=[CSS(string='@page { size: A4; margin: 0; }')]
        )

# Specify the folder containing entity subfolders
entities_folder = './entities'
# Specify the output folder for PDF reports
output_folder = './reports'
# Template file (located in the current directory)
template_name = 'report_template.html'

# Generate the PDF reports
generate_pdf_reports(entities_folder, output_folder, template_name)
