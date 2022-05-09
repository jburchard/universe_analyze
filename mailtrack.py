import streamlit as st
import pandas as pd
from utilities import form_values
from io import StringIO


st.set_page_config(page_title="Universe Validate", page_icon="📆", layout="wide")
st.title("Universe Analyze")

st.selectbox('Universe Type', ['Mail'])

# File Uploader Code.
st.header("Upload File")
uploaded_file = st.file_uploader("Upload a csv")
csv_settings = st.columns([1,1,1])
delimiter = csv_settings[0].selectbox("Delimiter", ['Comma','Tab','Pipe','Custom Tab'])
if delimiter == 'Comma':
    delimiter = ','
if delimiter == 'Tab':
    delimiter = "\t"
if delimiter == 'Pipe':
    delimiter = '|'
encoding = csv_settings[1].selectbox("Encoding", ['utf_8', 'utf_16'])
encoding_errors = csv_settings[2].selectbox("Encoding Errors", ['strict', 'ignore'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=delimiter, encoding=encoding, encoding_errors=encoding_errors)
    with st.expander('View Sample Records') as exp:
            uploaded_file.seek(0)
            st.write(df[:100])

    # Configuration Code
    def guess_column(df, column_name):

        col_map = {'state': ['st','state'],
                   'district': ['hd', 'sd', 'cd', 'precinct']
                  }

        cols = df.columns.values.tolist()

        for col in cols:
            cleaned_col = col.lower().replace('_', '').replace(' ', '')
            for i in col_map[column_name]:
                if cleaned_col.find(i) != -1:
                    return cols.index(col)

    st.header("Configuration")
    st.caption("Map the columns and enter expected values.")
    map_cols = st.columns([1,1,2])
    state = map_cols[0].selectbox('State Column', df.columns.values.tolist(), index=guess_column(df, 'state'))
    valid_states = map_cols[1].multiselect('Expected States', form_values.states, help="You may select multiple states.")
    district = map_cols[0].selectbox('District Column', df.columns.values.tolist(), index=guess_column(df, 'district'))
    valid_districts = map_cols[1].text_input('Expected Districts', help="A list of districts you expect to see in the file. Separate by multiple states comma. e.g. (01, 02).")
    
    def clean_text_input(input):
        input = input.split(',')
        return [i.strip() for i in input]
        
    def out_of_geo_count(df, col, valid_values):
        if type(valid_values) == str:
            valid_values = clean_text_input(valid_values)
        out_of_geo = df[col].count() - df[col][df[col].isin(valid_values)].count()
        total = out_of_geo + df[col].isna().sum()
        return total
    
    # Analysis Code
    st.header("Analysis")
    report_col = st.columns([1,1,1,1])
    report_col[0].metric('Records', len(df))
    if len(valid_states) > 0: 
        report_col[1].metric('Out Of State Or State Null', out_of_geo_count(df, state, valid_states))
    if len(valid_districts) > 0: 
        report_col[2].metric('Out Of District Or District Null', out_of_geo_count(df, district, valid_districts))
