from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# If the file is started with "python app.py" or VS Code's Run button, relaunch it through Streamlit
if __name__ == "__main__":
    from streamlit import runtime
    if not runtime.exists():
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", str(Path(__file__).resolve())]
        sys.exit(stcli.main())

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Internet Usage Dashboard",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).parent

# Colours (validated for colour-blind separation on the dark navy surface)
BLUE, ORANGE, AQUA, YELLOW = "#3987e5", "#d95926", "#199e70", "#c98500"
VIOLET, MAGENTA = "#9085e9", "#d55181"
SURFACE, CARD, GRID = "#0b1220", "#111a2e", "#23304a"
TEXT1, TEXT2, MUTED = "#f0efec", "#c3c8d4", "#8a94a8"
GENDER_COLOURS = {"Female": BLUE, "Male": ORANGE, "Other": AQUA}

# ---------------------------------------------------------------------------
# Survey structure (same as the notebook)
# ---------------------------------------------------------------------------
COLUMN_NAMES = [
    "gender", "age_group", "device", "purpose",
    "total_hours", "academic_hours", "social_hours", "entertainment_hours",
    "spend_more_time_than_intended", "online_morning_to_night",
    "internet_essential_for_routine", "restless_without_internet",
    "use_for_assignments", "internet_helps_find_resources",
    "use_collaboration_platforms", "more_research_than_nonacademic",
    "social_media_first", "social_media_largest_share",
    "communicate_with_friends", "urge_to_check_notifications",
    "stream_video_music", "gaming_major_portion",
    "browsing_is_relaxation", "background_streaming",
    "easy_to_balance_study", "usage_helps_performance",
    "distracted_from_study", "want_to_reduce_screen_time",
]
HOURS_COLS = ["total_hours", "academic_hours", "social_hours", "entertainment_hours"]
LIKERT_COLS = COLUMN_NAMES[8:]
HOURS_MAP = {
    "Less than 1 hour": 0.5,
    "1 - 2 hours": 1.5,
    "2 - 3 hours": 2.5,
    "3 - 4 hours": 3.5,
    "4 - 5 hours": 4.5,
    "More than 5 hours": 5.5,
}
HOUR_BAND_LABELS = {0.5: "<1 h", 1.5: "1–2 h", 2.5: "2–3 h", 3.5: "3–4 h", 4.5: "4–5 h", 5.5: ">5 h"}
LIKERT_MAP = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}

HOURS_LABELS = {
    "total_hours": "Total internet",
    "academic_hours": "Academic / learning",
    "social_hours": "Social media & communication",
    "entertainment_hours": "Entertainment & gaming",
}
DEVICE_COLS = {
    "uses_smartphone": "Smartphone",
    "uses_laptop_desktop": "Laptop / Desktop",
    "uses_tablet": "Tablet",
    "uses_other_device": "Other",
}
PURPOSE_COLS = {
    "purpose_academic": "Academic learning / research",
    "purpose_social_media": "Social media & networking",
    "purpose_entertainment": "Entertainment / streaming / gaming",
    "purpose_communication": "Communication",
    "purpose_other": "Other",
}
GENDER_ORDER = ["Female", "Male", "Other"]
AGE_ORDER = ["Under 18", "18 - 20", "21 - 23", "24 or above"]
DEVICE_GROUP_ORDER = ["Smartphone only", "Smartphone + Laptop", "Other combination"]
GROUP_OPTIONS = {"Gender": ("gender", GENDER_ORDER), "Age group": ("age_group", AGE_ORDER),
                 "Device group": ("device_group", DEVICE_GROUP_ORDER)}

RAW_FILE_NAMES = ["Student Daily Internet.csv", "Student_Daily_Internet.csv"]
CLEAN_FILE_NAMES = ["cleaned_student_internet_data.csv"]



