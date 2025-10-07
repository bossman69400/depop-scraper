# app.py
import streamlit as st
from typing import List, Dict

st.set_page_config(page_title="Depop → eBay Crosslister", page_icon="👕", layout="centered")

if "drafts" not in st.session_state:
    st.session_state.drafts: List[Dict] = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None  # which draft we’re editing

st.title("Depop → eBay Crosslister")
st.subheader("Create a new draft")

with st.form("create_form", clear_on_submit=True):
    c1, c2 = st.columns([2, 1])
    with c1:
        title = st.text_input("Title", "Vintage Nike Tee")
        desc = st.text_area("Description", "Old school logo, size M")
    with c2:
        price = st.number_input("Price (AUD)", min_value=0.0, value=30.0, step=1.0)
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    images = st.file_uploader("Images", accept_multiple_files=True)

    submitted = st.form_submit_button("Add to drafts")

if submitted:
    new_item = {
        "title": title.strip(),
        "desc": desc.strip(),
        "price": float(price),
        "quantity": int(quantity),
        "images": images or [],  # list of UploadedFile objects for now
    }
    st.session_state.drafts.append(new_item)
    st.success("Draft added.")


