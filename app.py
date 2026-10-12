import datetime
import json
import streamlit as st

st.set_page_config(
    page_title="ระบบสร้างทิคเก็ต GPS",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom styling for a clean professional look
st.markdown(
    """
    <style>
    .main-title {
        color: #38bdf8;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .section-header {
        color: #38bdf8;
        font-size: 16px;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">ระบบสร้างทิคเก็ต GPS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">กรุณากรอกข้อมูลด้านล่างเพื่อสร้างทิคเก็ตสำหรับ Dynamics 365</div>', unsafe_allow_html=True)

# Session state initialization
if "requests" not in st.session_state:
    st.session_state.requests = []
if "generated_ticket" not in st.session_state:
    st.session_state.generated_ticket = None

# Base Form Fields
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        server_ip = st.text_input("Server IP *", placeholder="122.155.12.70", key="server_ip")
        company_id = st.text_input("Company ID *", placeholder="ระบุ Company ID", key="company_id")
        user_name = st.text_input("User Name", key="user_name")
        system_name = st.text_input("ชื่อระบบ", key="system_name")
    with col2:
        server_name = st.text_input("Server Name", placeholder="Onetrack", key="server_name")
        company_name = st.text_input("Company Name", key="company_name")
        password = st.text_input("Password", key="password")
        link = st.text_input("Link", key="link")

    report_name = st.text_input("ระบุชื่อรายงาน", placeholder="เช่น รายงานการเดินทาง", key="report_name")
    details = st.text_area("รายละเอียด", rows=3, key="details")

st.markdown('<div class="section-header">ข้อมูลวันที่และรถที่ต้องการตรวจสอบ</div>', unsafe_allow_html=True)

# Add Date & Vehicle Request Row
req_col1, req_col2, req_col3, req_col4 = st.columns([2, 1.5, 1.5, 1])

with req_col1:
    req_mid = st.text_input("MID (เว้นว่างไว้หากต้องการดึงข้อมูลทั้งบริษัท)", placeholder="เช่น 12345 หรือเว้นว่าง", key="input_mid")
with req_col2:
    today = datetime.date.today()
    req_start = st.date_input("วันที่เริ่มต้น *", value=today, max_value=today, format="DD/MM/YYYY", key="input_start")
with req_col3:
    req_end = st.date_input("วันที่สิ้นสุด *", value=today, max_value=today, format="DD/MM/YYYY", key="input_end")
with req_col4:
    st.write("")
    st.write("")
    if st.button("+ เพิ่ม", use_container_width=True):
        if req_start > req_end:
            st.error("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        else:
            mid_val = req_mid.strip() if req_mid.strip() else "ALL"
            st.session_state.requests.append({
                "mid": mid_val,
                "start": req_start,
                "end": req_end,
            })
            st.rerun()

# Display current requests list
if st.session_state.requests:
    st.markdown("**รายการที่เพิ่มแล้ว:**")
    for idx, item in enumerate(st.session_state.requests):
        col_info, col_del = st.columns([5, 1])
        with col_info:
            start_str = item["start"].strftime("%d/%m/%Y")
            end_str = item["end"].strftime("%d/%m/%Y")
            st.info(f"ลำดับที่ {idx + 1} | MID: {item['mid']} | วันที่: {start_str} ถึง {end_str}")
        with col_del:
            if st.button("ลบ", key=f"del_{idx}", use_container_width=True):
                st.session_state.requests.pop(idx)
                st.rerun()

st.divider()

# Generation Action
col_action1, col_action2 = st.columns([3, 1])

with col_action1:
    generate_clicked = st.button("สร้างทิคเก็ต (Generate Ticket)", type="primary", use_container_width=True)
with col_action2:
    if st.button("ล้างรายการทั้งหมด (Clear Requests)", use_container_width=True):
        st.session_state.requests = []
        st.session_state.generated_ticket = None
        st.rerun()

if generate_clicked:
    # Prepare requests including current active inputs if list is empty
    active_requests = list(st.session_state.requests)
    if not active_requests and req_start and req_end:
        mid_val = req_mid.strip() if req_mid.strip() else "ALL"
        active_requests.append({
            "mid": mid_val,
            "start": req_start,
            "end": req_end,
        })

    has_mid = any(r["mid"] and r["mid"] != "ALL" for r in active_requests)

    if not server_ip.strip():
        st.error("กรุณาระบุ Server IP")
    elif len(active_requests) == 0:
        st.error("กรุณาระบุวันที่เริ่มต้นและสิ้นสุดอย่างน้อย 1 รายการ")
    elif not company_id.strip() and not has_mid:
        st.error("กรุณาระบุอย่างน้อย Company ID หรือ MID")
    else:
        # Build ticket text
        lines = ["รายละเอียด"]
        if server_name.strip():
            lines.append(f"Server Name : {server_name.strip()}")
        lines.append(f"Server IP : {server_ip.strip()}")
        if company_name.strip():
            lines.append(f"company name : {company_name.strip()}")
        if company_id.strip():
            lines.append(f"company id : {company_id.strip()}")
        if user_name.strip():
            lines.append(f"User name : {user_name.strip()}")
        if password.strip():
            lines.append(f"Password : {password.strip()}")
        if system_name.strip():
            lines.append(f"ชื่อระบบ : {system_name.strip()}")
        if link.strip():
            lines.append(f"link : {link.strip()}")
        if details.strip():
            lines.append(f"รายละเอียด : {details.strip()}")
        lines.append("")

        # Group by MID
        mid_groups = {}
        for r in active_requests:
            mid = r["mid"]
            start_str = r["start"].strftime("%d/%m/%Y")
            end_str = r["end"].strftime("%d/%m/%Y")
            date_range = f"{start_str} - {end_str}"
            if mid not in mid_groups:
                mid_groups[mid] = []
            mid_groups[mid].append(date_range)

        for mid, date_ranges in mid_groups.items():
            if mid != "ALL":
                lines.append(f"MID : {mid}")
            for d in date_ranges:
                lines.append(f"วันที่ {d}")

        if report_name.strip():
            lines.append(f"\nระบุชื่อรายงาน {report_name.strip()}")

        # Build JSON payload
        formatted_requests = [
            {
                "mid": r["mid"],
                "start": r["start"].strftime("%Y-%m-%d"),
                "end": r["end"].strftime("%Y-%m-%d"),
            }
            for r in active_requests
        ]
        payload = {
            "ip": server_ip.strip(),
            "company_id": company_id.strip(),
            "requests": formatted_requests,
        }

        lines.append("\n[SYSTEM_DATA]")
        lines.append(json.dumps(payload, indent=2, ensure_ascii=False))
        lines.append("[/SYSTEM_DATA]")

        st.session_state.generated_ticket = "\n".join(lines)

# Display Generated Ticket
if st.session_state.generated_ticket:
    st.subheader("ผลลัพธ์ทิคเก็ต (Ticket Result)")
    st.caption("คลิกที่ปุ่ม Copy ด้านขวาบนของกล่องข้อความด้านล่าง เพื่อนำไปวางใน Dynamics 365")
    st.code(st.session_state.generated_ticket, language="text")
