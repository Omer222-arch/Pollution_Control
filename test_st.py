import streamlit as st
import sys

def main():
    st.set_page_config(page_title="Test")
    st.write("Hello")

if __name__ == "__main__":
    from streamlit.web import cli as stcli
    import streamlit.runtime as runtime
    if runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
