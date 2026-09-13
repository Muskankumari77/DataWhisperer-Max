import streamlit as st


def inject_css(theme="dark"):
    light = theme == "light"
    c = {
        "bg": "#f7f0e7" if light else "#0d120e",
        "surface": "#fffaf4" if light else "#151b15",
        "surface2": "#f3e9dc" if light else "#1b241b",
        "sidebar": "#eee3d5" if light else "#0b100c",
        "text": "#191714" if light else "#f5eee6",
        "muted": "#6f675e" if light else "#b8b1a8",
        "border": "#d8ccbd" if light else "#303a31",
        "accent": "#d66f4b",
        "accent2": "#b95739",
        "green": "#43a967",
        "tablehead": "#f2d7c6" if light else "#3a281f",
        "shadow": "0 12px 32px rgba(0,0,0,.16)" if not light else "0 12px 32px rgba(77,55,34,.08)",
    }
    css = f"""
<style>
:root {{ --bg:{c['bg']}; --surface:{c['surface']}; --surface2:{c['surface2']}; --sidebar:{c['sidebar']}; --text:{c['text']}; --muted:{c['muted']}; --border:{c['border']}; --accent:{c['accent']}; --accent2:{c['accent2']}; --green:{c['green']}; --tablehead:{c['tablehead']}; --shadow:{c['shadow']}; }}
[data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{ background:var(--bg)!important; color:var(--text)!important; }}
#MainMenu, footer {{ visibility:hidden; }}
section[data-testid="stSidebar"] {{ background:var(--sidebar)!important; border-right:1px solid var(--border)!important; }}
section[data-testid="stSidebar"] > div {{ background:var(--sidebar)!important; }}
section[data-testid="stSidebar"] .block-container {{ padding:22px 20px!important; }}
.stButton > button {{ border-radius:12px!important; border:1px solid var(--border)!important; background:var(--surface)!important; color:var(--text)!important; font-weight:650!important; }}
.stButton > button:hover {{ border-color:var(--accent)!important; color:var(--accent)!important; }}
.stButton > button[kind="primary"] {{ background:var(--accent)!important; color:#fff!important; border-color:var(--accent)!important; }}
div[data-baseweb="input"], div[data-baseweb="select"] {{ background:var(--surface)!important; border-color:var(--border)!important; border-radius:10px!important; }}
input, textarea {{ color:var(--text)!important; background:var(--surface)!important; }}
label, label p, div[data-testid="stRadio"] label, div[data-testid="stRadio"] label p {{ color:var(--text)!important; }}
[data-testid="stFileUploaderDropzone"] {{ background:var(--surface2)!important; border:1px dashed var(--border)!important; border-radius:10px!important; }}
[data-testid="stFileUploaderDropzone"] span {{ color:var(--text)!important; }}
.dw-brand {{ display:flex;align-items:center;gap:12px;margin-bottom:20px; }}
.dw-brand-mark {{ width:44px;height:44px;border-radius:13px;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:21px;box-shadow:0 6px 18px rgba(214,111,75,.25); }}
.dw-brand-name {{ font-size:18px;font-weight:800;color:var(--text); }} .dw-brand-name span {{color:var(--accent);}} .dw-brand-sub {{font-size:11px;color:var(--muted);margin-top:3px;}}
.dw-side-title {{font-size:10px;font-weight:800;letter-spacing:1.3px;color:var(--text);margin:22px 0 9px;}}
.dw-main-head {{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;}}
.dw-main-brand {{display:flex;align-items:center;gap:12px;}} .dw-home {{font-size:25px;}} .dw-main-title {{font-size:17px;font-weight:800;color:var(--text);}} .dw-main-sub {{font-size:10px;color:var(--muted);margin-top:3px;}}
.dw-status {{padding:8px 13px;border:1px solid var(--border);border-radius:999px;color:var(--text);font-size:10px;background:var(--surface);}} .dw-dot {{display:inline-block;width:7px;height:7px;border-radius:50%;background:#52d991;margin-right:7px;}}
.dw-card {{background:var(--surface);border:1px solid var(--border);border-radius:14px;box-shadow:var(--shadow);padding:15px;}}
.dw-source-banner {{display:flex;align-items:center;gap:14px;min-height:72px;margin-bottom:12px;}} .dw-source-icon {{width:48px;height:48px;border-radius:12px;background:var(--accent);color:white;display:flex;align-items:center;justify-content:center;font-size:22px;}} .dw-source-title {{font-size:16px;font-weight:800;color:var(--text);}} .dw-source-sub {{font-size:10px;color:var(--muted);margin-top:4px;}} .dw-connected {{color:var(--green);font-size:10px;font-weight:750;border:1px solid var(--green);border-radius:999px;padding:5px 9px;margin-left:8px;}}
.dw-card-title {{font-size:14px;font-weight:800;color:var(--text);margin:0 0 10px;}} .dw-card-title small {{font-size:9px;color:var(--muted);font-weight:500;margin-left:7px;}}
.dw-info-row {{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:10px;}} .dw-info-row:last-child {{border-bottom:0;}} .dw-info-row span {{color:var(--muted);}} .dw-info-row strong {{color:var(--text);}}
.dw-quality {{display:flex;align-items:center;gap:13px;}} .dw-ring {{width:54px;height:54px;border:4px solid var(--green);border-radius:50%;display:flex;align-items:center;justify-content:center;color:var(--text);font-size:12px;font-weight:800;}} .dw-good {{color:var(--green);font-weight:800;font-size:13px;}} .dw-muted {{color:var(--muted);font-size:9px;margin-top:3px;}}
.dw-type-row {{display:flex;justify-content:space-between;padding:5px 0;color:var(--muted);font-size:10px;}} .dw-type-row b {{color:var(--text);}}
.dw-question {{font-size:10px;color:var(--muted);margin:14px 0 7px;}}
.dw-empty {{min-height:350px;display:flex;align-items:center;justify-content:center;text-align:center;border:1px solid var(--border);border-radius:16px;background:var(--surface);box-shadow:var(--shadow);}} .dw-empty h2 {{color:var(--text);font-size:24px;margin:10px 0 7px;}} .dw-empty p {{color:var(--muted);font-size:11px;}}
[data-testid="stDataFrame"] {{border:1px solid var(--border);border-radius:10px;overflow:hidden;}}
div[data-testid="stChatInput"] > div {{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:14px!important;}} div[data-testid="stChatInput"] textarea {{background:transparent!important;color:var(--text)!important;}}
[data-testid="stChatMessage"] {{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important;}}
/* =====================================================
   FINAL TYPOGRAPHY + QUESTION AREA
   ===================================================== */

.dw-brand-name {{
    font-size: 20px !important;
}}

.dw-brand-sub {{
    font-size: 12px !important;
}}

.dw-side-title {{
    font-size: 11px !important;
}}

.dw-main-title {{
    font-size: 19px !important;
}}

.dw-main-sub {{
    font-size: 12px !important;
}}

.dw-status {{
    font-size: 11px !important;
}}

.dw-source-title {{
    font-size: 18px !important;
}}

.dw-source-sub {{
    font-size: 12px !important;
}}

.dw-card-title {{
    font-size: 16px !important;
}}

.dw-card-title small {{
    font-size: 11px !important;
}}

.dw-info-row {{
    font-size: 12px !important;
}}

.dw-muted {{
    font-size: 11px !important;
}}

.dw-good {{
    font-size: 15px !important;
}}

.dw-type-row {{
    font-size: 12px !important;
}}

.dw-question-title {{
    font-size: 15px !important;
    font-weight: 750 !important;
    color: var(--text) !important;
    margin: 20px 0 9px 2px !important;
}}

/* Question input */

div[data-testid="stTextInput"] input {{
    height: 48px !important;
    font-size: 14px !important;
    color: var(--text) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}}

div[data-testid="stTextInput"] input::placeholder {{
    color: var(--muted) !important;
    opacity: 1 !important;
    font-size: 13px !important;
}}

/* Send button */

div[data-testid="stFormSubmitButton"] button {{
    height: 48px !important;
    min-width: 48px !important;
    border-radius: 12px !important;
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    color: #ffffff !important;
    font-size: 19px !important;
    font-weight: 800 !important;
}}

div[data-testid="stFormSubmitButton"] button:hover {{
    background: var(--accent2) !important;
    border-color: var(--accent2) !important;
}}

</style>
"""
    st.markdown(css, unsafe_allow_html=True)
