import streamlit as st
import pandas as pd
import dubo


def main():
    st.set_page_config(page_title="File Summary Statistics", page_icon=":chart_with_upwards_trend:", layout="wide")
    input_type = st.radio("Select Input Type", ("Text Input", "File Input"))
    f = 'https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv'
    if input_type == "File Input":
        f = st.file_uploader("Upload your file", type=["csv", "json"])
    else:
        url_list = ['https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv',
                    'https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv',
                    'https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv']
        f = st.selectbox("Select a URL", url_list)
    if f is not None:
        df = pd.read_csv(f)
        st.write("Data Preview:")
        st.write(df.head())
        st.write("Summary Statistics:")
        st.write(df.describe())
        while True:
            text = st.text_input("Enter dubo query:") or "who is the tallest?"
            st.write(dubo.ask(text, df))

if __name__ == "__main__":
    main()
