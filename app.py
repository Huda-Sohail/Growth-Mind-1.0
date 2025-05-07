import streamlit as st
import pandas as pd
import os
from io import BytesIO
import altair as alt

st.set_page_config(page_title="Data Sweeper", layout='wide')


st.markdown(
    """
    <style>
    .stApp {
         background-color: black;
         color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Datasweeper Sterling Integrator")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization")

uploaded_files = st.file_uploader(
    "Upload your files (accept CSV and Excel):", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_name = file.name
        file_ext = os.path.splitext(file_name)[-1].lower()

        
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue
        df_display = df.copy()
        df_display = df_display.convert_dtypes()
        df_display = df_display.astype(str)


        st.write("### Preview of the Data")
        st.dataframe(df.head())

    
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file_name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from {file_name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates removed")

            with col2:
                if st.button(f"Fill missing values in {file_name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing values filled")

    
        st.subheader("Select Columns to Keep")
        columns = st.multiselect(f"Choose columns for {file_name}", df.columns, default=list(df.columns))
        df = df[columns]

    
        st.subheader("Data Visualization")
        numeric_df = df.select_dtypes(include='number')

        if st.checkbox(f"Show Visualization for: {file_name}"):
            if numeric_df.shape[1] >= 1:
                df_for_chart = numeric_df.iloc[:, :2].copy()
                df_for_chart["Row"] = df_for_chart.index
                melted_df = df_for_chart.melt(id_vars="Row", var_name="Metric", value_name="Value")

                chart = alt.Chart(melted_df).mark_bar().encode(
                    x=alt.X('Row:O', title='Row Index'),
                    y=alt.Y('Value:Q'),
                    color='Metric:N'
                ).properties(width=600)

                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("No numeric columns available for visualization.")

        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file_name} to:", ["CSV", "Excel"], key=file_name)

        if st.button(f"Convert {file_name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                converted_file_name = file_name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                converted_file_name = file_name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"Download {converted_file_name}",
                data=buffer,
                file_name=converted_file_name,
                mime=mime_type
            )

st.success("All files processed successfully!")
