# app.py
import streamlit as st

st.set_page_config(page_title="Depop → eBay Crosslister", page_icon="👕", layout="centered")

st.title("Depop → eBay Crosslister (Starter)")

st.write("This is a minimal starter. We’ll add editing + eBay API next.")

with st.form("demo_form"):
    title = st.text_input("Listing title", "Vintage Nike Tee")
    desc = st.text_area("Description", "Old school logo, size M")
    price = st.number_input("Price (AUD)", min_value=0.0, value=30.0, step=1.0)
    images = st.file_uploader("Upload images", accept_multiple_files=True)
    submitted = st.form_submit_button("Save draft")

if submitted:
    st.success("Draft saved (in memory for now).")
    st.json({"title": title, "desc": desc, "price": price, "images_count": len(images) if images else 0})

st.caption("Next: connect real Depop data → edit → publish to eBay AU.")