# ---------------------------------------------------------------------------
# Built-in survey data (cleaned, 98 students) - used when no CSV file is found
# ---------------------------------------------------------------------------
EMBEDDED_CSV = """respondent_id,gender,age_group,device,purpose,total_hours,academic_hours,social_hours,entertainment_hours,spend_more_time_than_intended,online_morning_to_night,internet_essential_for_routine,restless_without_internet,use_for_assignments,internet_helps_find_resources,use_collaboration_platforms,more_research_than_nonacademic,social_media_first,social_media_largest_share,communicate_with_friends,urge_to_check_notifications,stream_video_music,gaming_major_portion,browsing_is_relaxation,background_streaming,easy_to_balance_study,usage_helps_performance,distracted_from_study,want_to_reduce_screen_time
1,Female,21 - 23,Smartphone,Academic Learning / Research,5.5,4.5,5.5,5.5,5,5,4,4,4,5,4,3,4,3,3,3,4,3,3,4,3,3,4,4
2,Female,21 - 23,Smartphone,Entertainment / Streaming / Gaming,5.5,3.5,5.5,5.5,5,4,4,4,4,4,4,4,4,4,4,5,5,3,4,2,4,3,5,5
3,Male,21 - 23,Smartphone,Social Media & Networking,4.5,1.5,2.5,4.5,3,2,3,4,2,2,3,3,4,2,3,3,2,2,2,2,2,2,3,3
4,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,4.5,5.5,4.5,3,2,3,2,3,5,3,3,3,3,3,3,3,3,3,3,3,3,3,3
5,Female,21 - 23,Smartphone; Laptop / Desktop,Academic Learning / Research,3.5,1.5,2.5,1.5,4,1,3,3,3,5,4,3,3,3,4,2,4,2,3,4,4,3,2,3
6,Female,21 - 23,Other combination,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,2.5,5.5,5.5,2,1,2,1,1,2,2,1,2,2,2,1,1,1,1,1,1,1,1,1
7,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,1.5,3.5,2.5,5,5,4,4,5,5,3,3,5,3,5,4,4,4,5,5,5,5,4,5
8,Female,24 or above,Smartphone,"Academic Learning / Research; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",3.5,2.5,3.5,2.5,3,3,3,3,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
9,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,1.5,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
10,Female,24 or above,Smartphone,Academic Learning / Research,5.5,3.5,5.5,1.5,3,4,3,2,5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4
11,Female,18 - 20,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,3.5,4.5,1.5,3,2,2,2,5,5,4,5,2,2,2,1,3,1,2,3,3,3,2,4
12,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",4.5,4.5,3.5,2.5,3,4,3,3,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3
14,Female,21 - 23,Other combination,Social Media & Networking,4.5,1.5,3.5,1.5,5,3,4,4,3,3,3,3,3,3,3,3,5,2,2,3,2,3,5,5
15,Male,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,3.5,3.5,3.5,3,4,4,2,4,4,5,3,2,4,4,2,4,2,4,4,4,4,2,4
16,Female,21 - 23,Smartphone,Academic Learning / Research; Social Media & Networking,3.5,3.5,3.5,4.5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
17,Female,18 - 20,Smartphone,Academic Learning / Research,4.5,2.5,1.5,2.5,4,4,4,4,4,4,4,4,4,4,5,4,4,4,4,4,4,4,4,4
18,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,2.5,3.5,2.5,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
19,Female,21 - 23,Smartphone,Entertainment / Streaming / Gaming,4.5,3.5,4.5,3.5,5,5,4,4,4,5,5,3,5,4,4,4,5,4,4,4,5,5,4,4
20,Female,18 - 20,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,3.5,5.5,2.5,4,4,3,2,4,4,2,2,2,3,3,2,3,4,3,3,3,2,2,2
21,Male,24 or above,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,5.5,3.5,5.5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
22,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,4.5,5.5,5.5,4,4,5,3,4,5,4,3,2,3,4,2,2,3,4,3,3,4,3,3
23,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,1.5,2.5,5,4,4,4,5,5,4,3,4,3,3,3,3,4,4,5,4,4,4,5
24,Female,18 - 20,Smartphone,Academic Learning / Research,4.5,2.5,3.5,1.5,4,3,5,3,5,5,5,5,3,4,3,4,4,4,4,4,3,4,4,4
26,Female,21 - 23,Smartphone,Social Media & Networking,5.5,2.5,5.5,4.5,4,4,3,2,3,5,5,5,5,5,5,3,4,1,4,2,3,2,2,2
27,Female,24 or above,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,5.5,5,5,5,5,2,5,4,1,5,3,3,3,3,4,4,4,2,4,4,4
28,Female,24 or above,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,2.5,5.5,5.5,2,2,2,1,1,1,1,1,1,2,2,1,2,1,2,1,2,1,2,1
29,Female,24 or above,Smartphone; Laptop / Desktop,Academic Learning / Research; Social Media & Networking,5.5,2.5,3.5,5.5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
30,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls); Other",5.5,2.5,5.5,3.5,5,5,3,4,4,5,2,2,4,4,4,2,2,1,2,2,3,3,4,5
31,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,3.5,5,4,3,3,5,5,5,3,5,4,2,2,5,1,3,4,3,5,5,5
32,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",5.5,4.5,1.5,3.5,5,2,1,1,5,5,4,2,5,2,1,4,5,1,4,5,4,4,4,5
33,Female,24 or above,Smartphone,Academic Learning / Research,5.5,3.5,3.5,2.5,2,2,2,2,2,2,4,4,4,4,4,4,4,4,4,4,5,5,5,5
34,Female,21 - 23,Smartphone,Social Media & Networking,5.5,1.5,2.5,2.5,4,4,4,5,4,4,2,4,4,4,4,4,5,5,5,5,4,4,4,4
36,Male,18 - 20,Smartphone,Academic Learning / Research,1.5,1.5,1.5,1.5,2,2,1,1,1,1,1,2,1,2,1,2,2,2,1,2,1,1,1,1
37,Female,Under 18,Smartphone,Academic Learning / Research,4.5,3.5,2.5,1.5,4,3,4,3,4,5,4,3,4,4,4,4,4,2,4,3,3,4,4,4
38,Female,Under 18,Smartphone,Academic Learning / Research,3.5,2.5,1.5,1.5,3,2,3,1,4,5,4,4,3,3,2,3,2,2,3,4,3,4,4,5
39,Female,Under 18,Other combination,Academic Learning / Research,3.5,2.5,1.5,1.5,2,1,2,1,4,5,4,4,1,1,1,1,5,1,1,5,5,5,3,4
41,Female,Under 18,Smartphone,Academic Learning / Research,3.5,3.5,1.5,2.5,1,2,1,2,2,2,2,2,2,2,1,2,2,2,2,2,2,4,4,3
42,Male,Under 18,Smartphone,Entertainment / Streaming / Gaming,3.5,2.5,2.5,1.5,3,2,4,4,4,5,3,3,4,3,3,4,3,3,4,3,3,4,4,5
43,Female,Under 18,Smartphone,Academic Learning / Research,1.5,1.5,1.5,1.5,4,3,3,2,4,5,3,4,4,4,4,4,4,3,4,3,4,4,3,3
44,Male,18 - 20,Smartphone,Academic Learning / Research,3.5,2.5,2.5,1.5,4,2,2,4,4,4,3,4,3,3,3,3,4,4,4,3,3,3,3,3
45,Female,18 - 20,Smartphone,Academic Learning / Research,4.5,4.5,3.5,4.5,5,4,3,4,4,5,5,4,4,3,3,3,5,3,4,4,3,4,4,5
46,Female,Under 18,Smartphone,Academic Learning / Research,3.5,2.5,2.5,3.5,5,3,4,5,4,5,4,3,5,4,3,4,4,5,3,4,5,4,4,4
48,Male,Under 18,Smartphone,Social Media & Networking,3.5,1.5,3.5,1.5,3,4,1,3,3,5,3,2,4,3,3,4,3,2,3,4,3,4,4,3
49,Female,Under 18,Smartphone,Entertainment / Streaming / Gaming,3.5,1.5,3.5,2.5,4,3,3,3,4,3,3,3,4,3,4,4,4,3,3,4,3,3,3,3
50,Male,Under 18,Smartphone,Academic Learning / Research; Social Media & Networking,3.5,2.5,2.5,1.5,4,2,3,4,4,4,2,2,2,2,2,2,2,2,2,2,2,2,2,2
51,Male,Under 18,Smartphone,Academic Learning / Research,4.5,2.5,3.5,3.5,4,3,3,3,4,5,3,3,3,4,3,3,3,4,4,3,3,3,3,4
52,Female,18 - 20,Smartphone,Academic Learning / Research,3.5,1.5,2.5,3.5,3,4,3,4,4,4,4,4,4,4,4,4,4,4,4,4,3,4,4,4
53,Male,Under 18,Smartphone,Academic Learning / Research,3.5,3.5,1.5,1.5,2,1,3,1,3,2,2,4,3,3,3,3,3,2,2,5,3,3,3,4
54,Female,Under 18,Smartphone,Social Media & Networking,3.5,2.5,3.5,2.5,2,2,1,1,1,1,2,1,1,1,1,1,1,2,1,1,1,1,1,1
55,Female,18 - 20,Smartphone,Academic Learning / Research,3.5,3.5,1.5,1.5,3,3,3,2,5,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3
56,Female,Under 18,Smartphone,Academic Learning / Research,3.5,2.5,2.5,1.5,4,3,3,2,4,4,4,3,3,3,3,3,4,3,3,3,3,3,4,4
57,Male,Under 18,Smartphone,Entertainment / Streaming / Gaming,4.5,1.5,1.5,3.5,4,3,4,4,4,4,4,2,4,3,2,2,4,2,4,3,3,4,4,4
58,Male,Under 18,Smartphone,Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming,5.5,1.5,2.5,2.5,2,2,1,1,1,1,2,2,1,1,1,2,1,2,1,2,2,1,1,1
59,Other,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,3.5,5.5,3.5,4,4,5,4,4,5,5,4,4,4,5,4,2,1,4,3,3,4,4,5
60,Male,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Communication (Messaging, Email, Calls)",4.5,3.5,2.5,4.5,5,5,4,5,4,4,4,2,4,4,3,3,4,2,1,1,2,3,2,3
61,Male,21 - 23,Other combination,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls); Other",3.5,3.5,3.5,2.5,1,1,1,1,1,1,2,1,1,1,1,2,1,2,1,2,1,1,1,1
62,Male,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,2.5,1.5,1.5,3,4,4,2,4,4,2,3,4,2,2,2,4,1,3,4,3,3,3,3
63,Male,21 - 23,Smartphone; Laptop / Desktop,"Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,5.5,5,5,5,1,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5
64,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,5.5,5,5,5,5,3,4,4,2,5,5,5,5,5,2,5,5,3,2,1,2
65,Male,24 or above,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",4.5,2.5,2.5,1.5,3,2,2,2,3,4,4,3,3,3,3,3,2,1,3,2,3,3,4,5
66,Female,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",3.5,3.5,3.5,2.5,3,4,3,4,3,4,3,4,5,5,5,2,4,4,5,5,4,5,4,5
67,Male,21 - 23,Smartphone,Entertainment / Streaming / Gaming,4.5,2.5,4.5,4.5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,4,4
68,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,2.5,3.5,3.5,3,3,2,1,3,4,4,4,3,3,3,2,3,3,3,2,4,4,2,2
69,Female,21 - 23,Smartphone,"Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,5.5,2,3,4,2,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
70,Female,18 - 20,Smartphone; Laptop / Desktop,Academic Learning / Research,3.5,3.5,2.5,2.5,3,3,3,2,3,3,3,3,3,3,3,3,4,3,3,4,3,3,3,4
71,Female,18 - 20,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,3.5,2.5,4,4,3,3,4,4,4,3,4,3,3,3,5,3,4,2,4,3,3,5
72,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,1.5,2.5,3.5,5,4,4,4,3,5,4,3,4,3,2,3,4,3,4,4,2,3,2,2
73,Female,18 - 20,Smartphone,Social Media & Networking,5.5,1.5,4.5,1.5,4,4,3,3,4,5,3,3,5,5,3,3,5,2,4,4,4,4,2,3
74,Female,18 - 20,Smartphone,Social Media & Networking,5.5,1.5,2.5,3.5,3,3,4,4,3,4,4,3,4,3,3,4,3,3,4,4,3,3,3,3
75,Male,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,2.5,4.5,4.5,5,4,4,4,4,4,5,4,4,4,3,4,4,2,4,4,3,4,4,5
76,Male,21 - 23,Smartphone,Entertainment / Streaming / Gaming,3.5,4.5,2.5,2.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
77,Male,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,2.5,3.5,5.5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5
78,Female,21 - 23,Smartphone,"Academic Learning / Research; Communication (Messaging, Email, Calls)",4.5,2.5,3.5,2.5,3,4,3,3,4,5,4,4,5,3,2,4,5,4,5,5,4,3,4,5
79,Female,18 - 20,Smartphone,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",5.5,4.5,4.5,1.5,3,3,3,4,4,5,3,3,4,3,3,2,5,2,3,4,3,3,3,3
80,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,4.5,3.5,1.5,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
81,Male,21 - 23,Smartphone; Laptop / Desktop,Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming,5.5,4.5,4.5,4.5,4,4,4,5,4,4,3,3,4,4,3,4,4,5,4,4,4,5,4,4
82,Female,18 - 20,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,2.5,3.5,2.5,5,5,4,4,3,5,5,4,5,4,4,4,5,4,4,5,4,3,4,4
84,Female,21 - 23,Smartphone; Laptop / Desktop,"Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,5.5,5.5,4,5,4,4,4,4,3,2,5,4,4,3,3,2,4,2,3,4,4,3
85,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,2.5,4.5,2.5,3,4,2,3,3,5,5,4,4,4,4,4,3,4,3,3,4,3,2,4
86,Male,21 - 23,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,2.5,2.5,4,4,4,3,4,4,4,4,3,2,4,3,4,4,4,4,4,4,4,5
87,Female,18 - 20,Other combination,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",3.5,1.5,2.5,1.5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
88,Female,18 - 20,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls); Other",5.5,3.5,4.5,4.5,3,4,4,3,4,4,4,3,4,4,4,3,4,4,4,4,4,3,3,2
89,Male,21 - 23,Smartphone,Academic Learning / Research,4.5,2.5,3.5,3.5,5,5,5,5,4,5,3,5,5,5,5,5,5,5,5,5,5,5,5,5
90,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,4.5,5.5,4.5,4,5,5,4,4,5,4,5,4,4,5,4,5,5,4,5,4,4,4,5
91,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",5.5,4.5,5.5,1.5,4,4,4,4,5,4,4,4,4,4,4,3,4,3,3,3,3,4,4,4
92,Female,21 - 23,Smartphone; Laptop / Desktop,Academic Learning / Research,3.5,2.5,1.5,2.5,3,4,4,3,3,4,3,4,3,4,3,3,3,3,3,3,4,3,3,3
93,Male,24 or above,Smartphone,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",3.5,2.5,3.5,3.5,4,4,2,4,3,3,2,3,2,2,3,2,3,2,3,2,3,2,2,3
94,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Communication (Messaging, Email, Calls)",3.5,2.5,2.5,3.5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
95,Male,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,1.5,2.5,5.5,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
96,Male,21 - 23,Smartphone,Social Media & Networking; Other,5.5,4.5,4.5,2.5,4,4,4,4,4,5,5,4,2,2,4,4,4,4,4,2,2,2,5,5
97,Male,21 - 23,Smartphone,Academic Learning / Research,1.5,2.5,2.5,1.5,4,2,3,2,4,4,3,2,3,4,3,2,2,4,1,3,4,5,4,5
98,Female,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",5.5,3.5,5.5,2.5,4,5,4,3,5,5,5,4,5,3,4,5,5,5,5,5,5,5,5,5
99,Female,21 - 23,Smartphone; Laptop / Desktop,Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming,4.5,3.5,3.5,2.5,3,4,3,2,4,5,5,4,5,4,5,5,5,5,5,5,5,5,5,5
100,Female,24 or above,Smartphone,Other,4.5,3.5,3.5,1.5,4,4,4,4,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
101,Female,21 - 23,Smartphone,"Communication (Messaging, Email, Calls)",3.5,1.5,3.5,2.5,3,2,2,2,3,4,4,2,2,2,1,2,4,1,2,3,4,2,2,2
102,Male,24 or above,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls)",4.5,3.5,1.5,1.5,3,2,3,1,4,5,5,4,3,3,3,1,2,1,2,3,5,4,2,3
103,Male,21 - 23,Smartphone,Academic Learning / Research,4.5,3.5,4.5,4.5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5
104,Other,21 - 23,Smartphone; Laptop / Desktop,"Academic Learning / Research; Social Media & Networking; Entertainment / Streaming / Gaming; Communication (Messaging, Email, Calls); Other",4.5,1.5,5.5,1.5,4,5,5,1,4,5,3,1,5,3,5,5,5,3,3,5,5,5,1,5
"""

