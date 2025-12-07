# web_ui.py
# Small Streamlit app for the paging simulator + an HTML/CSS animated result card
# Usage:
# 1) pip install streamlit
# 2) streamlit run web_ui.py
#
# This file includes simple FIFO/LRU/OPTIMAL/CLOCK implementations
# and an embedded HTML/CSS effect showing algorithm name + faults.

import streamlit as st
from collections import deque, OrderedDict
import html

st.set_page_config(page_title="Virtual Memory Visual", layout="centered")

# ---------- Simple algorithm implementations (same as earlier) ----------
def fifo(reference, frames_count):
    frames = deque()
    faults = 0
    for page in reference:
        if page not in frames:
            faults += 1
            if len(frames) < frames_count:
                frames.append(page)
            else:
                frames.popleft()
                frames.append(page)
    return faults

def lru(reference, frames_count):
    frames = OrderedDict()
    faults = 0
    for page in reference:
        if page in frames:
            frames.pop(page)
            frames[page] = True
        else:
            faults += 1
            if len(frames) < frames_count:
                frames[page] = True
            else:
                frames.popitem(last=False)
                frames[page] = True
    return faults

def optimal(reference, frames_count):
    frames = []
    faults = 0
    for i, page in enumerate(reference):
        if page in frames:
            continue
        faults += 1
        if len(frames) < frames_count:
            frames.append(page)
        else:
            farthest = -1
            victim = 0
            for idx, p in enumerate(frames):
                try:
                    nxt = reference.index(p, i+1)
                except ValueError:
                    nxt = float('inf')
                if nxt > farthest:
                    farthest = nxt
                    victim = idx
            frames[victim] = page
    return faults

def clock(reference, frames_count):
    frames = [None]*frames_count
    use = [0]*frames_count
    ptr = 0
    faults = 0
    for page in reference:
        if page in frames:
            use[frames.index(page)] = 1
        else:
            faults += 1
            while True:
                if frames[ptr] is None:
                    frames[ptr] = page
                    use[ptr] = 1
                    ptr = (ptr + 1) % frames_count
                    break
                if use[ptr] == 0:
                    frames[ptr] = page
                    use[ptr] = 1
                    ptr = (ptr + 1) % frames_count
                    break
                use[ptr] = 0
                ptr = (ptr + 1) % frames_count
    return faults

# ---------- UI ----------
st.title("Virtual Memory — Quick Simulator ✨")
st.write("Enter a reference string and choose frames. Press Run to see page faults and a small animated card.")

# Input controls
ref_input = st.text_input("Reference string (space-separated integers)", value="7 0 1 2 0 3 0 4 2 3 0 3 2")
frames = st.slider("Number of frames", min_value=1, max_value=8, value=3)
algo = st.selectbox("Choose algorithm", ["FIFO", "LRU", "OPTIMAL", "CLOCK", "ALL"])

col1, col2 = st.columns([2,1])

with col1:
    if st.button("Run"):
        # parse
        try:
            reference = [int(x) for x in ref_input.strip().split() if x.strip()!='']
            if len(reference) == 0:
                st.warning("Reference string empty — using demo default.")
                reference = [7,0,1,2,0,3,0,4,2,3,0,3,2]
        except Exception:
            st.error("Invalid reference string. Use space-separated integers.")
            reference = [7,0,1,2,0,3,0,4,2,3,0,3,2]

        results = {}
        if algo == "FIFO" or algo == "ALL":
            results["FIFO"] = fifo(reference, frames)
        if algo == "LRU" or algo == "ALL":
            results["LRU"] = lru(reference, frames)
        if algo == "OPTIMAL" or algo == "ALL":
            results["OPTIMAL"] = optimal(reference, frames)
        if algo == "CLOCK" or algo == "ALL":
            results["CLOCK"] = clock(reference, frames)

        # Show table
        st.subheader("Results")
        for name, faults in results.items():
            st.write(f"*{name}* → Page faults: *{faults}*")

        # Choose one to show on animated card (prefer selected, else first)
        card_name = algo if algo != "ALL" else list(results.keys())[0]
        card_faults = results[card_name]

        # Escape values for safe embedding
        safe_name = html.escape(card_name)
        safe_faults = html.escape(str(card_faults))

        # ---------- HTML + CSS animated card ----------
        card_html = f"""
        <div style="display:flex;justify-content:center;margin-top:18px;">
          <div class="card">
            <div class="glass">
              <h2 class="title">{safe_name} Algorithm</h2>
              <p class="sub">Page Faults</p>
              <p class="count">{safe_faults}</p>
            </div>
          </div>
        </div>

        <style>
        /* Card container */
        .card {{
          width: 320px;
          height: 180px;
          border-radius: 16px;
          background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
          box-shadow: 0 8px 30px rgba(2,6,23,0.6);
          position: relative;
          overflow: hidden;
          padding: 18px;
          transform: translateZ(0);
        }}

        /* animated gradient blobs */
        .card::before, .card::after {{
          content: "";
          position: absolute;
          width: 220px;
          height: 220px;
          background: radial-gradient(circle at 30% 30%, rgba(255, 115, 135, 0.18), transparent 30%),
                      radial-gradient(circle at 70% 70%, rgba(120, 99, 255, 0.14), transparent 30%);
          filter: blur(18px);
          animation: float 6s ease-in-out infinite;
          opacity: 0.9;
        }}
        .card::before {{ top: -40px; left: -60px; }}
        .card::after {{ bottom: -40px; right: -60px; animation-delay: 3s; }}

        @keyframes float {{
          0% {{ transform: translateY(0px) rotate(0deg); }}
          50% {{ transform: translateY(-12px) rotate(6deg); }}
          100% {{ transform: translateY(0px) rotate(0deg); }}
        }}

        .glass {{
          position: relative;
          z-index: 2;
          color: white;
          font-family: "Segoe UI", Roboto, Arial, sans-serif;
          height: 100%;
          display:flex;
          flex-direction:column;
          justify-content:center;
          align-items:center;
          text-align:center;
        }}

        .title {{
          margin: 0;
          font-size: 20px;
          letter-spacing: 0.6px;
          text-transform: uppercase;
          color: #fff;
          opacity: 0.95;
        }}

        .sub {{
          margin: 6px 0 2px 0;
          color: #e6e6e6;
          opacity: 0.8;
        }}

        .count {{
          margin: 4px 0 0 0;
          font-size: 46px;
          font-weight: 700;
          background: linear-gradient(90deg, #fff, #ffd27f);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }}
        </style>
        """
        # embed HTML
        st.components.v1.html(card_html, height=260, scrolling=False)

with col2:
    st.markdown("### Quick tips")
    st.write("- Use small reference strings (10-15 numbers) for easy demonstration.")
    st.write("- Take a screenshot of the animated card as evidence for your GitHub.")
    st.write("- To save logs, use the console run or copy results shown here.")

st.markdown("---")
st.caption("This small UI combines Python simulation with a lightweight HTML/CSS effect for presentation. Good for screenshots in reports!")