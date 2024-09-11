import streamlit as st
import pandas as pd
from openai import OpenAI
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64

#%% Load environment variables (e.g., for API keys)
from dotenv import load_dotenv
load_dotenv()

#%% Data preparation
df = pd.read_csv("sales_data_sample.csv")


#%%SQL Database Set-up
temp_db = create_engine('sqlite:///:memory:', echo=True)
data = df.to_sql(name='Sales',con=temp_db)


#%% Set-up Open AI API Key
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
##    api_key=OPENAI_API_KEY,
#)



#%% Helper Functions
#%% Helper Functions
def create_table_definition_prompt(df):
    """Create a SQL table structure definition as prompt for GPT."""
    columns = ", ".join(df.columns)
    return f"### sqlite SQL table with columns:\n# Sales({columns})\n"

def combine_prompts(df, query_prompt):
    """Combine table definition and user query prompt."""
    definition = create_table_definition_prompt(df)
    query_init_string = f"### A query to answer: {query_prompt}\nSELECT"
    return definition + query_init_string

def handle_response(response):
    """Extract SQL query from GPT response."""
    query = response.choices[0].message.content.strip()
    if not query.lower().startswith("select"):
        query = "SELECT " + query
    return query

def execute_sql(query):
    """Execute a SQL query and return results as a dataframe."""
    with temp_db.connect() as conn:
        result = conn.execute(text(query))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

def remove_backticks(input_string):
    # Remove all occurrences of the backtick character `
    cleaned_string = input_string.replace("`", "")
    # Remove all occurrences of the word 'python' (case-insensitive)
    cleaned_string = cleaned_string.replace("python", "")
    return cleaned_string

def generate_plot_code(df):
    """Generate Python plotting code using GPT based on the dataframe structure."""
    columns = ", ".join(df.columns)
    prompt = f"Generate Python code to plot a DataFrame with columns: {columns} using matplotlib. Output only the code such that it can be immediately executed in python. And be creative with the types of graphs produced"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=4000,
    )
    return remove_backticks(response.choices[0].message.content.strip())

def image_to_base64(img):
    """Convert an image to base64 format."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode()

def add_image_to_gpt_message(image_base64, image_type="image/png"):
    """Add image to GPT message as base64 encoded string."""
    return {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{image_type};base64,{image_base64}"}
            }
        ]
    }

#%% Streamlit Page Layout
# Set page configuration
st.set_page_config(
    page_title="Byte Insight - AI SQL Query and Data Visualization",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Setup
st.sidebar.title("About the App")
st.sidebar.info(
    """
    This app enables users to interact with a database using natural language queries. Instead of relying on complex SQL commands, users can simply input their requests in everyday language. The app processes the input, extracts relevant data from the database, and returns the results in a user-friendly format—either as a data table or a dynamic visualization. This tool streamlines data retrieval and makes it accessible to non-technical users, empowering them to make data-driven decisions with ease.
    """
)

# Header
# CSS to center elements
st.markdown(
    """
    <style>
    .center-text {
        text-align: center;
    }
    .center-image img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True
)

# Header
st.markdown('<h1 class="center-text">Byte Insight💡</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="center-text">AI-Powered Data Query and Visualization🦾</h3>', unsafe_allow_html=True)

with st.sidebar:
        default_openai_api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        with st.popover("🔐 OpenAI API Key"):
            openai_api_key = st.text_input("Introduce your OpenAI API Key (https://platform.openai.com/)", value=default_openai_api_key, type="password")

    # --- Main Content ---
# Checking if the user has introduced the OpenAI API Key, if not, a warning is displayed
if openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key:
    st.write("#")
    st.warning("⬅️ Please introduce your OpenAI API Key (make sure to have funds) to continue...")  

    with st.sidebar:
        st.write("#")
        st.write("#")
        st.video("EQ.mp4")
        st.write("📋[Stemperiodt Blog](https://stemperiodt.co.za/blog/)")

else:
    client = OpenAI(api_key=openai_api_key)          

# Image
image = Image.open("Data.png")  # Replace with your image path
st.markdown('<div class="center-image">', unsafe_allow_html=True)
st.image(image, use_column_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input form for user query
st.write("### Step 1: Enter your query:")
query_prompt = st.text_input("What would you like to know about the data?")

# Run the query
if st.button("Run Query"):
    with st.spinner("Generating SQL query..."):
        gpt_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": combine_prompts(df, query_prompt)}],
            temperature=0,
            max_tokens=4000
        )

        # Extract and run the generated SQL query
        sql_query = handle_response(gpt_response)
        #st.write(f"**Generated SQL Query**:\n{sql_query}")
        
        # Execute the SQL query and display the result as a dataframe
        result_df = execute_sql(sql_query)
        if not result_df.empty:
            st.write("### Step 2: View the Query Results:")
            st.dataframe(result_df)

# Option to visualize the results
if st.button("Visualize Data"):
    with st.spinner("Generating plot code..."):
        gpt_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": combine_prompts(df, query_prompt)}],
        temperature=0,
        max_tokens=4000
    )
        sql_query = handle_response(gpt_response)
        #st.write(f"**Generated SQL Query**:\n{sql_query}")
            
            # Execute the SQL query and display the result as a dataframe
        result_df = execute_sql(sql_query)
        plot_code = generate_plot_code(result_df)
        #st.write(f"**Generated Plot Code**:\n{plot_code}")

        # Dynamically execute the generated plot code in a secure manner
        figure, ax = plt.subplots()
        # Use exec() but ensure the plot is built correctly by capturing the generated figure
        exec(plot_code, {"df": result_df, "plt": plt, "ax": ax})

        # Display the plot in Streamlit
        st.write("### Step 3: Visualized Results")
        st.pyplot(plt.gcf())
        # Save the generated plot as an image in-memory
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        # Convert the image to base64 for GPT analysis
        img = Image.open(img_buffer)
        img_base64 = image_to_base64(img)

         # Add the image to the GPT message
        gpt_message = add_image_to_gpt_message(img_base64, image_type="image/png")

        # Send the base64 image to GPT-4 for analysis
        with st.spinner("Analyzing the figure..."):
            analysis_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[gpt_message],
                temperature=0,
                max_tokens=4000,
            )
            st.write("### Step 4: Visual Analysis")
            st.write(analysis_response.choices[0].message.content)
# Footer
st.markdown("---")
st.write("Designed By Royal Mcgrady Data Science")