# Write the dark theme file once so Streamlit's own widgets match (takes effect after a restart)
try:
    _cfg = Path.cwd() / ".streamlit" / "config.toml"
    if not _cfg.exists():
        _cfg.parent.mkdir(exist_ok=True)
        _cfg.write_text('[theme]\nbase = "dark"\nprimaryColor = "#3987e5"\nbackgroundColor = "#0b1220"\n'
                        'secondaryBackgroundColor = "#111a2e"\ntextColor = "#f0efec"\n', encoding="utf-8")
except OSError:
    pass

# ---------------------------------------------------------------------------
# Data cleaning (mirrors the notebook, Part 1)
# ---------------------------------------------------------------------------
def tidy_text(s: pd.Series) -> pd.Series:
    return (s.astype(str).str.replace(" ", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True).str.strip())


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Binary device/purpose flags, counts and the grouped device category."""
    df["device"] = tidy_text(df["device"]).str.replace(r",\s*", "; ", regex=True)
    df["purpose"] = tidy_text(df["purpose"]).str.replace(
        r",\s*(?=Academic|Social|Entertainment|Communication|Other)", "; ", regex=True)

    df["uses_smartphone"] = df["device"].str.contains("Smartphone", regex=False).astype(int)
    df["uses_laptop_desktop"] = df["device"].str.contains("Laptop / Desktop", regex=False).astype(int)
    df["uses_tablet"] = df["device"].str.contains("Tablet", regex=False).astype(int)
    df["uses_other_device"] = df["device"].str.contains("Other", regex=False).astype(int)

    df["purpose_academic"] = df["purpose"].str.contains("Academic Learning / Research", regex=False).astype(int)
    df["purpose_social_media"] = df["purpose"].str.contains("Social Media & Networking", regex=False).astype(int)
    df["purpose_entertainment"] = df["purpose"].str.contains("Entertainment / Streaming / Gaming", regex=False).astype(int)
    df["purpose_communication"] = df["purpose"].str.contains("Communication", regex=False).astype(int)
    df["purpose_other"] = df["purpose"].str.contains("Other", regex=False).astype(int)

    df["number_of_devices"] = df[list(DEVICE_COLS)].sum(axis=1)
    df["number_of_purposes"] = df[list(PURPOSE_COLS)].sum(axis=1)

    df["gender"] = tidy_text(df["gender"]).replace({"Prefer not to say": "Other"})
    df["age_group"] = tidy_text(df["age_group"])

    only_phone = (df["number_of_devices"] == 1) & (df["uses_smartphone"] == 1)
    phone_laptop = (df["number_of_devices"] == 2) & (df["uses_smartphone"] == 1) & (df["uses_laptop_desktop"] == 1)
    df["device_group"] = np.select([only_phone, phone_laptop],
                                   ["Smartphone only", "Smartphone + Laptop"], "Other combination")
    df["purpose_group"] = np.where(df["number_of_purposes"] > 1, "Multiple purposes", df["purpose"])
    return df


def clean_raw(raw: pd.DataFrame):
    """Clean the raw Google Forms export exactly like the notebook."""
    report = {"source": "raw", "raw_rows": len(raw), "raw_cols": raw.shape[1]}
    df = raw.copy()
    df = df.drop(columns=[c for c in df.columns if str(c).strip().lower() in ("score", "timestamp")])
    if df.shape[1] != len(COLUMN_NAMES):
        raise ValueError(
            f"Expected 28 survey questions (plus Timestamp and Score) but found {df.shape[1]} columns.")
    df.columns = COLUMN_NAMES
    df.insert(0, "respondent_id", range(1, len(df) + 1))

    dup_mask = df.drop(columns="respondent_id").duplicated()
    report["duplicates"] = int(dup_mask.sum())
    df = df[~dup_mask]

    df = df.replace(r"^\s*$", np.nan, regex=True)
    report["missing_cells"] = int(df.isna().sum().sum())
    report["dropped_missing"] = int(df.isna().any(axis=1).sum())
    df = df.dropna().reset_index(drop=True)

    for col in HOURS_COLS:
        df[col] = tidy_text(df[col]).map(HOURS_MAP)
    for col in LIKERT_COLS:
        df[col] = tidy_text(df[col]).map(LIKERT_MAP)
    invalid = df[HOURS_COLS + LIKERT_COLS].isna().any(axis=1)
    report["dropped_invalid"] = int(invalid.sum())
    df = df[~invalid].reset_index(drop=True)
    df[LIKERT_COLS] = df[LIKERT_COLS].astype(int)

    df = add_derived_columns(df)
    report["clean_rows"], report["clean_cols"] = df.shape
    return df, report


def prepare_cleaned(df: pd.DataFrame):
    """Accept the notebook's cleaned CSV (hours and Likert already numeric)."""
    df = df.copy()
    for col in HOURS_COLS:
        if df[col].dtype == object:
            df[col] = tidy_text(df[col]).map(HOURS_MAP)
    for col in LIKERT_COLS:
        if df[col].dtype == object:
            df[col] = tidy_text(df[col]).map(LIKERT_MAP)
    df = df.dropna(subset=HOURS_COLS + LIKERT_COLS).reset_index(drop=True)
    df[LIKERT_COLS] = df[LIKERT_COLS].astype(int)
    # Some saved versions replaced the device answer with its group name, which hides the real devices
    lost = int((tidy_text(df["device"]) == "Other combination").sum())
    df = add_derived_columns(df)
    if lost:
        df.loc[df["device"] == "Other combination", "device_group"] = "Other combination"
    report = {"source": "cleaned", "clean_rows": df.shape[0], "clean_cols": df.shape[1], "device_detail_lost": lost}
    return df, report


@st.cache_data(show_spinner="Cleaning survey data…")
def load_data(csv_bytes: bytes):
    from io import BytesIO
    raw = pd.read_csv(BytesIO(csv_bytes))
    if {"respondent_id", "gender", "total_hours"}.issubset(raw.columns):
        return prepare_cleaned(raw)
    return clean_raw(raw)


def find_local_file():
    for folder in (APP_DIR, APP_DIR / "data"):
        for name in RAW_FILE_NAMES + CLEAN_FILE_NAMES:
            if (folder / name).exists():
                return folder / name
    return None


# ---------------------------------------------------------------------------
# Statistics helpers (NumPy / Pandas / SciPy)
# ---------------------------------------------------------------------------
def describe_series(s: pd.Series) -> dict:
    s = s.dropna()
    if s.empty:
        return {}
    return {"Count": int(s.count()), "Mean": s.mean(), "Median": s.median(), "Mode": s.mode().iloc[0],
            "Min": s.min(), "Max": s.max(), "Range": s.max() - s.min(), "Std dev": s.std(ddof=1)}


def iqr_filter(df: pd.DataFrame, group: str, value: str = "total_hours", k: float = 1.5) -> pd.DataFrame:
    """Remove outliers with the 1.5 × IQR rule inside each group (notebook 2.4)."""
    q1 = df.groupby(group)[value].transform(lambda s: np.percentile(s, 25))
    q3 = df.groupby(group)[value].transform(lambda s: np.percentile(s, 75))
    iqr = q3 - q1
    return df[(df[value] >= q1 - k * iqr) & (df[value] <= q3 + k * iqr)]


def spearman(x: pd.Series, y: pd.Series):
    if len(x) < 5 or x.nunique() < 2 or y.nunique() < 2:
        return None
    rho, p = stats.spearmanr(x, y)
    return float(rho), float(p), int(len(x))


def strength(r: float) -> str:
    r = abs(r)
    return "negligible" if r < 0.1 else "weak" if r < 0.3 else "moderate" if r < 0.5 else "strong"


def pct(x: float) -> str:
    return f"{x:.1f}%"


def hours(x: float) -> str:
    return f"{x:.2f} h"



# ---------------------------------------------------------------------------
# Look and feel - matches the Figma prototype (dark navy, blue accents)
# ---------------------------------------------------------------------------
BLUE, GREEN, PURPLE, ORANGE, TEAL = "#3b82f6", "#1fa865", "#a855f7", "#e2691b", "#12a091"
BG, SIDEBAR, PANEL, PANEL2, LINE = "#0a1020", "#0f1830", "#131c33", "#18233f", "#24304d"
TEXT1, TEXT2, MUTED, ACCENT = "#f1f5f9", "#c3cad8", "#8b95ab", "#6ea8ff"
GRID = LINE
CARD = PANEL
DEVICE_COLOURS = {"Smartphone": BLUE, "Laptop / Desktop": GREEN, "Tablet": PURPLE, "Other": ORANGE}
PURPOSE_SHORT = {"purpose_academic": "Academic Learning", "purpose_social_media": "Social Media",
                 "purpose_communication": "Communication", "purpose_entertainment": "Entertainment",
                 "purpose_other": "Other"}
PURPOSE_COLOURS = {"Academic Learning": BLUE, "Social Media": GREEN, "Communication": PURPLE,
                   "Entertainment": ORANGE, "Other": TEAL}
