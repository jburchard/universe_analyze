import os
import streamlit as st
import pandas as pd
import petl as etl

st.set_page_config(page_title="Universe Validate", page_icon="📆", layout="wide")
st.title("Universe Analyze")

st.selectbox('Universe Type', ['Mail'])

st.header("Upload File")
uploaded_file = st.file_uploader("Upload a csv")
delimiter = st.selectbox("Delimiter", ['Comma','Tab'])
if delimiter == 'Comma':
    delimiter = ','
if delimiter == 'Tab':
    delimiter == '\t'
if delimiter == 'Pipe':
    delimiter = '|'

if uploaded_file is not None:
    with st.expander('View Sample Records') as exp:
        df = pd.read_csv(uploaded_file, sep=delimiter, dtype=str)
        uploaded_file.seek(0)
        st.write(df[:100])

    st.header("Configuration")
    st.caption("Map the columns and enter expected values.")
    map_cols = st.columns([1,1,2])
    state = map_cols[0].selectbox('State Column', df.columns.values.tolist())
    valid_states = map_cols[1].text_input('Expected States', help="A list of states you expect to see in the file. Separate by multiple states comma. e.g. (IL, WI).")
    district = map_cols[0].selectbox('District Column', df.columns.values.tolist())
    valid_districts = map_cols[1].text_input('Expected Districts', help="A list of districts you expect to see in the file. Separate by multiple states comma. e.g. (01, 02).")
    
    def clean_text_input(input):
        input = input.split(',')
        return [i.strip() for i in input]
        
    def out_of_geo_count(df, col, valid_values):
        valid_values = clean_text_input(valid_values)
        out_of_geo = df[col].count() - df[col][df[col].isin(valid_values)].count()
        total = out_of_geo + df[col].isna().sum()
        return total
    
    st.header("Analysis")
    report_col = st.columns([1,1,1,1])
    report_col[0].metric('Records', len(df))
    if len(valid_states) > 0: 
        report_col[1].metric('Out Of State Or State Null', out_of_geo_count(df, state, valid_states))
    if len(valid_districts) > 0: report_col[2].metric('Out Of District Or District Null', out_of_geo_count(df, district, valid_districts))

