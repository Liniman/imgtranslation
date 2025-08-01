import streamlit as st

st.title("🎉 Streamlit is Working!")
st.write("If you can see this, Streamlit is running correctly.")

if st.button("Test Button"):
    st.success("Button clicked! Everything works!")
    
st.info("Now let's try the real app...")