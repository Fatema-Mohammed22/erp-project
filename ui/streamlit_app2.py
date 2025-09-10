import streamlit as st, requests, json, os

API = os.getenv("MCP_API", "http://localhost:8000")

st.title("MCP Tooling — Agent ERP")
st.caption("Teammate 2 — Tool Registry + Adapters demo")

if st.button("List Tools"):
    r = requests.get(f"{API}/tools")
    st.json(r.json())

st.subheader("Execute a Tool")
tool = st.text_input("Tool name", "sales_sql_read")
params_str = st.text_area("Params (JSON)", '{"sql":"SELECT name FROM sqlite_master WHERE type = \'table\';"}')

if st.button("Run"):
    try:
        params = json.loads(params_str)
    except Exception as e:
        st.error(f"Invalid JSON: {e}")
        st.stop()
    r = requests.post(f"{API}/tools/execute", json={"tool_name": tool, "params": params})
    if r.status_code == 200:
        st.success("OK")
        st.json(r.json())
    else:
        st.error(f"Error {r.status_code}: {r.text}")
