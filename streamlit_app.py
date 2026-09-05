import streamlit as st

st.set_page_config(
    page_title="Dashboard - Phone Price Prediction",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Phone Price Prediction Dashboard")
st.markdown("### Predict mobile prices using Artificial Intelligence")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.info("### 📊 Current Market Price\nPredict current market price of a mobile phone using its specifications.")
    if st.button("Open Current Price Model", use_container_width=True, key="btn_current"):
        st.switch_page("pages/1_Current_Price.py")

    st.success("### 💰 Resale Price Prediction\nPredict resale value of a mobile phone using its specifications and condition.")
    if st.button("Open Resale Price Model", use_container_width=True, key="btn_resale"):
        st.switch_page("pages/2_Resale_Price.py")

with col2:
    st.error("### 📸 OCR Price Prediction\nUpload a mobile phone invoice to extract details using OCR and predict the price range.")
    if st.button("Open OCR Scanner", use_container_width=True, key="btn_ocr"):
        st.switch_page("pages/3_OCR_Scanner.py")

    st.warning("### 📈 Price Tracker\nTrack the price history and trends of mobile phones on Amazon.")
    if st.button("Open Price Tracker", use_container_width=True, key="btn_tracker"):
        st.switch_page("pages/4_Price_Tracker.py")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Phone Price Prediction System &bull; Powered by AI</p>", unsafe_allow_html=True)
