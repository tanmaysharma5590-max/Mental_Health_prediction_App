import streamlit as st
import requests
import plotly.graph_objects as go

# ---------- Page Config ----------
st.set_page_config(
    page_title="Signal — Mental Health Reading",
    page_icon="🌙",
    layout="wide"
)

# ---------- API URL ----------
# Local testing: FastAPI runs on your machine
# Deployed: set this in Streamlit Cloud -> Settings -> Secrets as:
#   API_URL = "https://your-fastapi-backend-url.com/predict"
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = "http://127.0.0.1:8000/predict"

# ---------- Theme (CSS) ----------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,500;0,600;1,500&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root{
    --coal:#040a16; --panel:#081428; --field:#0d1c34; --field-border:#1c3a5e;
    --field-border-focus:#d9a441; --cream:#f4efe4; --cream-dim:#b7c0cc;
    --muted:#7f93a5; --gold:#d9a441; --gold-bright:#f0c060; --amber-soft:#e8c98a;
    --danger:#e0704f;
}

.stApp{
    background:
        radial-gradient(1200px 800px at 15% -10%, #0f2444 0%, transparent 55%),
        radial-gradient(900px 700px at 110% 10%, #0a1c38 0%, transparent 50%),
        var(--coal);
    font-family:'Inter', sans-serif;
    color: var(--cream);
}

/* Hide default streamlit chrome */
#MainMenu, header, footer {visibility:hidden;}

.eyebrow{
    font-family:'IBM Plex Mono', monospace;
    font-size:12px; letter-spacing:0.14em; text-transform:uppercase;
    color: var(--gold); margin-bottom:6px;
}
.headline{
    font-family:'Fraunces', serif; font-weight:500;
    font-size:38px; line-height:1.1; color:var(--cream); margin-bottom:8px;
}
.headline em{ font-style:italic; font-weight:300; color:var(--amber-soft); }
.sub{ color:var(--muted); font-size:14.5px; line-height:1.6; max-width:52ch; margin-bottom:28px; }

.section-title{
    font-family:'Fraunces', serif; font-size:17px; font-weight:500;
    color:var(--cream); margin: 6px 0 2px;
    display:flex; align-items:center; gap:10px;
}
.section-num{
    font-family:'IBM Plex Mono', monospace; font-size:11px; color:var(--coal);
    background:var(--gold); padding:2px 6px; border-radius:3px;
}

/* Inputs */
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
.stNumberInput input,
.stTextInput input{
    background: var(--field) !important;
    border: 1.5px solid var(--field-border) !important;
    color: var(--cream) !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] > div:hover,
.stNumberInput input:hover, .stTextInput input:hover{
    border-color:#2c5688 !important;
}
div[data-baseweb="select"] span{ color: var(--cream) !important; }
label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stSlider label{
    color: var(--cream-dim) !important; font-size:13px !important; font-weight:500 !important;
}

/* Radio (stress level) styled as pills */
div[role="radiogroup"]{ gap:8px; }
div[role="radiogroup"] label{
    background: var(--field) !important;
    border: 1.5px solid var(--field-border) !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    color: var(--cream-dim) !important;
}

/* Button */
.stButton>button{
    width:100%;
    background: linear-gradient(180deg, var(--gold-bright), var(--gold));
    color:#241a06; font-weight:700; font-size:15px;
    border:none; border-radius:10px; padding:14px;
    box-shadow: 0 10px 30px rgba(217,164,65,0.22);
}
.stButton>button:hover{ transform:translateY(-1px); }

/* Result panel — targets the real Streamlit container (key="result_panel")
   instead of an unclosed raw <div>, so everything actually nests inside it */
div[class*="st-key-result_panel"]{
    background: linear-gradient(180deg, #0a1e3a 0%, #050e1e 100%) !important;
    border-radius: 18px !important;
    padding: 36px 28px !important;
    border: 1px solid #16304f !important;
    min-height: 560px !important;
    display:flex !important; flex-direction:column !important;
    align-items:center !important; justify-content:center !important;
    text-align:center;
}
div[class*="st-key-result_panel"] .stPlotlyChart{ width:100% !important; }

.result-eyebrow{
    font-family:'IBM Plex Mono', monospace; font-size:12px; letter-spacing:0.16em;
    text-transform:uppercase; color:var(--muted); margin-bottom: 4px;
}
.score-tagline{
    font-family:'Fraunces', serif; font-size:20px; font-weight:500;
    color:var(--cream); max-width:30ch; margin: 10px auto 6px;
}
.score-detail{ font-size:13.5px; color:var(--muted); max-width:34ch; line-height:1.6; margin:0 auto; }
.placeholder-icon{ font-size:34px; margin-bottom:14px; opacity:0.85; }
.placeholder-copy{
    font-family:'Fraunces', serif; font-style:italic; font-size:20px;
    color:var(--amber-soft); max-width:27ch; margin: 4px auto 10px;
    line-height:1.4;
}
.placeholder-sub{ font-size:13.5px; color:var(--muted); max-width:32ch; line-height:1.7; margin:0 auto; }
.footnote{ font-size:11px; color:#5c7590; line-height:1.5; margin-top:24px; max-width:36ch; }
hr{ border-color:#16304f !important; }
</style>
""", unsafe_allow_html=True)

# ---------- Layout ----------
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown('<p class="eyebrow">Habit-based reading</p>', unsafe_allow_html=True)
    st.markdown('<p class="headline">Read your <em>signal.</em></p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub">Answer honestly about your day-to-day habits. The model looks for '
        'patterns across students with similar routines — not a diagnosis, a reading.</p>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title"><span class="section-num">01</span> Profile</div>', unsafe_allow_html=True)
    name = st.text_input("Name", value="Tanmay Sharma")
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", min_value=10, max_value=100, value=20)
    with c2:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with c3:
        country = st.text_input("Country", value="India")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="section-num">02</span> Academic &amp; digital habits</div>', unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        academic_level = st.selectbox("Academic level", ["High School", "Undergraduate", "Graduate"])
        purpose_of_use = st.selectbox("Primary purpose", ["Entertainment", "Networking", "Education", "News"])
        daily_unlocks = st.number_input("Daily phone unlocks", min_value=0, value=50)
    with c5:
        most_used_platform = st.selectbox(
            "Most-used platform",
            ['Instagram', 'YouTube', 'TikTok', 'Facebook', 'Snapchat', 'Twitter',
             'WhatsApp', 'WeChat', 'LinkedIn', 'LINE', 'KakaoTalk', 'VKontakte']
        )
        avg_daily_usage_hours = st.number_input("Avg. daily screen time (hrs)", min_value=0.0, max_value=24.0, value=3.0, step=0.5)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="section-num">03</span> Lifestyle &amp; stress</div>', unsafe_allow_html=True)
    c6, c7, c8 = st.columns(3)
    with c6:
        study_hours = st.number_input("Study hours / day", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
    with c7:
        physical_activity_hours = st.number_input("Physical activity / day (hrs)", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
    with c8:
        sleep_hours_per_night = st.number_input("Sleep / night (hrs)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)

    stress_level = st.radio("Perceived stress level", ["Low", "Medium", "High", "Very High"], horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.button("Read my signal")


# ---------- Result rendering helpers ----------
def render_idle():
    with st.container(key="result_panel"):
        st.markdown('<div class="placeholder-icon">🌙</div>', unsafe_allow_html=True)
        st.markdown('<p class="result-eyebrow">Predicted reading</p>', unsafe_allow_html=True)
        st.markdown('<p class="placeholder-copy">Your signal is waiting to be read.</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="placeholder-sub">Fill in your habits on the left and submit — '
            'we\'ll turn them into a 0–10 reading, with a short note on what it means for you.</p>',
            unsafe_allow_html=True
        )


def render_result(score, display_name=""):
    display_name = display_name.strip() if display_name else ""
    greeting = f"{display_name}, y" if display_name else "Y"

    if score >= 7:
        tag = "Signal reads steady."
        detail = f"{greeting}our habits line up with the patterns of students reporting stronger wellbeing. Keep the routine that's working."
    elif score >= 4:
        tag = "Signal reads mixed."
        detail = f"{greeting}our habits show a mixed picture. Sleep, screen time, or stress may be worth adjusting first."
    else:
        tag = "Signal reads strained."
        detail = f"{greeting}our habits line up with patterns of higher reported strain. Consider easing screen time and protecting sleep — and reach out to someone if it helps."

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": " /10", "font": {"size": 42, "color": "#f4efe4", "family": "Fraunces"}},
        gauge={
            "axis": {"range": [0, 10], "tickcolor": "#7f93a5", "tickfont": {"color": "#7f93a5", "size": 10}},
            "bar": {"color": "#d9a441", "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [{"range": [0, 10], "color": "#0d1c34"}],
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=10),
        height=260,
        font={"color": "#f4efe4"}
    )

    with st.container(key="result_panel"):
        eyebrow_text = f"Predicted reading — {display_name}" if display_name else "Predicted reading"
        st.markdown(f'<p class="result-eyebrow">{eyebrow_text}</p>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<p class="score-tagline">{tag}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-detail">{detail}</p>', unsafe_allow_html=True)


def render_error(title, detail=""):
    with st.container(key="result_panel"):
        st.markdown('<p class="result-eyebrow">Error</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="placeholder-copy">{title}</p>', unsafe_allow_html=True)
        if detail:
            st.markdown(f'<p class="placeholder-sub">{detail}</p>', unsafe_allow_html=True)


with right:
    if submitted:
        payload = {
            "age": age,
            "gender": gender,
            "country": country,
            "academic_level": academic_level,
            "most_used_platform": most_used_platform,
            "purpose_of_use": purpose_of_use,
            "avg_daily_usage_hours": avg_daily_usage_hours,
            "daily_unlocks": daily_unlocks,
            "study_hours": study_hours,
            "physical_activity_hours": physical_activity_hours,
            "sleep_hours_per_night": sleep_hours_per_night,
            "stress_level": stress_level
        }

        try:
            with st.spinner("Reading your signal…"):
                response = requests.post(API_URL, json=payload, timeout=15)

            if response.status_code == 200:
                score = response.json()["predicted_mental_health_score"]
                render_result(score, name)
            else:
                render_error(f"API Error {response.status_code}", response.text)

        except requests.exceptions.ConnectionError:
            render_error(
                "Can't reach the server.",
                "Make sure your FastAPI backend is running and API_URL is set correctly."
            )
        except Exception as e:
            render_error("Something went wrong.", str(e))
    else:
        render_idle()

    st.markdown(
        '<p class="footnote">This reading is an estimate from a habits-based model, not a clinical diagnosis. '
        'If you\'re struggling, talking to a counsellor or someone you trust is always worth doing.</p>',
        unsafe_allow_html=True
    )