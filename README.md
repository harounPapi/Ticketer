
**Running the Ticketer Application**

This guide will walk you through the steps to run the Ticketer application. Ticketer is a Python-based project, and it uses Streamlit for the user interface.

**Prerequisites:**

- Python installed on your system.
- Git installed on your system.
- A terminal or command prompt.

**Installation Steps:**

1. **Clone the Repository:**

   Open your terminal and run the following command to clone the Ticketer repository from GitHub:

   ```bash
   git clone https://github.com/harounPapi/Ticketer.git
   ```

   This command will download the Ticketer project files to your local machine.

2. **Navigate to the Project Directory:**

   Change your current directory to the "Ticketer" project directory using the `cd` command:

   ```bash
   cd Ticketer
   ```

   You should now be inside the "Ticketer" directory where the project files are located.

3. **Install Dependencies:**

   Next, you need to install the required Python libraries listed in the `requirements.txt` file. Run the following command:

   ```bash
   pip install -r requirements.txt
   ```

   This command will use `pip` to install all the necessary libraries for the Ticketer application.

4. **Run the Application:**

   Once the dependencies are installed, you can run the Ticketer application using Streamlit. Run the following command:

   ```bash
   streamlit run app.py
   ```

   This command will start the Streamlit server and launch the Ticketer application in your default web browser.

5. **Explore the Application:**

   - **Dashboard:** The Ticketer application consists of two main pages. The "Dashboard" page provides insights and visualizations for the uploaded data. Here, you can explore various statistics and trends related to the data entities.

   - **Add Data:** The "Add Data" page allows you to upload data files. You can upload a single file, or if you check the "Bulk" option, you can upload multiple files in bulk. Once the data is processed, you will find the insights displayed on the "Dashboard" page.

   - **Downloading PDF Reports:** Each entity displayed on the "Dashboard" has an associated PDF report that provides detailed information and analysis. To download a PDF report, simply click the "Download Report" button next to the respective entity.

6. **Exit the Application:**

   To stop the Streamlit server and exit the application, you can simply close the terminal or press `Ctrl + C` in the terminal where the Streamlit server is running.

**Congratulations!** You've successfully cloned, installed dependencies, and run the Ticketer application on your local machine. Enjoy using Ticketer for your ticket-related tasks and exploring the insights and reports generated from your data.