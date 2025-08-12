import streamlit as st

st.title("Label Template Uploader")

uploaded_template = st.file_uploader("Upload your template file", type=["pdf", "png", "jpg", "svg"])

if uploaded_template is not None:
    st.success("Template uploaded successfully!")
    
    # যদি image হয় তাহলে preview দেখাও
    if uploaded_template.type.startswith("image"):
        st.image(uploaded_template, caption="Uploaded Template", use_container_width=True)
    else:
        st.write("PDF/SVG uploaded. Ready for processing.")
