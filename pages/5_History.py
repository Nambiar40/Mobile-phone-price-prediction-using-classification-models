import streamlit as st
import pandas as pd
from db_utils import get_search_history

st.set_page_config(page_title="History", page_icon="🕒", layout="wide")

st.title("🕒 Search History")
st.markdown("View your recent predictions, OCR scans, and price tracking history.")

try:
    history = get_search_history(limit=50)
    
    if not history:
        st.info("No history found. Try making some predictions!")
    else:
        # Convert to DataFrame for a nice table display
        df = pd.DataFrame(history)
        
        # Reorder and rename columns if they exist
        if all(col in df.columns for col in ["date", "type", "brand", "model_name", "price"]):
            df = df[["date", "type", "brand", "model_name", "price"]]
            df.columns = ["Date & Time", "Prediction Type", "Brand / Platform", "Model / Item", "Predicted Price"]
        
        # Display dataframe as a table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
except Exception as e:
    st.error(f"Database error: {e}")
