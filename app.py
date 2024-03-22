import streamlit as st
import requests
import base64

def clear_ui():
    for _ in range(10):
        st.empty()

def display_resume_data(data, uploaded_file):
    # Display the uploaded CV in an iframe
    file_bytes = uploaded_file.getvalue()
    b64 = base64.b64encode(file_bytes).decode()
    if ".pdf" in uploaded_file.name:
        pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error("Unsupported file format. Please upload a PDF file.")

    resume = data.get("Resume", {})
    structured_resume = resume.get("StructuredResume", {})
    
    # PII and LinkedIn
    contact_method = structured_resume.get("ContactMethod", {})
    person_name = structured_resume.get("PersonName", {})
    linkedin = structured_resume.get("LinkedIn", "")
    st.subheader("Personal Information and LinkedIn")
    st.write(f"Name: {person_name.get('FormattedName', 'Not Available')}")
    st.write(f"Email: {contact_method.get('InternetEmailAddress_main', 'Not Available')}")
    st.write(f"LinkedIn: {linkedin}")
    
    # Employment History
    employment_history = structured_resume.get("EmploymentHistory", [])
    if employment_history:
        st.subheader("Employment History")
        for job in employment_history:
            st.write(f"Title: {', '.join(job.get('Title', []))}")
            st.write(f"Employer: {job.get('EmployerOrgName', 'Not Available')}")
            st.write(f"Description: {job.get('Description', 'Not Available')}")
            st.write(f"Start Date: {job.get('StartDate', 'Not Available')} - End Date: {job.get('EndDate', 'Not Available')}")
            st.write("-----")
    
    # Skills
    skills = structured_resume.get("Skills", [])
    if skills:
        st.subheader("Skills")
        st.write(", ".join(skills))
    
    # Other Links
    if "InternetWebAddress" in contact_method and contact_method["InternetWebAddress"]:
        st.subheader("Other Links")
        for link in contact_method["InternetWebAddress"]:
            st.write(link)

def upload_file_and_parse():
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])
    if uploaded_file is not None:
        clear_ui()
        try:
            files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
            headers = {'Authorization': f'Token {st.secrets["API_SECRET"]}'}
            response = requests.post(st.secrets["API_URL"], files=files, headers=headers)
            response.raise_for_status()  # Raises a HTTPError if the response status code is 4XX/5XX
            data = response.json()
            display_resume_data(data, uploaded_file)
        except requests.exceptions.HTTPError as http_err:
            st.error(f"HTTP error occurred: {http_err} - {response.text}")
        except Exception as err:
            st.error(f"An error occurred: {err}")

st.title("CV Parser")
upload_file_and_parse()
