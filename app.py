# app.py

import streamlit as st
import pandas as pd
from advisory_bot import recommend_electives

# Load your merged_df (Excel file)
@st.cache_data
def load_data():
    return pd.read_excel("merged_df.xlsx")

# Streamlit UI setup
st.set_page_config(page_title="Student Advisory BOT", page_icon="🎓")
st.title("🎓 Academic Advisory BOT")
st.markdown("Welcome! Ask me for **personalized elective recommendations** based on your academic history.")

# Input: Student Name
student_name = st.text_input("Enter your full name")

# Trigger button
if st.button("Get Recommendations"):
    if student_name.strip() == "":
        st.warning("Please enter a valid name.")
    else:
        merged_df = load_data()
        result = recommend_electives(student_name, merged_df)

        if result["status"] == "not_found":
            st.error(result["student_summary"])
        else:
            st.markdown("### 👤 Student Profile")
            
            # Extract student profile info from summary string
            profile = result["student_summary"]
            # Optional cleanup to split nicely (based on your format)
            for part in profile.split(" "):
                if "👤" in part:
                    st.markdown(f"- {part} {profile.split('👤')[-1].split('🆔')[0].strip()}")
                elif "🆔" in part:
                    st.markdown(f"- {part} {profile.split('🆔')[-1].split('🎓')[0].strip()}")
                elif "🎓" in part:
                    st.markdown(f"- {part} {profile.split('🎓')[-1].split('📊')[0].strip()}")
                elif "📊" in part:
                    st.markdown(f"- {part} {profile.split('📊')[-1].strip()}")

            st.markdown("### 📚 Subjects Taken")
            st.dataframe(pd.DataFrame(result["subjects"]))

            st.markdown("### ✅ Recommended Electives")
            for rec in result["recommendations"]:
                st.success(f"""
**{rec['title']}** ({rec['module']})  
🕒 **Time**: {rec['time']}  
📅 **Days**: {rec['days']}
""")

            st.markdown("Electives suggested based on your academic background and interests!")
