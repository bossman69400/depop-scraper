import streamlit as st
from typing import List, Dict
import json, os, io, csv

st.set_page_config(page_title="Depop → eBay Crosslister", page_icon="👕", layout="centered")

DATA_PATH = "drafts.json"

def save_drafts_to_file(drafts):
    # Convert non-serializable types (like images) into placeholders
    serializable = []
    for d in drafts:
        serializable.append({
            "title": d["title"],
            "desc": d["desc"],
            "price": d["price"],
            "quantity": d.get("quantity", 1),
            "images": [getattr(f, 'name', 'file') for f in d.get("images", [])],
        })
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

def load_drafts_from_file():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            d["images"] = []  # can't restore files, names only
        return data
    return []

# ---- Session State Initialization ----

if "drafts" not in st.session_state:
    st.session_state.drafts: List[Dict] = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Load drafts if not yet loaded (first run)
if not st.session_state.drafts:
    st.session_state.drafts = load_drafts_from_file()

st.title("Depop → eBay Crosslister")
st.caption("Step 2: Add, review, edit your drafts. Next up: eBay export!")

# --- NEW DRAFT FORM ---

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
        "images": images or [],
    }
    st.session_state.drafts.append(new_item)
    save_drafts_to_file(st.session_state.drafts)
    st.success("Draft added.")

# --- BULK IMPORT BY CSV ---
st.divider()
st.subheader("Bulk import drafts (CSV)")
help_text = "CSV headers: title,desc,price,quantity"
csv_file = st.file_uploader("Upload CSV", type=["csv"], help=help_text, key="csv_importer")
if csv_file is not None:
    reader = csv.DictReader(io.StringIO(csv_file.getvalue().decode("utf-8")))
    added = 0
    for row in reader:
        try:
            st.session_state.drafts.append({
                "title": row.get("title", "").strip(),
                "desc": row.get("desc", "").strip(),
                "price": float(row.get("price", 0) or 0),
                "quantity": int(row.get("quantity", 1) or 1),
                "images": [],
            })
            added += 1
        except Exception:
            pass
    save_drafts_to_file(st.session_state.drafts)
    st.success(f"Imported {added} drafts.")

# --- DRAFTS TABLE ---

st.divider()
st.subheader("Drafts")

if not st.session_state.drafts:
    st.info("No drafts yet. Add one above.")
else:
    for i, d in enumerate(st.session_state.drafts):
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 2])
            with c1:
                st.markdown(f"**{d['title']}**")
                st.caption((d["desc"][:120] + "…") if len(d["desc"]) > 120 else d["desc"])
                st.write(f"Price: ${d['price']:.2f} AUD | Qty: {d['quantity']}")
                if d["images"]:
                    st.caption(f"Images: {len(d['images'])}")
            with c2:
                if st.button("Edit", key=f"edit_{i}"):
                    st.session_state.edit_index = i
            with c3:
                if st.button("Delete", key=f"delete_{i}"):
                    st.session_state.drafts.pop(i)
                    save_drafts_to_file(st.session_state.drafts)
                    st.rerun()

# --- EDIT FORM ---
st.divider()
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    d = st.session_state.drafts[idx]
    st.subheader(f"Edit draft #{idx + 1}")

    with st.form("edit_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            e_title = st.text_input("Title", d["title"])
            e_desc = st.text_area("Description", d["desc"])
        with c2:
            e_price = st.number_input("Price (AUD)", min_value=0.0, value=float(d["price"]), step=1.0)
            e_quantity = st.number_input("Quantity", min_value=1, value=int(d["quantity"]), step=1)
        e_images = st.file_uploader("Replace images (optional)", accept_multiple_files=True)

        left, mid, right = st.columns(3)
        with left:
            save = st.form_submit_button("Save changes")
        with mid:
            cancel = st.form_submit_button("Cancel")

    if save:
        d["title"] = e_title.strip()
        d["desc"] = e_desc.strip()
        d["price"] = float(e_price)
        d["quantity"] = int(e_quantity)
        if e_images:
            d["images"] = e_images
        st.session_state.drafts[idx] = d
        save_drafts_to_file(st.session_state.drafts)
        st.session_state.edit_index = None
        st.success("Draft updated.")
        st.rerun()
    elif cancel:
        st.session_state.edit_index = None
        st.info("Edit canceled.")
        st.rerun()

st.caption("Step 2 complete! Next up: exporting these drafts to eBay AU using their API.")