GENDER_LABEL = {"Female": "Female", "Male": "Male", "Other": "Prefer not to say"}
AGE_LABEL = {"Under 18": "Under 18", "18 - 20": "18–20", "21 - 23": "21–23", "24 or above": "24+"}
BAND_LABEL = {0.5: "<1 hr", 1.5: "1–2 hrs", 2.5: "2–3 hrs", 3.5: "3–4 hrs", 4.5: "4–5 hrs", 5.5: "5+ hrs"}
BAND_SHADES = ["#2a63c9", "#3474e6", "#3b82f6", "#5f9bf8", "#8cb8fb", "#b4d1fd"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, .stApp, [data-testid="stMarkdownContainer"], button, input {{font-family: 'Inter', 'Segoe UI', sans-serif !important;}}
.stApp {{background: {BG};}}
header[data-testid="stHeader"] {{background: transparent;}}
.block-container {{max-width: 1180px; padding-top: 2.4rem; padding-bottom: 3rem;}}
[data-testid="stVerticalBlock"] {{gap: 0.9rem;}}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {{background: {SIDEBAR}; border-right: 1px solid {LINE};}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{gap: 0.5rem;}}
.brand {{display:flex; align-items:center; gap:14px; margin: 4px 0 26px 4px;}}
.brand-logo {{width:46px; height:46px; border-radius:50%; background:{PANEL2}; border:1px solid {LINE};
             display:flex; align-items:center; justify-content:center; font-size:22px; overflow:hidden;}}
.brand-logo img {{width:100%; height:100%; object-fit:cover;}}
.brand-name {{color:{TEXT1}; font-weight:700; letter-spacing:.08em; font-size:14px;}}
.brand-sub {{color:{MUTED}; letter-spacing:.14em; font-size:11px; margin-top:2px;}}
.side-label {{color:{MUTED}; font-size:12px; font-weight:700; letter-spacing:.14em; margin: 0 0 4px 12px;}}
[data-testid="stSidebar"] [data-testid="stRadio"], [data-testid="stSidebar"] [data-testid="stRadio"] > div {{width: 100%;}}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{gap: 6px; width:100%; display:flex;
    flex-direction:column; align-items:stretch;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{padding: 12px 16px !important; border-radius: 10px; width: 100% !important;
    max-width: 100% !important; margin: 0; cursor: pointer; transition: background .15s;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:not(:last-child) {{display: none !important;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:last-child {{padding-left: 0 !important; margin-left: 0 !important;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {{font-size: 15px; font-weight: 600; color: #c9d2e3; white-space: pre;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{background: rgba(255,255,255,0.04);}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{background: #1d3460;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {{color: #7fb0ff;}}
.side-foot {{border-top:1px solid {LINE}; margin-top: 26px; padding: 18px 0 4px 10px;}}
.side-foot .dot {{display:inline-block; width:8px; height:8px; border-radius:50%; background:{GREEN}; margin-right:6px;}}
.side-foot .lbl {{color:{MUTED}; font-size:11px; font-weight:700; letter-spacing:.12em;}}
.side-foot .val {{color:{TEXT1}; font-weight:700; font-size:14px; margin: 4px 0 0 14px;}}

/* ---------- header ---------- */
.hdr {{display:flex; justify-content:space-between; align-items:flex-start; gap:20px;
       padding-bottom: 22px; border-bottom: 1px solid {LINE}; margin-bottom: 8px;}}
.hdr-title {{color:{TEXT1}; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.02em; line-height:1.15;}}
.hdr-sub {{color:{TEXT2}; font-size: 1rem; margin-top: 8px;}}
.badge {{border:1px solid {LINE}; color:#93bbff; padding:10px 14px; border-radius:10px; font-size:12px;
        font-weight:700; letter-spacing:.1em; white-space:nowrap;}}

/* ---------- cards ---------- */
.st-key-explore, [class*="st-key-card_"] {{background:{PANEL}; border:1px solid {LINE}; border-radius:16px;
       padding: 24px 26px 20px 26px;}}
.card-title {{color:{TEXT1}; font-size: 1.15rem; font-weight: 700;}}
.card-sub {{color:{MUTED}; font-size: .9rem; margin-top: 4px;}}
.viewing {{color:{ACCENT}; font-weight:700; font-size:.9rem; margin-top: 10px;}}
.eyebrow {{color:{ACCENT}; font-size:12px; font-weight:800; letter-spacing:.16em; text-transform:uppercase;}}
.sec {{display:flex; justify-content:space-between; align-items:flex-end; margin: 26px 0 4px 0; gap: 16px;}}
.sec-title {{color:{TEXT1}; font-size: 1.65rem; font-weight: 400; letter-spacing:-0.01em; margin-top: 6px;}}
.sec-note {{color:{MUTED}; font-size: .92rem; text-align:right;}}
.empty {{text-align:center; padding: 40px 0;}}
.empty h3 {{color:{TEXT1}; font-size:1.4rem; font-weight:700; margin:0 0 6px 0;}}
.empty p {{color:{MUTED}; margin:0;}}

/* KPI */
.kpi {{background:{PANEL}; border:1px solid {LINE}; border-radius:16px; padding: 22px 24px; height:100%; margin-bottom: 10px;}}
.kpi-bar {{width: 34px; height: 4px; border-radius: 2px; margin-bottom: 18px;}}
.kpi-label {{color:{TEXT2}; font-size: .95rem;}}
.kpi-value {{color:{TEXT1}; font-size: 1.85rem; font-weight: 800; line-height: 1.25; margin-top: 6px;}}
.kpi-sub {{color:{MUTED}; font-size: .85rem; margin-top: 2px;}}

/* progress rows */
.br {{margin: 0 0 16px 0;}}
.br-top {{display:flex; justify-content:space-between; color:{TEXT1}; font-size: .95rem; margin-bottom: 7px;}}
.br-top b {{font-weight:700;}}
.track {{height: 10px; border-radius: 6px; background: #26324f; overflow:hidden;}}
.fill {{height: 100%; border-radius: 6px;}}
.foot {{color:{MUTED}; font-size:.8rem; margin-top: 4px;}}

/* legend next to donuts */
.lg {{display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); column-gap: 22px; row-gap: 10px; margin-top: 4px;}}
.lg-row {{display:flex; justify-content:space-between; align-items:center; gap: 8px; color:{TEXT2}; font-size:.88rem; min-width:0;}}
.lg-row > span {{white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
.lg-row b {{color:{TEXT1}; white-space:nowrap;}}
.lg-dot {{display:inline-block; width:10px; height:10px; border-radius:50%; margin-right: 8px;}}

/* audience (group) cards */
.badge-ic {{width:36px; height:36px; border-radius:8px; display:inline-flex; align-items:center; justify-content:center;
           font-weight:800; margin-right: 12px;}}
.gk {{color:{MUTED}; font-size: 12px; font-weight:800; letter-spacing:.14em;}}
.big-title {{color:{TEXT1}; font-size:1.45rem; font-weight:800; margin-top: 18px;}}
[class*="st-key-gc_"] {{background:{PANEL2}; border:1px solid {LINE}; border-radius:12px; padding: 16px 20px 14px 20px; gap: .3rem;}}
[class*="st-key-gc_"][class*="_onB"] {{border-color:{BLUE}; background:#1b2c52;}}
[class*="st-key-gc_"][class*="_onG"] {{border-color:{GREEN}; background:#1b2c52;}}
[class*="st-key-gc_"][class*="_zero"] {{opacity: .5;}}
.gc-name {{color:{TEXT1}; font-weight:700; font-size: 1rem; padding-top: 6px;}}
.gc-name span {{color:{TEXT2}; font-weight:400;}}
.gc-count {{color:{TEXT1}; font-size: 1.9rem; font-weight:800;}}
.gc-count span {{color:{TEXT2}; font-size:.95rem; font-weight:400;}}
.gc-foot {{display:flex; justify-content:space-between; color:{TEXT2}; font-size:.88rem; margin-top: 12px;}}
.tip {{background:#16264a; border:1px solid {LINE}; border-radius:10px; padding: 12px 16px; color:{TEXT2}; font-size:.9rem;}}
.tip b {{color:{ACCENT}; letter-spacing:.12em; font-size:11px; margin-right:10px;}}

/* highlight cards on insights */
.hl {{border-radius:16px; padding: 30px 30px; position:relative; overflow:hidden; min-height: 210px;}}
.hl::after {{content:""; position:absolute; right:-40px; bottom:-60px; width:170px; height:170px; border-radius:50%;
            border: 18px solid rgba(255,255,255,0.06);}}
.hl .k {{font-size:12px; font-weight:800; letter-spacing:.16em;}}
.hl .v {{color:{TEXT1}; font-size:1.9rem; font-weight:800; margin-top: 12px; line-height:1.2;}}
.hl .s {{color:{TEXT2}; margin-top: 12px; font-size: .95rem;}}
.stat {{background:{PANEL2}; border:1px solid {LINE}; border-radius:10px; padding: 14px 16px;}}
.stat .l {{color:{MUTED}; font-size:.82rem;}}
.stat .v {{color:{TEXT1}; font-size:1.3rem; font-weight:800; margin-top: 8px;}}
.act .v {{color:{TEXT1}; font-size:1.35rem; font-weight:800;}}
.act .l {{color:{MUTED}; font-size:.88rem; margin-top: 4px;}}
.hx {{display:grid; gap:6px; align-items:center;}}
.hx .c {{border-radius:6px; text-align:center; padding: 15px 0; color:#fff; font-weight:700; font-size:.92rem;}}
.hx .h {{color:{TEXT2}; font-size:.85rem; font-weight:600; text-align:center;}}
.hx .r {{color:{TEXT2}; font-size:.92rem; font-weight:600;}}
.test {{display:flex; justify-content:space-between; align-items:center; padding: 16px 0; border-bottom: 1px solid {LINE};}}
.test .t {{color:{TEXT1}; font-weight:700; font-size: 1rem;}}
.test .d {{color:{MUTED}; font-size:.86rem; margin-top: 4px;}}
.test .p {{color:{ACCENT}; font-weight:800; font-size:1.05rem; white-space:nowrap;}}
.concl {{background:#1b2c52; border-radius:10px; padding: 16px 18px; color:{TEXT1}; font-size:.95rem; margin-top: 18px; line-height:1.5;}}
.insight {{background:{PANEL}; border:1px solid {LINE}; border-left: 4px solid {BLUE}; border-radius: 12px; padding: 16px 18px; margin-bottom: 12px;}}
.insight h4 {{margin: 0 0 6px 0; font-size: 1rem; color: {TEXT1}; font-weight:700;}}
.insight p {{margin: 0; color: {TEXT2}; font-size: 0.93rem; line-height:1.55;}}
.insight .so {{margin-top: 8px; color: #93bbff; font-size: 0.9rem;}}

/* ---------- widgets ---------- */
[data-testid="stButtonGroup"] {{display: block; background: none; width: 100%;}}
[data-testid="stButtonGroup"] [data-testid="stWidgetLabel"] {{display: block; margin-bottom: 8px;}}
[data-testid="stButtonGroup"] div:has(> button) {{background: #0b1222; border-radius: 12px; padding: 5px; gap: 2px;
    display: inline-flex; flex-wrap: wrap; width: auto; max-width: 100%;}}
[data-testid="stButtonGroup"] button {{background: transparent !important; border: none !important; color: #d5dcea !important;
    font-weight: 600 !important; border-radius: 9px !important; padding: 6px 14px !important; min-height: 38px;
    box-shadow:none !important; flex: 0 0 auto; white-space: nowrap;}}
[data-testid="stButtonGroup"] button p {{font-weight: 600 !important;}}
[data-testid="stButtonGroup"] button:hover {{background: #1d2a47 !important;}}
[data-testid="stButtonGroup"] button[data-testid$="Active"] {{background: {BLUE} !important; color: #fff !important;}}
[data-testid="stWidgetLabel"] p {{color: {TEXT2}; font-weight: 600;}}
button[data-testid="stBaseButton-tertiary"] {{color: {ACCENT} !important;}}
button[data-testid="stBaseButton-tertiary"] p {{font-weight: 700 !important; font-size: 11px; letter-spacing: .07em;
    white-space: nowrap !important; overflow: visible !important; text-overflow: clip !important;}}
button[data-testid="stBaseButton-tertiary"] {{justify-content: flex-end; padding-right: 0 !important; min-width: max-content;}}
button[data-testid="stBaseButton-tertiary"] div {{overflow: visible !important;}}
.st-key-clear button p {{font-size: 14px !important; letter-spacing: 0 !important;}}
.st-key-clear button {{justify-content: flex-end;}}
[class*="st-key-gc_"] button[data-testid="stBaseButton-tertiary"] p {{font-size: 18px !important; color:{MUTED};}}
[class*="st-key-gc_"] button[data-testid="stBaseButton-tertiary"]:hover p {{color:{ACCENT};}}
[data-testid="stExpander"] details {{background:{PANEL}; border-color:{LINE}; border-radius:12px;}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Small building blocks
# ---------------------------------------------------------------------------
def html(s):
    st.markdown(s, unsafe_allow_html=True)


def card(key):
    return st.container(key=f"card_{key}")


def section(eyebrow, title, note=""):
    html(f"<div class='sec'><div><div class='eyebrow'>{eyebrow}</div><div class='sec-title'>{title}</div></div>"
         f"<div class='sec-note'>{note}</div></div>")


def goto(page):
    st.session_state.page = page


def card_head(title, sub=None, link=None, key=None, eyebrow=None):
    left, right = st.columns([1.7, 1], vertical_alignment="top")
    with left:
        html((f"<div class='eyebrow' style='margin-bottom:8px'>{eyebrow}</div>" if eyebrow else "")
             + f"<div class='card-title'>{title}</div>" + (f"<div class='card-sub'>{sub}</div>" if sub else ""))
    if link:
        with right:
            st.button(f"EXPLORE {link.upper()} ↗", key=f"lnk_{key}", type="tertiary", on_click=goto, args=(link,),
                      width="stretch")


def kpi(col, label, value, sub, accent):
    col.markdown(f"<div class='kpi'><div class='kpi-bar' style='background:{accent}'></div>"
                 f"<div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div>"
                 f"<div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)


def bar_rows(rows, foot=None):
    """rows: (label, value text, fraction 0-1, colour)"""
    out = "".join(
        f"<div class='br'><div class='br-top'><span>{l}</span><b>{v}</b></div>"
        f"<div class='track'><div class='fill' style='width:{min(max(f, 0), 1) * 100:.1f}%;background:{c}'></div></div></div>"
        for l, v, f, c in rows)
    if foot:
        out += f"<div class='foot'>{foot}</div>"
    html(out)


def insight(title, text, so_what=None, accent=BLUE):
    extra = f"<div class='so'>Why it matters: {so_what}</div>" if so_what else ""
    html(f"<div class='insight' style='border-left-color:{accent}'><h4>{title}</h4><p>{text}</p>{extra}</div>")


def style(fig, height=300, title=None, legend=True):
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=title, font=dict(size=15, color=TEXT1), x=0, xanchor="left") if title else None,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color=TEXT2),
        height=height, margin=dict(l=6, r=6, t=44 if title else 8, b=6),
        hoverlabel=dict(bgcolor=BG, bordercolor=LINE, font=dict(color=TEXT1)),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None),
        bargap=0.35,
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False, linecolor=LINE, title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=LINE, zeroline=False, linecolor=LINE, title_font=dict(color=MUTED))
    return fig


def show(fig, key=None):
    st.plotly_chart(fig, width="stretch", key=key,
                    config={"displaylogo": False, "toImageButtonOptions": {"scale": 2}})


def donut(labels, values, colours, centre_value, centre_label, key):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.66, sort=False, direction="clockwise",
                           marker=dict(colors=colours, line=dict(color=PANEL, width=3)), textinfo="none",
                           hovertemplate="<b>%{label}</b><br>%{value} · %{percent}<extra></extra>"))
    fig.add_annotation(text=f"<span style='font-size:30px;font-weight:800'>{centre_value}</span><br>"
                            f"<span style='font-size:10px;letter-spacing:2px'>{centre_label}</span>",
                       showarrow=False, font=dict(color=TEXT1))
    show(style(fig, height=230, legend=False), key)


def legend_html(labels, values, colours):
    total = sum(values) or 1
    html("<div class='lg'>" + "".join(
        f"<div class='lg-row'><span><span class='lg-dot' style='background:{c}'></span>{l}</span>"
        f"<b>{v} · {v / total * 100:.1f}%</b></div>" for l, v, c in zip(labels, values, colours)) + "</div>")


def group_mean_bar(df, group_col, order, value="total_hours", title=None):
    g = df.groupby(group_col)[value].agg(["count", "mean", "median"]).reindex(order).dropna()
    names = [GENDER_LABEL.get(i, AGE_LABEL.get(i, i)) for i in g.index]
    fig = go.Figure(go.Bar(
        x=names, y=g["mean"], marker_color=BLUE, marker_cornerradius=4,
        text=[f"{m:.2f}" for m in g["mean"]], textposition="outside", cliponaxis=False, textfont=dict(color=TEXT2),
        customdata=np.stack([g["count"], g["median"]], axis=-1),
        hovertemplate="<b>%{x}</b><br>Mean: %{y:.2f} h/day<br>Median: %{customdata[1]:.1f}<br>n = %{customdata[0]:.0f}<extra></extra>",
    ))
    fig.update_xaxes(ticktext=[f"{nm}<br><span style='font-size:10px'>n={int(c)}</span>" for nm, c in zip(names, g["count"])],
                     tickvals=names)
    fig.update_yaxes(title="Mean hours per day", range=[0, 6.2])
    return style(fig, height=320, title=title, legend=False)


# ---------------------------------------------------------------------------
# Sidebar: brand + navigation
# ---------------------------------------------------------------------------
PAGES = ["Overview", "Usage", "Devices", "Purposes", "Insights"]
for k, v in {"page": "Overview", "f_gender": "All", "f_age": "All", "ins_mode": "Purposes"}.items():
    st.session_state.setdefault(k, v)

logo_html = "📶"
for name in ("logo.png", "logo.jpg", "logo.jpeg"):
    if (APP_DIR / name).exists():
        import base64
        b64 = base64.b64encode((APP_DIR / name).read_bytes()).decode()
        logo_html = f"<img src='data:image/{name.split('.')[-1]};base64,{b64}'/>"
        break

with st.sidebar:
    html(f"<div class='brand'><div class='brand-logo'>{logo_html}</div>"
         f"<div><div class='brand-name'>STUDENT DATA</div><div class='brand-sub'>INTERNET USAGE</div></div></div>"
         f"<div class='side-label'>DASHBOARD</div>")
    st.radio("Go to page", PAGES, key="page", label_visibility="collapsed",
             format_func=lambda p: f"{PAGES.index(p) + 1:02d}    {p}")

# ---------------------------------------------------------------------------
# Load data (uploaded file > CSV next to app.py > built-in data)
# ---------------------------------------------------------------------------
with st.sidebar:
    foot_slot = st.empty()
    with st.expander("Data source"):
        uploaded = st.file_uploader("Load a different survey CSV", type="csv",
                                    help="Raw Google Forms export or the cleaned CSV from the notebook.")

csv_bytes, source_name = None, None
if uploaded is not None:
    csv_bytes, source_name = uploaded.getvalue(), uploaded.name
else:
    local = find_local_file()
    if local is not None:
        csv_bytes, source_name = local.read_bytes(), local.name
if csv_bytes is None:
    csv_bytes, source_name = EMBEDDED_CSV.encode("utf-8"), "built-in survey data"

try:
    data, clean_report = load_data(csv_bytes)
except Exception as exc:
    st.error(f"Could not read **{source_name}**: {exc}")
    st.stop()

N_ALL = len(data)
with foot_slot:
    html(f"<div class='side-foot'><span class='dot'></span><span class='lbl'>SURVEY DATA</span>"
         f"<div class='val'>{N_ALL} responses</div></div>")

# ---------------------------------------------------------------------------
# Header and filter card
# ---------------------------------------------------------------------------
html("<div class='hdr'><div><div class='hdr-title'>Student Daily Internet Usage Dashboard</div>"
     "<div class='hdr-sub'>Analysis of Daily Internet Usage Among Students, PRG405 Introduction to Data Science</div>"
     "</div><div class='badge'>PRG405 · DATA SCIENCE</div></div>")

GENDER_OPTS = ["All", "Female", "Male", "Other"]
AGE_OPTS = ["All"] + AGE_ORDER


def keep_value(key, fallback):
    """Segmented controls can be clicked off; put the default back so something is always selected."""
    if st.session_state.get(key) is None:
        st.session_state[key] = fallback


def reset_filters():
    st.session_state.f_gender = "All"
    st.session_state.f_age = "All"


f_gender = st.session_state.get("f_gender") or "All"
f_age = st.session_state.get("f_age") or "All"
viewing = (f"Viewing {'All genders' if f_gender == 'All' else GENDER_LABEL[f_gender]} · "
           f"{'all ages' if f_age == 'All' else 'ages ' + AGE_LABEL[f_age]}")

with st.container(key="explore"):
    t1, t2 = st.columns([3, 1])
    with t1:
        html(f"<div class='card-title'>Explore the data</div><div class='card-sub'>Choose a group to update every view.</div>"
             f"<div class='viewing'>{viewing}</div>")
    with t2:
        st.button("Clear filters", key="clear", type="tertiary", on_click=reset_filters, width="stretch")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.segmented_control("Gender", GENDER_OPTS, key="f_gender", on_change=keep_value, args=("f_gender", "All"),
                             format_func=lambda g: "All" if g == "All" else GENDER_LABEL[g])
    with c2:
        st.segmented_control("Age group", AGE_OPTS, key="f_age", on_change=keep_value, args=("f_age", "All"),
                             format_func=lambda a: "All" if a == "All" else AGE_LABEL[a])

f_gender = st.session_state.get("f_gender") or "All"
f_age = st.session_state.get("f_age") or "All"


def apply_filters(frame, gender=True, age=True):
    if gender and f_gender != "All":
        frame = frame[frame["gender"] == f_gender]
    if age and f_age != "All":
        frame = frame[frame["age_group"] == f_age]
    return frame


df = apply_filters(data)
n = len(df)


def no_match():
    with card("empty"):
        html("<div class='empty'><h3>No matching responses</h3><p>There are no students in this combination of "
             "gender and age group. Try a different filter or clear your selection.</p></div>")


# Numbers shared by several pages
def device_numbers(frame):
    cnt = frame[list(DEVICE_COLS)].sum().rename(DEVICE_COLS).astype(int)
    return cnt


def purpose_numbers(frame):
    cols = ["purpose_academic", "purpose_social_media", "purpose_communication", "purpose_entertainment", "purpose_other"]
    return frame[cols].sum().rename(PURPOSE_SHORT).astype(int)


# ---------------------------------------------------------------------------
# 01 Overview
# ---------------------------------------------------------------------------
def page_overview():
    section("At a glance", "Survey overview", "The big picture, tailored to your selection.")
    if n == 0:
        return no_match()
    dev = device_numbers(df)
    k = st.columns(3)
    kpi(k[0], "Total Respondents", f"{n}", "Students surveyed", BLUE)
    kpi(k[1], "Estimated Mean Usage", f"{df['total_hours'].mean():.2f} hrs", "Mean of coded hour bands", GREEN)
    kpi(k[2], "Most-Used Device", dev.idxmax(), f"{dev.max() / n * 100:.1f}% of students", PURPLE)

    c1, c2 = st.columns([1.3, 1])
    with c1, card("box"):
        card_head("Daily hours · box plot", "Estimated spread of daily internet hours", "Usage", "ov1")
        fig = go.Figure(go.Box(x=df["total_hours"], orientation="h", name="", boxpoints=False,
                               fillcolor="rgba(59,130,246,0.30)", line=dict(color="#7fb0ff", width=2),
                               whiskerwidth=0.6, hoverinfo="x"))
        fig.update_xaxes(range=[1.3, 5.7], tickvals=[1.5, 2.5, 3.5, 4.5, 5.5], showgrid=False,
                         showline=True, linecolor=LINE)
        fig.update_yaxes(visible=False)
        show(style(fig, height=150, legend=False), "ov_box")
        s = df["total_hours"]
        html(f"<div class='foot'>Min {s.min():.2f} hrs · median {s.median():.2f} hrs · max {s.max():.2f} hrs</div>")
    with c2, card("dev"):
        card_head("Usage by device", "Device selections · multiple selections possible", "Devices", "ov2")
        cols = [DEVICE_COLOURS[i] for i in dev.index]
        donut(list(dev.index), list(dev.values), cols, int(dev.sum()), "SELECTIONS", "ov_donut")
        legend_html(list(dev.index), list(dev.values), cols)

    c3, c4 = st.columns([1, 1.25])
    with c3, card("pur"):
        card_head("Usage by purpose", "Mentions · multiple selections possible", "Purposes", "ov3")
        pur = purpose_numbers(df)
        bar_rows([(l, f"{v}", v / n, PURPOSE_COLOURS[l]) for l, v in pur.items()])
    with c4, card("dist"):
        card_head("Daily usage distribution", "Reported hour bands, not exact hours", "Usage", "ov4")
        bands = sorted(data["total_hours"].unique())
        counts = [int((df["total_hours"] == b).sum()) for b in bands]
        fig = go.Figure(go.Bar(x=[BAND_LABEL[b] for b in bands], y=counts, marker_cornerradius=4,
                               marker_color=[BAND_SHADES[min(int(b), 5)] for b in bands],
                               text=counts, textposition="outside", cliponaxis=False,
                               textfont=dict(color=TEXT1, size=14),
                               hovertemplate="<b>%{x}</b> per day<br>%{y} students<extra></extra>"))
        fig.update_yaxes(visible=False, range=[0, max(counts + [1]) * 1.25])
        fig.update_xaxes(showgrid=False, showline=False)
        show(style(fig, height=270, legend=False), "ov_dist")

    with card("act"):
        card_head("Where the hours go", "Mean hours per day spent on each activity (asked separately, so they overlap)")
        means = df[HOURS_COLS[1:]].mean()
        names = ["Academic / learning", "Social media & communication", "Entertainment & gaming"]
        fig = go.Figure(go.Bar(x=means.values, y=names, orientation="h", marker_color=[BLUE, GREEN, ORANGE],
                               marker_cornerradius=4, text=[f"{v:.2f} hrs" for v in means.values],
                               textposition="outside", cliponaxis=False, textfont=dict(color=TEXT1),
                               hovertemplate="<b>%{y}</b><br>%{x:.2f} hrs/day<extra></extra>"))
        fig.update_xaxes(range=[0, 6.3], title="Mean hours per day")
        fig.update_yaxes(autorange="reversed", showgrid=False)
        show(style(fig, height=210, legend=False), "ov_act")


# ---------------------------------------------------------------------------
# 02 Usage
# ---------------------------------------------------------------------------
def set_gender(g):
    st.session_state.f_gender = "All" if st.session_state.get("f_gender") == g else g


def set_age(a):
    st.session_state.f_age = "All" if st.session_state.get("f_age") == a else a


def audience_card(kind, value, label, count, frac_of_sel, max_count, mean_h, colour, selected, on_click):
    tag = ("_onB" if colour == BLUE else "_onG") if selected else ""
    tag += "_zero" if count == 0 else ""
    with st.container(key=f"gc_{kind}_{value.replace(' ', '')}{tag}"):
        a, b = st.columns([6, 1], vertical_alignment="center")
        with a:
            html(f"<div class='gc-name'>{label}</div>")
        with b:
            st.button("↗", key=f"go_{kind}_{value}", type="tertiary", on_click=on_click, args=(value,),
                      help=f"Filter the whole dashboard to {label.split('<')[0].strip()}")
        width = count / max_count * 100 if max_count else 0
        html(f"<div class='gc-count'>{count} <span>students</span></div>"
             f"<div class='track' style='margin-top:12px'><div class='fill' style='width:{width:.1f}%;background:{colour}'></div></div>"
             f"<div class='gc-foot'><span>{frac_of_sel:.0f}% of selection</span>"
             f"<span>{'N/A' if count == 0 else f'{mean_h:.2f} hrs'} / day</span></div>")


def page_usage():
    section("Group comparison", "Explore the audience", "Choose a group to filter the usage view.")
    left, right = st.columns(2)
    with left, card("bygender"):
        base = apply_filters(data, gender=False)
        html(f"<div><span class='badge-ic' style='background:#e8efff;color:{BLUE}'>G</span><span class='gk'>01 / GENDER</span></div>"
             f"<div class='big-title'>By gender</div>"
             f"<div class='card-sub'>{'For all students' if f_age == 'All' else 'For students aged ' + AGE_LABEL[f_age]} · click ↗ to explore</div>")
        counts = {g: int((base["gender"] == g).sum()) for g in GENDER_ORDER}
        mx = max(counts.values()) if counts else 0
        for g in GENDER_ORDER:
            sub = base[base["gender"] == g]
            audience_card("g", g, GENDER_LABEL[g], counts[g], counts[g] / max(len(base), 1) * 100, mx,
                          sub["total_hours"].mean() if len(sub) else 0, BLUE, f_gender == g, set_gender)
    with right, card("byage"):
        base = apply_filters(data, age=False)
        who = "all" if f_gender == "All" else GENDER_LABEL[f_gender].lower()
        html(f"<div><span class='badge-ic' style='background:#dcf7e9;color:{GREEN}'>A</span><span class='gk'>02 / AGE GROUP</span></div>"
             f"<div class='big-title'>By age group</div>"
             f"<div class='card-sub'>For {who} students · click ↗ to explore</div>")
        counts = {a: int((base["age_group"] == a).sum()) for a in AGE_ORDER}
        mx = max(counts.values()) if counts else 0
        for a in AGE_ORDER:
            sub = base[base["age_group"] == a]
            lab = AGE_LABEL[a] + ("" if a == "Under 18" else " <span>years</span>")
            audience_card("a", a, lab, counts[a], counts[a] / max(len(base), 1) * 100, mx,
                          sub["total_hours"].mean() if len(sub) else 0, GREEN, f_age == a, set_age)
    html("<div class='tip'><b>TIP</b>Combine the filters above to compare genders within an age group, "
         "or age groups within a gender.</div>")

    section("Time online", "How much time students spend online", "Descriptive statistics with Pandas and NumPy.")
    if n == 0:
        return no_match()
    with card("stats"):
        card_head("Descriptive statistics", "Hours per day · range midpoints (1–2 hrs → 1.5 … 5+ hrs → 5.5)")
        table = pd.DataFrame({HOURS_LABELS[c]: describe_series(df[c]) for c in HOURS_COLS}).T
        table["Count"] = table["Count"].astype(int)
        st.dataframe(table.style.format({c: "{:.0f}" if c == "Count" else "{:.2f}" for c in table.columns}),
                     width="stretch")

    c1, c2 = st.columns(2)
    with c1, card("udist"):
        card_head("Distribution by activity", "Share of students in each hour band")
        act = st.selectbox("Activity", HOURS_COLS, format_func=lambda c: HOURS_LABELS[c], key="u_act")
        bands = sorted(data[act].unique())
        counts = np.array([int((df[act] == b).sum()) for b in bands])
        fig = go.Figure(go.Bar(x=[BAND_LABEL[b] for b in bands], y=counts / n * 100, marker_cornerradius=4,
                               marker_color=[BAND_SHADES[min(int(b), 5)] for b in bands],
                               text=[f"{c / n * 100:.0f}%" for c in counts], textposition="outside", cliponaxis=False,
                               textfont=dict(color=TEXT1), customdata=counts,
                               hovertemplate="<b>%{x}</b><br>%{y:.1f}% of students (%{customdata})<extra></extra>"))
        fig.update_yaxes(title="% of students", range=[0, max(counts.max() / n * 100, 1) * 1.25])
        show(style(fig, height=300, legend=False), "u_dist")
    with c2, card("ugrp"):
        card_head("Compare groups", "Mean hours per day for the chosen activity")
        grp_name = st.selectbox("Compare by", list(GROUP_OPTIONS), key="u_grp")
        gcol, gorder = GROUP_OPTIONS[grp_name]
        show(group_mean_bar(df, gcol, gorder, act), "u_grpbar")

    with card("ubox"):
        card_head("Variability of daily internet use", "Box plots by group · dashed line = mean")
        t = st.columns([1.2, 1.2, 2.5], vertical_alignment="bottom")
        box_grp = t[0].selectbox("Box plot by", ["Age group", "Gender", "Device group"], key="u_boxgrp")
        drop_out = t[1].toggle("Remove IQR outliers", key="u_iqr",
                               help="Removes values outside Q1 − 1.5×IQR … Q3 + 1.5×IQR within each group (notebook 2.4).")
        gcol, gorder = GROUP_OPTIONS[box_grp]
        box_df = df
        if box_grp == "Gender":
            box_df, gorder = df[df["gender"].isin(["Female", "Male"])], ["Female", "Male"]
        if drop_out and len(box_df):
            before = len(box_df)
            box_df = iqr_filter(box_df, gcol)
            t[2].caption(f"{before - len(box_df)} outlier(s) removed · {len(box_df)} students shown")
        fig = go.Figure()
        for gname in gorder:
            vals = box_df.loc[box_df[gcol] == gname, "total_hours"]
            if len(vals):
                fig.add_trace(go.Box(y=vals, name=f"{GENDER_LABEL.get(gname, AGE_LABEL.get(gname, gname))} (n={len(vals)})",
                                     marker_color=BLUE, fillcolor="rgba(59,130,246,0.30)", boxmean=True,
                                     boxpoints="outliers", line=dict(width=2), hovertemplate="%{y} h/day<extra></extra>"))
        fig.update_yaxes(title="Total hours per day", range=[0.8, 6.0])
        show(style(fig, height=340, legend=False), "u_box")
        if box_grp == "Gender":
            st.caption("'Prefer not to say' (2 students) is left out of the gender box plot: two values can't form a box.")


# ---------------------------------------------------------------------------
# 03 Devices
# ---------------------------------------------------------------------------
def page_devices():
    section("Access & devices", "How students connect", "Students could select more than one device.")
    if n == 0:
        return no_match()
    dev = device_numbers(df)
    cols = [DEVICE_COLOURS[i] for i in dev.index]
    c1, c2 = st.columns([1, 1.05])
    with c1, card("dshare"):
        card_head("Share of device selections", f"Distribution of {int(dev.sum())} device selections")
        donut(list(dev.index), list(dev.values), cols, int(dev.sum()), "SELECTIONS", "d_donut")
        legend_html(list(dev.index), list(dev.values), cols)
    with c2, card("dbreak"):
        card_head("Device breakdown", f"How many of the {n} students selected each device")
        bar_rows([(l, f"{v} ({v / n * 100:.1f}%)", v / n, DEVICE_COLOURS[l]) for l, v in dev.items()],
                 "Percentages can total more than 100% because multiple choices were allowed.")
        if clean_report.get("device_detail_lost"):
            html(f"<div class='foot'>{clean_report['device_detail_lost']} students' device answers were saved as "
                 "'Other combination' in the cleaned file; load the raw survey CSV (sidebar → Data source) to count them exactly.</div>")

    c3, c4 = st.columns(2)
    with c3, card("dgroup"):
        card_head("Device combinations", "Each student counted once")
        dg = df["device_group"].value_counts().reindex(DEVICE_GROUP_ORDER).fillna(0).astype(int)
        gcols = [BLUE, GREEN, ORANGE]
        donut(list(dg.index), list(dg.values), gcols, n, "STUDENTS", "d_grp")
        legend_html(list(dg.index), list(dg.values), gcols)
    with c4, card("dmean"):
        card_head("Daily hours by device group", "Mean total hours per day")
        show(group_mean_bar(df, "device_group", DEVICE_GROUP_ORDER), "d_mean")
    st.caption("'Other combination' has very few students, so its averages are less reliable.")


# ---------------------------------------------------------------------------
# 04 Purposes
# ---------------------------------------------------------------------------
def page_purposes():
    section("Online activities", "Why students go online", "The survey allows students to select multiple purposes.")
    if n == 0:
        return no_match()
    pur = purpose_numbers(df)
    cols = [PURPOSE_COLOURS[i] for i in pur.index]
    c1, c2 = st.columns([1, 1.05])
    with c1, card("pshare"):
        card_head("Share of purpose mentions", f"Pie chart of {int(pur.sum())} mentions, not a percentage of students")
        donut(list(pur.index), list(pur.values), cols, int(pur.sum()), "MENTIONS", "p_donut")
        legend_html(list(pur.index), list(pur.values), cols)
    with c2, card("pbreak"):
        card_head("Purpose breakdown", f"How many of the {n} selected students mentioned each purpose")
        bar_rows([(l, f"{v} ({v / n * 100:.1f}%)", v / n, PURPOSE_COLOURS[l]) for l, v in pur.items()],
                 "Percentages of students can total more than 100% because multiple choices were allowed.")

    c3, c4 = st.columns([1, 1.4])
    with c3, card("pnum"):
        card_head("Purposes per student", f"Mean {df['number_of_purposes'].mean():.2f} · "
                                          f"{(df['number_of_purposes'] > 1).mean() * 100:.0f}% chose more than one")
        npc = df["number_of_purposes"].value_counts().reindex(range(1, 6), fill_value=0)
        fig = go.Figure(go.Bar(x=[str(i) for i in npc.index], y=npc.values, marker_color=BLUE, marker_cornerradius=4,
                               text=npc.values, textposition="outside", cliponaxis=False, textfont=dict(color=TEXT1),
                               hovertemplate="%{x} purpose(s): %{y} students<extra></extra>"))
        fig.update_xaxes(title="Number of purposes selected")
        fig.update_yaxes(visible=False, range=[0, max(npc.max(), 1) * 1.25])
        show(style(fig, height=280, legend=False), "p_num")
    with c4, card("phours"):
        card_head("Time spent by purpose chosen", "Mean hours per day among students who chose each purpose")
        rows = []
        for col, label in PURPOSE_SHORT.items():
            sub = df[df[col] == 1]
            if len(sub) >= 3:
                for h, hl in zip(HOURS_COLS[1:], ["Academic", "Social & communication", "Entertainment"]):
                    rows.append({"purpose": f"{label}<br>n={len(sub)}", "activity": hl, "mean": sub[h].mean()})
        if rows:
            fig = px.bar(pd.DataFrame(rows), x="purpose", y="mean", color="activity", barmode="group",
                         color_discrete_sequence=[BLUE, GREEN, ORANGE],
                         labels={"purpose": "", "mean": "Mean hours per day", "activity": ""})
            fig.update_traces(marker_cornerradius=3, hovertemplate="<b>%{x}</b><br>%{y:.2f} h/day<extra></extra>")
            show(style(fig, height=300), "p_hours")
            st.caption("Purposes chosen by fewer than 3 students in the current selection are hidden.")
        else:
            st.info("Too few students in this selection to compare purposes.")


# ---------------------------------------------------------------------------
# 05 Insights
# ---------------------------------------------------------------------------
def page_insights():
    section("A closer look", "Usage insights", "Switch between what students do and how they connect.")
    if n == 0:
        return no_match()
    pur, dev = purpose_numbers(df), device_numbers(df)
    mode = st.session_state.get("ins_mode") or "Purposes"
    c1, c2 = st.columns([1.65, 1])
    with c1, card("breakdown"):
        a, b = st.columns([2.2, 1], vertical_alignment="center")
        with a:
            html("<div class='eyebrow' style='margin-bottom:8px'>Breakdown</div>"
                 f"<div class='card-title' style='font-size:1.4rem'>{'Why students go online' if mode == 'Purposes' else 'How students connect'}</div>"
                 f"<div class='card-sub'>Students could choose more than one {'purpose' if mode == 'Purposes' else 'device'}.</div>")
        with b:
            st.segmented_control("View", ["Purposes", "Devices"], key="ins_mode", label_visibility="collapsed",
                                 on_change=keep_value, args=("ins_mode", "Purposes"))
        st.write("")
        src, colours = (pur, PURPOSE_COLOURS) if mode == "Purposes" else (dev, DEVICE_COLOURS)
        bar_rows([(l, f"{v} ({v / n * 100:.1f}%)", v / n, colours[l]) for l, v in src.items()])
    with c2:
        html(f"<div class='hl' style='background:#1d3461'><div class='k' style='color:#93bbff'>TOP ACTIVITY</div>"
             f"<div class='v'>{pur.idxmax()}</div><div class='s'>{pur.max()} of {n} students · {pur.max() / n * 100:.1f}%</div></div>")
        st.write("")
        html(f"<div class='hl' style='background:#173d2e'><div class='k' style='color:#4ade80'>MOST USED DEVICE</div>"
             f"<div class='v'>{dev.idxmax()}</div><div class='s'>{dev.max()} of {n} students · {dev.max() / n * 100:.1f}%</div></div>")
        st.button("View daily usage distribution ↗", key="lnk_dist", type="tertiary", on_click=goto, args=("Overview",))

    with card("closer"):
        a, b = st.columns([3, 1])
        with a:
            html("<div class='eyebrow' style='margin-bottom:8px'>Descriptive statistics</div>"
                 "<div class='card-title' style='font-size:1.3rem'>A closer look at daily hours</div>")
        with b:
            html(f"<div class='gk' style='text-align:right;padding-top:22px'>{n} RESPONSES</div>")
        s = df["total_hours"]
        tiles = [("Median", f"{s.median():.2f} hrs"), ("Mode", f"{s.mode().iloc[0]:.2f} hrs"),
                 ("Standard deviation", f"{s.std():.2f} hrs" if n > 1 else "–"),
                 ("Lowest band midpoint", f"{s.min():.2f} hrs"), ("Highest band midpoint", f"{s.max():.2f} hrs")]
        cols = st.columns(5)
        for col, (l, v) in zip(cols, tiles):
            col.markdown(f"<div class='stat'><div class='l'>{l}</div><div class='v'>{v}</div></div>", unsafe_allow_html=True)
        html(f"<div class='eyebrow' style='margin-top:14px;color:{MUTED}'>Estimated time by activity</div>")
        cols = st.columns(3)
        for col, c, l in zip(cols, HOURS_COLS[1:], ["Academic / day", "Social & communication / day", "Entertainment / day"]):
            col.markdown(f"<div class='act'><div class='v'>{df[c].mean():.2f} hrs</div><div class='l'>{l}</div></div>",
                         unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3, card("corr"):
        html("<div class='eyebrow' style='margin-bottom:8px'>Relationships</div>"
             "<div class='card-title' style='font-size:1.4rem'>Usage correlations</div>"
             f"<div class='card-sub'>Spearman correlation on all {N_ALL} responses · band midpoints</div>")
        corr = data[HOURS_COLS].corr(method="spearman")
        names = ["Daily", "Academic", "Social", "Entertainment"]
        cells = "<div></div>" + "".join(f"<div class='h'>{nm}</div>" for nm in names)
        for i, nm in enumerate(names):
            cells += f"<div class='r'>{nm}</div>"
            for j in range(4):
                r = corr.iloc[i, j]
                alpha = 0.25 + 0.75 * abs(r)
                base = "59,130,246" if r >= 0 else "216,74,74"
                cells += f"<div class='c' style='background:rgba({base},{alpha:.2f})' title='ρ = {r:.3f}'>{r:.2f}</div>"
        html(f"<div class='hx' style='grid-template-columns:1.2fr repeat(4,1fr);margin-top:18px'>{cells}</div>"
             "<div class='foot' style='margin-top:14px'>Association does not establish causation. "
             "Brighter cells = stronger relationship.</div>")
    with c4, card("tests"):
        html("<div class='eyebrow' style='margin-bottom:8px'>Exploratory hypothesis checks</div>"
             "<div class='card-title' style='font-size:1.4rem'>Do groups differ?</div>"
             "<div class='card-sub'>Tests across all valid responses, not the current filter.</div>")
        f_h = data.loc[data.gender == "Female", "total_hours"]
        m_h = data.loc[data.gender == "Male", "total_hours"]
        mw = stats.mannwhitneyu(f_h, m_h, alternative="two-sided")
        groups = [data.loc[data.age_group == a, "total_hours"] for a in AGE_ORDER]
        kw = stats.kruskal(*[g for g in groups if len(g) >= 2])
        gm = data[data.gender.isin(["Female", "Male"])]
        sp_g = spearman(gm["gender"].map({"Male": 1, "Female": 2}), gm["total_hours"])
        sp_a = spearman(data["age_group"].map({a: i + 1 for i, a in enumerate(AGE_ORDER)}), data["total_hours"])
        rows = [("Female vs Male", f"Two-sided Mann–Whitney U · n = {len(f_h)} / {len(m_h)}", mw.pvalue),
                ("Across four age groups", "Kruskal–Wallis · n = " + " / ".join(str(len(g)) for g in groups), kw.pvalue)]
        if sp_g:
            rows.append(("H1 · Gender and daily use", f"Spearman ρ = {sp_g[0]:.3f} · n = {sp_g[2]}", sp_g[1]))
        if sp_a:
            rows.append(("H2 · Age group and daily use", f"Spearman ρ = {sp_a[0]:.3f} · n = {sp_a[2]}", sp_a[1]))
        html("".join(f"<div class='test'><div><div class='t'>{t}</div><div class='d'>{d}</div></div>"
                     f"<div class='p'>p = {p:.4f}</div></div>" for t, d, p in rows))
        g_txt = ("there is evidence of a female/male difference" if mw.pvalue < 0.05
                 else "there is no clear evidence of a female/male difference")
        a_txt = ("age-group distributions show evidence of a difference, and daily use rises with age"
                 if kw.pvalue < 0.05 else "age groups do not show a clear difference")
        html(f"<div class='concl'>At the exploratory 0.05 threshold, {g_txt}; {a_txt}. "
             f"So H1 (gender) is {'supported' if mw.pvalue < 0.05 else 'not supported'} and H2 (age group) is "
             f"{'supported' if kw.pvalue < 0.05 else 'not supported'}.</div>"
             "<div class='foot' style='margin-top:12px'>Exploratory tests use coded ranges, not exact hours. "
             "“Prefer not to say” is excluded only from the two-group gender tests. A p-value does not measure "
             "the size of a difference.</div>")

    # Written findings
    section("Findings", "What the data tells us", "Recalculated for your selection.")
    mean_t, med_t = df["total_hours"].mean(), df["total_hours"].median()
    over5 = (df["total_hours"] == 5.5).mean() * 100
    over4 = (df["total_hours"] >= 4.5).mean() * 100
    act_means = df[HOURS_COLS[1:]].mean().rename(HOURS_LABELS).sort_values(ascending=False)
    insight("RQ1 · How long are students online?",
            f"Students in this selection spend about <b>{mean_t:.2f} hours a day</b> online (median {med_t:.1f} h). "
            f"<b>{over4:.1f}%</b> report 4 hours or more and <b>{over5:.1f}%</b> report more than 5 hours, the top "
            f"option on the form, so the true average is probably a little higher.",
            "For most students the internet takes up a large part of the day, comparable to time spent in class.")
    insight("RQ2 · What do they use it for?",
            f"<b>{pur.idxmax()}</b> is the most common purpose ({pur.max() / n * 100:.1f}%), and "
            f"{(df['number_of_purposes'] > 1).mean() * 100:.1f}% use the internet for more than one purpose. But time "
            f"tells a different story: <b>{act_means.index[0].lower()}</b> has the highest mean hours "
            f"({act_means.iloc[0]:.2f} h), while academic use averages {df['academic_hours'].mean():.2f} h.",
            "Students say the internet is for learning, but more of their hours go to social and entertainment use. "
            "That gap is where guidance on balanced use can help.", ORANGE)
    insight("RQ3 · Which devices?",
            f"<b>{dev['Smartphone'] / n * 100:.1f}%</b> use a smartphone and "
            f"{(df['device_group'] == 'Smartphone only').mean() * 100:.1f}% rely on a smartphone alone; "
            f"{dev['Laptop / Desktop'] / n * 100:.1f}% also use a laptop or desktop.",
            "Learning materials, LMS pages and assessments should work well on a phone screen.", TEAL)
    by_age = df.groupby("age_group")["total_hours"].mean().reindex(AGE_ORDER).dropna()
    if len(by_age) >= 2:
        insight("RQ4 · Do groups differ?",
                f"Daily use rises with age, from <b>{by_age.iloc[0]:.2f} h</b> ({AGE_LABEL[by_age.index[0]]}) to "
                f"<b>{by_age.iloc[-1]:.2f} h</b> ({AGE_LABEL[by_age.index[-1]]}). Across all students this age effect is "
                f"statistically significant (Kruskal–Wallis p = {kw.pvalue:.4f}; Spearman ρ = {sp_a[0]:.3f}), while the "
                f"female/male gap is not (p = {mw.pvalue:.4f}).",
                "Age, not gender, is the difference to plan around: older students, deeper into their programmes, "
                "are online the most.", PURPLE)
    r = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1)).stack().sort_values(key=np.abs, ascending=False)
    (a1, b1), v1 = r.index[0], r.iloc[0]
    insight("RQ5 · What relationships stand out?",
            f"Total daily use moves most closely with <b>{HOURS_LABELS[b1 if a1 == 'total_hours' else a1].lower()}</b> time "
            f"(ρ = {v1:.2f}), while academic time is almost unrelated to total time (ρ = {corr.loc['total_hours', 'academic_hours']:.2f}).",
            "Students who are online the longest are mainly spending the extra time on social media, not study.", YELLOW)

    with card("recs"):
        card_head("Recommendations")
        st.markdown("""
- **Teachers:** design online tasks and resources mobile-first, and point students to quality academic sources.
- **Students:** set daily limits, turn off non-essential notifications during study time, and plan academic time online deliberately.
- **The college:** run digital well-being and time-management sessions, with extra attention to students aged 21 and above.
- **Future research:** ask for exact hours instead of ranges, survey a larger and more balanced sample, and link usage to academic results.
""")
    with card("limits"):
        card_head("Limitations")
        st.markdown(f"""
- Self-reported data from {N_ALL} students at one college; results may not represent all students.
- Hours are range midpoints and "more than 5 hours" is capped at 5.5, which understates heavy use.
- Some groups are small ('Prefer not to say': 2 students; 'Other combination' devices: 5), so their averages are unstable.
- The analysis shows associations, not causes.
""")


{
    "Overview": page_overview, "Usage": page_usage, "Devices": page_devices, "Purposes": page_purposes,
    "Insights": page_insights,
}[st.session_state.get("page") or "Overview"]()

html(f"<div class='foot' style='text-align:center;margin-top:34px'>Group 6 · B.Ed. ICT · Samtse College of Education · "
     f"PRG405 Introduction to Data Science</div>")
