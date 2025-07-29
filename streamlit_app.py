import streamlit as st
import sqlite3
import bcrypt
import openai
import os

# --- Secure API Key Management ---
#openai.api_key = os.getenv("YOUR-API-KEY")  # Ensure to set this in your environment variables

#Set Page Configuration

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("user_data.db")
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Feedback table
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            feedback TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Authentication Functions ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def add_user(username, email, password):
    try:
        conn = sqlite3.connect("user_data.db")
        c = conn.cursor()
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                  (username, email, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(email, password):
    conn = sqlite3.connect("user_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user and verify_password(password, user[3]):
        return user
    return None

# --- Feedback Submission ---
def submit_feedback(username, feedback):
    conn = sqlite3.connect("user_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO feedback (username, feedback) VALUES (?, ?)", 
              (username, feedback))
    conn.commit()
    conn.close()

# --- Chatbot Functionality ---
def get_chatbot_response(query, history):
    prompt = "\n".join(history + [query])
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        reply = response.choices[0].text.strip()
        return reply
    except Exception as e:
        return f"Error: {e}"

# --- Power BI Embed ---
def embed_power_bi_report():
    
    # Create an interactive dropdown for navigation
    navigation_option = st.selectbox(
        "Choose a Dashboard View:",
        [
            "Homepage",
            "GDP",
            "Sectoral Contributions",
            "City-wise Patents",
            "City-wise Expenditure",
            "City-wise Employment Rates"
        ]
    )

    # Dictionary of Power BI report embed URLs for each section
    embed_urls = {
        "Homepage": "https://app.powerbi.com/reportEmbed?reportId=efc2043a-944b-4b0a-97c1-b6e88688aabb&autoAuth=true&ctid=b8593818-1c51-461d-ac9a-c1192e67c2dd",
        "GDP": "https://app.powerbi.com/reportEmbed?reportId=efc2043a-944b-4b0a-97c1-b6e88688aabb&autoAuth=true&ctid=b8593818-1c51-461d-ac9a-c1192e67c2dd",
        "Sectoral Contributions": "https://app.powerbi.com/reportEmbed?reportId=efc2043a-944b-4b0a-97c1-b6e88688aabb&autoAuth=true&ctid=b8593818-1c51-461d-ac9a-c1192e67c2dd",
        "City-wise Patents": "https://app.powerbi.com/reportEmbed?reportId=efc2043a-944b-4b0a-97c1-b6e88688aabb&autoAuth=true&ctid=b8593818-1c51-461d-ac9a-c1192e67c2dd",
        "City-wise Expenditure": "https://app.powerbi.com/reportEmbed?reportId=efc2043a-944b-4b0a-97c1-b6e88688aabb&autoAuth=true&ctid=b8593818-1c51-461d-ac9a-c1192e67c2dd",
        "City-wise Employment Rates": "https://app.powerbi.com/reportEmbed?reportId=efc2043a-944b-4b0a-97c1-b6e88688aabb&autoAuth=true&ctid=b8593818-1c51-461d-ac9a-c1192e67c2dd"
    }

    # Dictionary of descriptions for each section
    descriptions = {
        "Homepage": (
        "Welcome to the interactive Power BI Dashboard! This dynamic platform offers an in-depth view of city-wise economic data in India. "
        "Navigate through various sections to explore key insights, visualize trends, and gain a comprehensive understanding of India's evolving economy. "
        "Discover how cities are performing across economic, innovation, and employment metrics through intuitive visualizations."
    ),
    "GDP": (
        "This section presents a detailed comparative analysis of GDP trends across major Indian cities from 2020 to 2024. "
        "Uncover how top-performing cities are driving India's economic growth, identify patterns in GDP fluctuations, and assess regional economic disparities. "
        "Interactive graphs and year-on-year comparisons help you grasp each city's economic trajectory."
    ),
    "Sectoral Contributions": (
        "Delve into the economic structure of Indian cities by analyzing the contributions of key sectors—Agriculture, Industry, Services, and Technology—to their GDP. "
        "Understand the diversity in economic drivers for each city and see how sectoral strengths have evolved over time. "
        "This view helps pinpoint emerging sectors and areas of growth potential."
    ),
    "City-wise Patents": (
        "Explore the innovation landscape of India through city-wise patent metrics. "
        "This section showcases the number of patents filed per 100,000 inhabitants, reflecting each city's focus on research, creativity, and technological advancements. "
        "Gain insights into regional hubs of innovation and track their progress over time."
    ),
    "City-wise Expenditure": (
        "Analyze the financial commitment of Indian cities towards Research and Development (R&D). "
        "This section highlights the percentage of GDP allocated to R&D activities, showcasing the priority given to fostering innovation and technological breakthroughs. "
        "Identify cities leading the way in building a knowledge-driven economy."
    ),
    "City-wise Employment Rates": (
        "Understand the employment landscape across key sectors such as Information and Communication Technology (ICT), Small and Medium Enterprises (SMEs), and Tourism. "
        "This section provides insights into employment trends, including overall unemployment rates and youth unemployment statistics, offering a clear picture of workforce dynamics in each city. "
        "Interactive visualizations allow for sector-specific and city-wise analysis."
    )
    }

    # Display the description for the selected dashboard view
    st.markdown(f"**Description:** {descriptions.get(navigation_option, 'Explore detailed insights for the selected dashboard view.')}")

    # Embed the selected Power BI report view
    selected_url = embed_urls.get(navigation_option, embed_urls["Homepage"])
    st.markdown(f"""
        <iframe title="Power BI Report - {navigation_option}" width="100%" height="600" src="{selected_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

# --- Main Application ---
# Streamlit Page Configuration
st.set_page_config(page_title="IndiaCityGDP Dashboard", layout="wide", page_icon=":bar_chart:")

# Custom CSS Styling
st.markdown(
    """
    <style>
    /* General Background */
    body {
        background-color: #00000;  /* Soft pastel cream */
    }
    .sidebar .sidebar-content {
    background: linear-gradient(to bottom, #6a11cb, #2575fc); /* Gradient background */
    color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3); /* Add a shadow */
    }
    .sidebar .sidebar-content a {
    color: white; /* Links in white */
    font-weight: bold;
    text-decoration: none;
    }
    sidebar .sidebar-content a:hover {
    color: #f0e130; /* Highlight links on hover */
    }
    

    /* Header (Navigation Bar) Styling */
    .navbar {
        background: linear-gradient(90deg, #a8d5e2, #fcbad3, #f8df81);
        color: white;
        padding: 15px;
        text-align: center;
        font-size: 20px; /* Increased font size */
        font-weight: bold;
        border-radius: 8px;
    }

    /* Content Styling */
    .stMarkdown, .stTextInput, .stButton {
        font-size: 20px;  /* Increased font size for content */
    }

    /* Buttons Styling */
    .sign-in-btn, .save-btn {
        background-color: #ffc4d6;
        border: none;
        color: #333;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 24px; /* Increased font size */
        font-weight: bold;
        cursor: pointer;
        margin-left: 10px;
    }
    .sign-in-btn:hover, .save-btn:hover {
        background-color: #ffb3c1;
    }

    /* Chatbot Styling */
    .chatbot-container {
        background-color: #e4f9f5; /* Soft pastel mint */
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        color: #333;
        font-size: 18px; /* Increased font size */
    }
    
    /* Footer Styling */
    footer {
        background-color: #ffefd5; /* Light pastel peach */
        color: #3a3b3c;
        padding: 16px;  /* Increased padding */
        text-align: center;
        font-size: 18px; /* Increased font size */
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Navigation Bar
st.markdown('<div class="navbar">IndiaCityGDP Dashboard</div>', unsafe_allow_html=True)


# --- User Authentication ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.sidebar.header("Login or Signup")

    auth_choice = st.sidebar.radio("Choose an option", ["Login", "Signup"])
    
    if auth_choice == "Signup":
        st.sidebar.subheader("Create a new account")
        username = st.sidebar.text_input("Username")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Signup"):
            if add_user(username, email, password):
                st.sidebar.success("Signup successful! Please login.")
            else:
                st.sidebar.error("Error: Username or email already exists.")
    
    elif auth_choice == "Login":
        st.sidebar.subheader("Login to your account")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.user = user
                st.sidebar.success(f"Welcome, {user[1]}!")
                #st.write(f"**Account Created On:** {st.session_state.user[3]}")  # Replace with actual date
                #st.write(f"**Last Login:** {st.session_state.user[4]}")
            else:
                st.sidebar.error("Invalid email or password.")

else:
    st.sidebar.success(f"Logged in as {st.session_state.user[1]}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None

# --- Main Content ---
# --- Main Content ---
if st.session_state.user:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["About", "Dashboard", "Insights", "Chatbot", "Feedback", "Profile"])

    with tab1:  # About Page
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        st.markdown('<div class="chat-header" style="color: #00a1a1; font-size: 36px; font-weight: bold;">About</div>', unsafe_allow_html=True)

        st.markdown("""
    <div>
        <p>IndiaCityGDP is a comprehensive platform that visualizes and analyzes the economic landscapes of Indian cities. 
        Through insightful data representation and analytics, it enables a deeper understanding of urban economies, fostering strategic planning and sustainable development. 
        Our mission is to empower policymakers, researchers, businesses, 
        and citizens with actionable insights into the economic growth and potential of urban India.</p>
    </div>
    <hr style="border: 1px solid #ff69b4; margin: 20px 0;">

    <div>
        <h2 style="color: #008080; font-weight: bold;">Our Vision:</h2>
        <p>To be the go-to platform for exploring, analyzing, and understanding urban economic metrics in India, driving informed decision-making and fostering inclusive growth across cities.
        We envision a future where data empowers cities to thrive sustainably, with tailored strategies for economic resilience, innovation, and sectoral excellence.</p>
    </div>
    <hr style="border: 1px solid #ff69b4; margin: 20px 0;">

    <div>
    <h2 style="color: #008080; font-weight: bold;">Key Features:</h2>
    <ul style="font-size: 16px; line-height: 1.6;">
        <li><strong style="color: #004d40;">Interactive GDP Analysis:</strong> Visualize city-wise GDP trends from 2019 to 2024, identifying economic leaders and growth patterns across Indian cities.</li>
        <li><strong style="color: #004d40;">Sectoral Contributions Insights:</strong> Explore the impact of key sectors like Agriculture, Industry, Services, and Technology on city GDPs, highlighting areas of strength and growth potential.</li>
        <li><strong style="color: #004d40;">Innovation Metrics:</strong> Dive into the innovation ecosystem with data on patents filed per 100,000 inhabitants, showcasing creativity and technological progress in different cities.</li>
        <li><strong style="color: #004d40;">R&D Expenditure Analysis:</strong> Discover how cities allocate their GDP towards Research and Development, reflecting their commitment to fostering innovation and knowledge-driven growth.</li>
        <li><strong style="color: #004d40;">Employment Trends Visualization:</strong> Gain insights into employment rates across sectors such as ICT, SMEs, and Tourism, along with a focus on youth unemployment and overall workforce dynamics.</li>
    </ul>
    </div>
    <hr style="border: 1px solid #ff69b4; margin: 20px 0;">


    <div>
        <h2 style="color: #008080; font-weight: bold;">How We Engage:</h2>
        <ul style="font-size: 16px; line-height: 1.6;">
            <li><strong style="color: #004d40;">Policy Makers:</strong> Leverage detailed economic data to formulate policies that foster sustainable growth and equitable resource distribution.</li>
            <li><strong style="color: #004d40;">Business Leaders:</strong> Identify high-growth sectors and cities for expansion and investment opportunities.</li>
            <li><strong style="color: #004d40;">Citizens & Students:</strong> Understand how your city performs economically and contribute to informed civic discussions.</li>
            <li><strong style="color: #004d40;">Researchers & Analysts:</strong> Utilize accurate data for studies, reports, and presentations on urban development and economic dynamics..</li>
        </ul>
    </div>
    <hr style="border: 1px solid #ff69b4; margin: 20px 0;">
    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    
    with tab2:  # Dashboard Page
        st.subheader("Power BI Dashboard")
        embed_power_bi_report()

    with tab3:  # Insights Page
        st.subheader("Insights")
    
    # Introduction and Navigation
        st.markdown("""
        ### Key Insights
        - **City-Level GDP Data:** Compare the GDP contributions of major metro cities.
        - **Growth Trends:** Observe economic trends over time using the interactive dashboard.
        - **Sector Contributions:** Deep dive into the sectors contributing most to urban economies.
        - **Actionable Metrics:** Use data for policy-making, business expansion, or academic research.
    """)
        st.info("Use the filters below to explore tailored insights.")

    # Filters Section
        st.markdown("#### Filter Data for Specific Insights:")
        col1, col2, col3 = st.columns([1, 1, 1])

    # City Filter
        with col1:
            city_filter = st.multiselect(
            "Select Cities:",
            options=["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata"],
            default=["Mumbai", "Delhi"]
        )
    
    # Year Filter
        with col2:
           year_filter = st.slider(
            "Select Year Range:",
            min_value=2010,
            max_value=2024,
            value=(2018, 2024),
            step=1
        )
    
    # Sector Filter
        with col3:
            sector_filter = st.multiselect(
            "Select Sectors:",
            options=["Agriculture", "Industry", "Services", "Technology", "Tourism"],
            default=["Services", "Technology"]
        )
    
    # Apply Filters and Display Insights
        st.markdown("### Filtered Insights")
        st.write(f"Showing data for **{', '.join(city_filter)}** from **{year_filter[0]} to {year_filter[1]}**, focusing on sectors: **{', '.join(sector_filter)}**.")

    # Example Visualization (replace with actual Power BI or plotly visualizations)
        st.markdown("#### GDP Trends Over Time")
        st.line_chart({
        "Mumbai": [150, 160, 170, 180, 190],
        "Delhi": [140, 155, 165, 175, 185],
    })  # Replace this with actual filtered data.

   
    # Dynamic Cards for Key Insights
        st.markdown("### Key Takeaways")
        col4, col5 = st.columns(2)

        with col4:
            st.metric("Highest GDP Growth City", "Bangalore", delta="12.5%")
            st.metric("Most Innovative City", "Hyderabad", delta="300 patents/year")
    
        with col5:
            st.metric("Top Contributing Sector", "Technology", delta="5% Increase")
            st.metric("Average GDP Growth (2020-2024)", "7.8%", delta="Stable")

    # Interactive Call to Action
        st.success("💡 Tip: Use these insights to make informed decisions for your research or business strategies.")
        st.button("Export Insights as PDF")

    
    with tab4:  # Chatbot Page
        st.subheader("Chatbot")
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        user_query = st.text_input("Ask a question")
        if st.button("Submit Query") and user_query:
            chatbot_response = get_chatbot_response(user_query, st.session_state.conversation_history)
            st.session_state.conversation_history.append(f"You: {user_query}")
            st.session_state.conversation_history.append(f"Bot: {chatbot_response}")

        st.write("\n".join(st.session_state.conversation_history))
    
    with tab5:  # Feedback Page
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown('<div class="chat-header" style="color: #00a1a1; font-size: 36px; font-weight: bold;">Feedback for IndiaCityGDP Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("""
    <h2 style="color: #008080; font-weight: bold; font-size: 24px;">Rate Your Experience ⭐️</h2>
    <p style="font-size: 16px;">How would you rate your experience with IndiaCityGDP Dashboard? Please select a rating below:</p>
    """, unsafe_allow_html=True)
        rating = st.slider("Rate your experience:", 1, 5)
        st.markdown(f"<p style='font-size: 24px; color: #008080;'>Rating: {'⭐️' * rating}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("""
    <h2 style="color: #008080; font-weight: bold; font-size: 24px;">Your Feedback 💬</h2>
    <p style="font-size: 16px;">Please share any comments, suggestions, or issues you encountered:</p>
    """, unsafe_allow_html=True)
        user_feedback = st.text_area("", height=150)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("""
        <h2 style="color: #008080; font-weight: bold; font-size: 24px;">Contact Information📧</h2>
        """, unsafe_allow_html=True)
        user_email = st.text_input("Enter your email")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        submit_button = st.button("Submit Feedback")
        if submit_button:
            if user_feedback:
                st.success("Thank you for your feedback! 😊")
                with open("feedback.txt", "a") as file:
                    file.write(f"Rating: {rating}\nFeedback: {user_feedback}\nEmail: {user_email if user_email else 'N/A'}\n\n")
            else:
                st.warning("Please provide feedback before submitting. ⚠️")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown("""
    <div class="response-box">
        <h2 style="color: #008080; font-weight: bold; font-size: 24px;">Get in Touch 📱</h2>
        <p>If you'd like to connect with me, feel free to reach out on LinkedIn or send an email!</p>
        <ul>
            <li><a href="https://www.linkedin.com/in/harshini-shivaratri" style="color: #008080;">LinkedIn</a>🔗</li>
            <li><a href="mailto:harshinishivaratri586@gmail.com" style="color: #008080;">harshinishivaratri586@gmail.com</a> 📧</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab6:
        st.markdown("""
<style>
    

    .profile-sidebar {
        width: 25%;
        background-color: #fff;
        border-radius: 10px;
        text-align: center;
        color: #333;
        padding: 20px;
    }

    .profile-sidebar img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        margin-bottom: 15px;
    }

    .profile-sidebar h3 {
        margin: 10px 0;
        color: #5e2b82;
    }

    .profile-sidebar p {
        color: #555;
        font-size: 14px;
    }

    .profile-details {
        width: 70%;
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        color: #333;
    }

    .profile-details h3 {
        color: #6a11cb;
        margin-bottom: 15px;
    }

    .profile-details .form-field {
        margin-bottom: 15px;
    }

    .profile-details label {
        font-size: 14px;
        font-weight: bold;
    }

    .profile-details input {
        width: 100%;
        padding: 8px;
        margin-top: 5px;
        border-radius: 5px;
        border: 1px solid #ccc;
    }

    .save-btn {
        margin-top: 15px;
        background-color: #6a11cb;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .save-btn:hover {
        background-color: #2575fc;
    }
    </style>
        """, unsafe_allow_html=True)

# Layout with sidebar and details
        st.markdown('<div class="profile-container">', unsafe_allow_html=True)

# Sidebar Section
        st.markdown('<div class="profile-sidebar">', unsafe_allow_html=True)
        st.image("https://via.placeholder.com/120", caption="Profile Picture")  # Replace with user's image path
        st.markdown(f"<h3>{st.session_state.user[1]}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{st.session_state.user[2]}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Details Section
        st.markdown('<div class="profile-details">', unsafe_allow_html=True)
        st.markdown('<h3>Profile Settings</h3>', unsafe_allow_html=True)

        with st.form(key='profile_form'):
    # Input fields
            first_name = st.text_input("First Name", placeholder="Enter your first name")
            last_name = st.text_input("Last Name", placeholder="Enter your last name")
            phone = st.text_input("Mobile Number", placeholder="Enter phone number")
            email = st.text_input("Email ID", value=st.session_state.user[2])
            address1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
            address2 = st.text_input("Address Line 2", placeholder="Enter address line 2")
            city = st.text_input("City", placeholder="Enter city")
            state = st.text_input("State", placeholder="Enter state")
            country = st.text_input("Country", placeholder="Enter country")

    # Save button
            submit_button = st.form_submit_button(label="Save Profile", type="primary")

        if submit_button:
            st.success("Profile updated successfully!")

        st.markdown('</div>', unsafe_allow_html=True)

# Close main layout div
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer Section
        st.markdown(
        """
        <hr style="border:1px solid #ddd;">
        <div style="text-align: center; color: #888; font-size: 14px;">
        © 2025 User Dashboard - All rights reserved
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("Please log in to access the application.")


# --- Custom CSS ---
st.markdown("""
    <style>
    body { background-color: #f5f5f5; }
    .stButton>button { background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <footer>
        <div style="background-color: #ffefd5; padding: 18px; border-radius: 5px;">
            <strong>Contact Me:</strong>  
            <br>
            <strong>Email:</strong>  harshinishivaratri586@gmail.com | <strong>Phone:</strong>  +91234567890
            <br>
            © 2025 IndiaCityGDP Dashboard
        </div>
    </footer>
    """,
    unsafe_allow_html=True,
)

