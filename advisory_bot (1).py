# advisory_bot.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample electives list (you can expand/replace this)
electives_df = pd.DataFrame({
    'course_title_long': [
        "Principles of Managerial Accounting", "Principles of Macroeconomics", "Principles of Finance",
        "Operations Management", "Applied Management Science", "Database Management Systems",
        "Introduction to Digital Forensics", "Business Research Methods", "Consumer Protection Law",
        "Communication Skills in English II", "Primary Rights in Rem and Accessory Real Rights in Rem",
        "Introduction to Information and Digital Technology", "Labour Law and Social Securities Law",
        "Communication Theories", "Case Studies in PR and Advertising", "PR Media Production",
        "Introduction to Entrepreneurship", "Math for Life", "Bioinformatics", "Cancer Biology I",
        "Introduction to Aeronautics", "UAE and GCC Society", "Pre-Calculus", "General Science",
        "Technical Communication for Work Place", "Genome Biology", "Principles of Medical Genetics",
        "Accounting Information Systems", "Cost Accounting", "Artificial Intelligence for Engineers",
        "Cross-platform Mobile Application Develop.", "Calculus I", "Probability and Stochastic Processes",
        "Project Scheduling and Time Management", "Project Costing and Financial Management",
        "Leadership and Communication", "Methods of Teaching Math", "Business Ethics and Corporate Governance"
    ],
    'module': [
        "Accounting", "Economics", "Finance", "Operations", "Management", "IT & Systems",
        "Cybersecurity", "Research", "Law", "Communication", "Law", "IT & Systems", "Law",
        "Communication", "Advertising", "Media", "Entrepreneurship", "Mathematics", "Biotech",
        "Biotech", "Engineering", "Sociology", "Mathematics", "General Science", "Communication",
        "Biotech", "Biotech", "Accounting", "Accounting", "Engineering", "App Development",
        "Mathematics", "Mathematics", "Project Management", "Finance", "Leadership", "Education", "Business Ethics"
    ]
})

def recommend_electives(student_name, merged_df):
    result = {"status": "success", "student_summary": "", "subjects": [], "recommendations": []}

    student_data = merged_df[merged_df['name_display'].str.strip().str.lower() == student_name.strip().lower()]
    
    if student_data.empty:
        result["status"] = "not_found"
        result["student_summary"] = "❌ Student not found in the records."
        return result

    std_id = student_data['emplid'].iloc[0]
    academic_program = student_data['acad_prog'].iloc[0]
    gpa = student_data['cum_gpa'].iloc[0] if 'cum_gpa' in student_data.columns else 'N/A'

    result["student_summary"] = (
        f"👤 **Name**: {student_name}\n"
        f"🆔 **Student ID**: {std_id}\n"
        f"🎓 **Academic Program**: {academic_program}\n"
        f"📊 **Cumulative GPA**: {gpa}"
    )

    subjects_taken = student_data[['course_title_long', 'subject_x', 'crse_grade_off']].drop_duplicates().reset_index(drop=True)
    result["subjects"] = subjects_taken.to_dict(orient="records")

    taken_courses_set = set(subjects_taken['course_title_long'].str.strip().str.lower())
    eligible_electives = electives_df[~electives_df['course_title_long'].str.strip().str.lower().isin(taken_courses_set)].copy()

    taken_subjects_text = ' '.join(subjects_taken['course_title_long'].dropna().tolist())
    elective_texts = eligible_electives['course_title_long'].tolist()

    corpus = [taken_subjects_text] + elective_texts
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    eligible_electives['similarity_score'] = similarity_scores.round(2)

    if "LAW" in academic_program.upper():
        eligible_electives = eligible_electives[eligible_electives['module'].str.contains("Law", case=False)]

    top_electives = eligible_electives.sort_values(by='similarity_score', ascending=False).head(5)

    for _, row in top_electives.iterrows():
        title = row['course_title_long']
        module = row['module']
        schedule_data = merged_df[merged_df['course_title_long'].str.strip().str.lower() == title.strip().lower()]

        if not schedule_data.empty:
            sched_row = schedule_data.iloc[0]
            days = [d.capitalize() for d in ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
                    if str(sched_row[d]).strip().upper() == 'Y']
            time_info = f"{sched_row['mtg_start']} - {sched_row['mtg_end']}" if pd.notna(sched_row['mtg_start']) else "TBA"
            day_str = ', '.join(days) if days else "TBA"
        else:
            time_info = "TBA"
            day_str = "TBA"

        result["recommendations"].append({
            "title": title,
            "module": module,
            "days": day_str,
            "time": time_info,
            "score": row["similarity_score"]
        })

    return result
