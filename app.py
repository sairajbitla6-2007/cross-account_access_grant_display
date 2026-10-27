import json
from datetime import datetime, timezone

import boto3
import pandas as pd
import plotly.express as px
import streamlit as st

from botocore.exceptions import ClientError, NoCredentialsError
from streamlit_autorefresh import st_autorefresh


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Cloud Access Monitor",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        :root {
            color-scheme: light;
        }

        body {
            background: #F5F7FB;
            color: #172033;
        }

        .stApp {
            --primary-color: #1769E0;
            --background-color: #F5F7FB;
            --secondary-background-color: #FFFFFF;
            --text-color: #172033;
            --border-color: #E5EAF2;
            background:
                radial-gradient(circle at top right, #EEF5FF 0, transparent 34%),
                #F5F7FB;
            color: #172033;
        }

        .block-container {
            max-width: 1600px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }

        [data-testid="stSidebar"] {
            --primary-color: #1769E0;
            --background-color: #FFFFFF;
            --secondary-background-color: #F5F7FB;
            --text-color: #172033;
            --border-color: #E5EAF2;
            background-color: #FFFFFF;
            border-right: 1px solid #E5EAF2;
            color: #172033;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stCaption"] {
            color: #52627A;
        }

        [data-testid="stHeader"] {
            background: rgba(245, 247, 251, 0.96);
            color: #172033;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1.5rem 1rem 1rem;
        }

        .brand {
            font-size: 21px;
            font-weight: 800;
            color: #1769E0;
            margin-bottom: 3px;
        }

        .brand-subtitle {
            color: #7B879A;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.08em;
            margin-bottom: 24px;
        }

        .top-label {
            color: #1769E0;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.3px;
            text-transform: uppercase;
        }

        .main-title {
            font-size: clamp(27px, 3vw, 34px);
            font-weight: 800;
            color: #172033;
            letter-spacing: -0.035em;
            margin-top: 5px;
            margin-bottom: 4px;
        }

        .subtitle {
            color: #758198;
            font-size: 14px;
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: #172033;
            margin-top: 4px;
            margin-bottom: 5px;
        }

        .section-subtitle {
            color: #7B879A;
            font-size: 12px;
            margin-bottom: 14px;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E7ECF4;
            border-radius: 15px;
            padding: 17px 18px;
            box-shadow: 0 5px 18px rgba(24, 49, 87, 0.045);
            min-height: 112px;
        }

        [data-testid="stMetricLabel"] {
            color: #77849A;
            font-size: 13px;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: #172033;
            font-size: 29px;
            font-weight: 800;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.92);
            border-color: #E4EAF3;
            border-radius: 15px;
            box-shadow: 0 5px 18px rgba(24, 49, 87, 0.035);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] h3,
        div[data-testid="stVerticalBlockBorderWrapper"] h4 {
            color: #243653;
            letter-spacing: -0.015em;
        }

        div[data-testid="stButton"] button {
            border-radius: 10px;
            font-weight: 600;
            min-height: 42px;
            transition: all 160ms ease;
        }

        div[data-testid="stButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            border-color: #1769E0;
            color: #1769E0;
            transform: translateY(-1px);
        }

        div[data-testid="stDownloadButton"] button {
            border-radius: 10px;
            font-weight: 600;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] > div > div {
            border-radius: 9px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #E5EAF2;
            border-radius: 10px;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            border-radius: 9px;
            padding: 4px 8px;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: #F2F6FC;
        }

        .footer-note {
            color: #8590A3;
            font-size: 11px;
            border-top: 1px solid #E5EAF2;
            margin-top: 24px;
            padding-top: 16px;
            padding-bottom: 12px;
            letter-spacing: 0.035em;
        }

        hr {
            border-color: #E5EAF2;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 1.25rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .main-title {
                font-size: 27px;
            }

            div[data-testid="stMetric"] {
                min-height: 96px;
                padding: 13px;
            }
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# AWS CONFIGURATION
# =========================================================

BUCKET_NAME = "access-grant-demo-150202114394-2026"
S3_PREFIX = "access-results/"
AWS_REGION = "us-east-1"


# =========================================================
# AUTOMATIC REFRESH
# =========================================================

st_autorefresh(
    interval=30_000,
    limit=None,
    key="aws_dashboard_autorefresh"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">☁ Cloud Monitor</div>
        <div class="brand-subtitle">AWS ACCESS INTELLIGENCE</div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Access Requests",
            "AWS Identity",
            "S3 Storage",
            "System Information"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.markdown("#### Environment")

    st.caption("AWS Region")
    st.code(AWS_REGION, language=None)

    st.caption("Data source")
    st.write(":material/cloud: Amazon S3")

    st.caption("Refresh interval")
    st.write(":material/autorenew: Every 30 seconds")

    st.divider()

    st.caption("Cloud Access Monitor")
    st.caption("Access monitoring prototype")


# =========================================================
# AWS CONNECTION
# =========================================================

@st.cache_resource
def get_s3_client():
    try:
        return boto3.client(
               "s3",
               region_name=AWS_REGION,
               aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
               aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
               aws_session_token=st.secrets["AWS_SESSION_TOKEN"],
        )
    except (KeyError, FileNotFoundError):
        return boto3.client("s3", region_name=AWS_REGION)



# =========================================================
# LOAD JSON RESULTS FROM S3
# =========================================================

@st.cache_data(ttl=30)
def load_results():
    s3 = get_s3_client()
    results = []

    paginator = s3.get_paginator("list_objects_v2")

    for page_data in paginator.paginate(
        Bucket=BUCKET_NAME,
        Prefix=S3_PREFIX
    ):
        for obj in page_data.get("Contents", []):
            key = obj["Key"]

            if not key.lower().endswith(".json"):
                continue

            response = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=key
            )

            content = response["Body"].read().decode("utf-8")
            record = json.loads(content)

            record["_s3_key"] = key
            record["_last_modified"] = (
                obj["LastModified"].isoformat()
            )

            results.append(record)

    results.sort(
        key=lambda item: item.get("_last_modified", ""),
        reverse=True
    )

    return results


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        '<div class="top-label">CLOUD OPERATIONS / MONITORING</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-title">Cloud Access Monitor</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Monitor AWS identity checks, S3 access, and request activity.'
        '</div>',
        unsafe_allow_html=True
    )

with header_right:
    if st.button(
        "Refresh now",
        icon=":material/refresh:",
        type="primary",
        width="stretch"
    ):
        load_results.clear()
        st.rerun()


# =========================================================
# FETCH DATA
# =========================================================

try:
    records = load_results()

    if not records:
        st.info(
            "No request records were found yet. Submit an MQTT request "
            "through AWS IoT Core and check that Lambda saves the result "
            "to the configured S3 prefix."
        )

        st.markdown(
            f"**Bucket:** `{BUCKET_NAME}`  \n"
            f"**Prefix:** `{S3_PREFIX}`"
        )

        st.stop()

    # =====================================================
    # BUILD DATAFRAME
    # =====================================================

    rows = []

    for record in records:
        rows.append(
            {
                "Request ID": record.get("requestId", "Unknown"),
                "Timestamp": record.get("timestamp", ""),
                "Overall Status": record.get("status", "Unknown"),
                "S3 Access": record.get("s3Access", "Unknown"),
                "Storage Status": record.get(
                    "storageStatus", "Unknown"
                ),
                "AWS Account": record.get("account", "Unknown"),
                "Identity": record.get("identity", "Unknown"),
                "Message": record.get("message", ""),
                "Processing Message": record.get(
                    "processingMessage", ""
                ),
                "S3 Object": record.get("_s3_key", ""),
                "_record": record
            }
        )

    df = pd.DataFrame(rows)

    # Normalize statuses for reliable metrics.
    df["Overall Status"] = (
        df["Overall Status"].fillna("Unknown").astype(str)
    )

    df["S3 Access"] = (
        df["S3 Access"].fillna("Unknown").astype(str)
    )

    df["Storage Status"] = (
        df["Storage Status"].fillna("Unknown").astype(str)
    )

    # =====================================================
    # KPI METRICS
    # =====================================================

    total_requests = len(df)

    successful_requests = (
        df["Overall Status"].str.upper() == "SUCCESS"
    ).sum()

    failed_requests = total_requests - successful_requests

    successful_s3_checks = (
        df["S3 Access"].str.upper() == "SUCCESS"
    ).sum()

    successful_storage = (
        df["Storage Status"].str.upper() == "SUCCESS"
    ).sum()

    st.markdown('<div class="section-title">Overview</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="section-subtitle">'
        'A summary of the request records currently available in S3.'
        '</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total requests", f"{total_requests:,}", border=True)
    k2.metric("Successful requests", f"{successful_requests:,}", border=True)
    k3.metric("Failed requests", f"{failed_requests:,}", border=True)
    k4.metric("Successful S3 checks", f"{successful_s3_checks:,}", border=True)

    st.space("small")

    # =====================================================
    # FILTERS
    # =====================================================

    st.markdown('<div class="section-title">Filter request activity</div>',
                unsafe_allow_html=True)

    with st.container(border=True):
        filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

        with filter_col1:
            search_text = st.text_input(
                "Search requests",
                placeholder="Search request ID, account, or message..."
            )

        with filter_col2:
            status_options = ["All"] + sorted(
                df["Overall Status"].unique().tolist()
            )

            selected_status = st.selectbox(
                "Overall status",
                status_options
            )

        with filter_col3:
            s3_options = ["All"] + sorted(
                df["S3 Access"].unique().tolist()
            )

            selected_s3 = st.selectbox(
                "S3 access",
                s3_options
            )

    filtered_df = df.copy()

    if search_text.strip():
        search_columns = [
            "Request ID",
            "AWS Account",
            "Message",
            "Processing Message"
        ]

        mask = pd.Series(False, index=filtered_df.index)

        for column in search_columns:
            mask |= (
                filtered_df[column]
                .fillna("")
                .astype(str)
                .str.contains(
                    search_text,
                    case=False,
                    regex=False
                )
            )

        filtered_df = filtered_df[mask]

    if selected_status != "All":
        filtered_df = filtered_df[
            filtered_df["Overall Status"] == selected_status
        ]

    if selected_s3 != "All":
        filtered_df = filtered_df[
            filtered_df["S3 Access"] == selected_s3
        ]

    # =====================================================
    # CHARTS
    # =====================================================

    chart_left, chart_right = st.columns([3, 2])

    with chart_left:
        with st.container(border=True):
            st.markdown("#### Request status distribution")

            status_counts = (
                filtered_df["Overall Status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Requests")
            )

            if not status_counts.empty:
                fig_status = px.bar(
                    status_counts,
                    x="Status",
                    y="Requests",
                    color="Status",
                    text="Requests",
                    color_discrete_map={
                        "SUCCESS": "#16A36A",
                        "ERROR": "#E24B4B",
                        "FAILED": "#E24B4B",
                        "WARNING": "#E6A23C"
                    }
                )

                fig_status.update_layout(
                    height=285,
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    margin=dict(l=10, r=10, t=15, b=10),
                    showlegend=False,
                    font=dict(
                        family="Inter, sans-serif",
                        color="#344054"
                    ),
                    xaxis_title="",
                    yaxis_title="Number of requests"
                )

                fig_status.update_yaxes(
                    gridcolor="#EEF1F6",
                    zeroline=False
                )

                st.plotly_chart(
                    fig_status,
                    width="stretch"
                )
            else:
                st.info("No matching requests for this chart.")

    with chart_right:
        with st.container(border=True):
            st.markdown("#### S3 access results")

            s3_counts = (
                filtered_df["S3 Access"]
                .value_counts()
                .rename_axis("S3 Access")
                .reset_index(name="Requests")
            )

            if not s3_counts.empty:
                fig_s3 = px.pie(
                    s3_counts,
                    names="S3 Access",
                    values="Requests",
                    hole=0.65,
                    color="S3 Access",
                    color_discrete_map={
                        "SUCCESS": "#16A36A",
                        "ERROR": "#E24B4B",
                        "NOT_TESTED": "#98A2B3",
                        "Unknown": "#D0D5DD"
                    }
                )

                fig_s3.update_traces(
                    domain=dict(x=[0, 0.68]),
                    textinfo="percent",
                    textfont=dict(color="white", size=12)
                )
                fig_s3.add_annotation(
                    text=f"<b>{len(filtered_df)}</b><br>checks",
                    x=0.34,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        family="Inter, sans-serif",
                        size=13,
                        color="#344054"
                    )
                )

                fig_s3.update_layout(
                    height=285,
                    paper_bgcolor="white",
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=0.73
                    ),
                    font=dict(
                        family="Inter, sans-serif",
                        color="#344054"
                    )
                )

                st.plotly_chart(
                    fig_s3,
                    width="stretch"
                )
            else:
                st.info("No matching requests for this chart.")

    # =====================================================
    # REQUEST TABLE
    # =====================================================

    display_columns = [
        "Request ID",
        "Timestamp",
        "Overall Status",
        "S3 Access",
        "Storage Status",
        "AWS Account",
        "Message"
    ]

    with st.container(border=True):
        st.markdown("#### Access request history")
        st.caption("Search and filters above apply to the records shown here.")

        st.dataframe(
            filtered_df[display_columns],
            width="stretch",
            hide_index=True,
            height=min(370, max(120, 35 * (len(filtered_df) + 1))),
            column_config={
                "Request ID": st.column_config.TextColumn(
                    "Request ID",
                    width="medium"
                ),
                "Timestamp": st.column_config.TextColumn(
                    "Timestamp",
                    width="medium"
                ),
                "Overall Status": st.column_config.TextColumn(
                    "Status",
                    width="small"
                ),
                "S3 Access": st.column_config.TextColumn(
                    "S3 Access",
                    width="small"
                ),
                "Storage Status": st.column_config.TextColumn(
                    "Storage",
                    width="small"
                ),
                "Message": st.column_config.TextColumn(
                    "Incoming Message",
                    width="large"
                )
            }
        )

        st.caption(
            f"Showing {len(filtered_df)} of {total_requests} request records."
        )

    # =====================================================
    # REQUEST INSPECTOR AND QUICK INSIGHTS
    # =====================================================

    st.space("medium")
    inspector_col, insights_col = st.columns([1.2, 1])

    with inspector_col:
        with st.container(border=True):
            st.markdown("#### :material/search: Request inspector")
            st.caption(
                "Select a request to inspect its complete stored JSON record."
            )

            if not filtered_df.empty:
                selected_ids = filtered_df.index.tolist()

                selected_index = st.selectbox(
                    "Choose a request",
                    selected_ids,
                    format_func=lambda idx: (
                        f"{df.loc[idx, 'Request ID']} — "
                        f"{df.loc[idx, 'Overall Status']} — "
                        f"{df.loc[idx, 'Timestamp']}"
                    )
                )

                selected_record = df.loc[selected_index, "_record"]

                detail1, detail2, detail3 = st.columns(3)

                detail1.metric(
                    "Request status",
                    str(selected_record.get("status", "Unknown")),
                    border=True
                )

                detail2.metric(
                    "S3 access",
                    str(selected_record.get("s3Access", "Unknown")),
                    border=True
                )

                detail3.metric(
                    "Storage status",
                    str(selected_record.get("storageStatus", "Unknown")),
                    border=True
                )

                st.markdown("**Incoming message**")

                st.code(
                    str(selected_record.get("message", "") or "(No message)"),
                    language=None
                )

                with st.expander(
                    "View complete JSON record",
                    icon=":material/data_object:"
                ):
                    st.json(selected_record)

                with st.expander(
                    "View stored S3 object information",
                    icon=":material/cloud:"
                ):
                    st.write(
                        "**S3 object key:**",
                        selected_record.get("_s3_key", "Unknown")
                    )

                    st.write(
                        "**Last modified:**",
                        selected_record.get("_last_modified", "Unknown")
                    )

            else:
                st.info("No requests match the selected filters.")

    with insights_col:
        with st.container(border=True):
            st.markdown("#### :material/lightbulb: Quick insights")

            matching_successes = int(
                (filtered_df["Overall Status"].str.upper() == "SUCCESS").sum()
            )
            matching_s3_successes = int(
                (filtered_df["S3 Access"].str.upper() == "SUCCESS").sum()
            )
            matching_storage_successes = int(
                (filtered_df["Storage Status"].str.upper() == "SUCCESS").sum()
            )
            matching_storage_not_tested = int(
                (filtered_df["Storage Status"].str.upper() == "NOT_TESTED").sum()
            )

            st.markdown("**Request outcomes**")
            st.caption(
                f"{matching_successes:,} of {len(filtered_df):,} matching "
                "requests are successful."
            )

            st.markdown("**S3 access**")
            st.caption(
                f"{matching_s3_successes:,} of {len(filtered_df):,} matching "
                "requests have successful S3 checks."
            )

            st.markdown("**Storage status**")
            st.caption(
                f"{matching_storage_successes:,} successful · "
                f"{matching_storage_not_tested:,} not tested."
            )

            recent_request = df.iloc[0]
            st.markdown("**Most recent record**")
            st.caption(
                f"{recent_request['Request ID']} · "
                f"{recent_request['Timestamp'] or 'Timestamp unavailable'}"
            )

            st.info(
                "This prototype reports the AWS identity and S3 results "
                "stored by the application; it does not independently "
                "verify cross-account role assumption."
            )

            st.markdown("#### Export data")
            export_df = filtered_df[display_columns].copy()
            csv_data = export_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label=":material/download: Download filtered CSV",
                data=csv_data,
                file_name="cloud_access_monitor_report.csv",
                mime="text/csv",
                width="stretch"
            )

            st.caption(
                "The export contains the records currently visible after "
                "applying your filters."
            )

    # =====================================================
    # PAGE-SPECIFIC CONTENT
    # =====================================================

    if page == "AWS Identity":
        st.divider()
        st.markdown("### AWS Identity")

        identity_df = filtered_df[
            ["Request ID", "Timestamp", "AWS Account", "Identity"]
        ]

        st.dataframe(
            identity_df,
            width="stretch",
            hide_index=True
        )

        st.info(
            "These values report the AWS identity observed by Lambda. "
            "They do not independently prove that cross-account role "
            "assumption into Account B is configured."
        )

    elif page == "S3 Storage":
        st.divider()
        st.markdown("### S3 Storage")

        storage_df = filtered_df[
            [
                "Request ID",
                "S3 Access",
                "Storage Status",
                "S3 Object"
            ]
        ]

        st.dataframe(
            storage_df,
            width="stretch",
            hide_index=True
        )

        st.write(f"**Bucket:** `{BUCKET_NAME}`")
        st.write(f"**Prefix:** `{S3_PREFIX}`")

    elif page == "Access Requests":
        st.caption(
            "Use the search and filters above to narrow the request history."
        )

    elif page == "System Information":
        st.divider()
        st.markdown("### System Information")

        st.write(f"**AWS Region:** `{AWS_REGION}`")
        st.write(f"**S3 Bucket:** `{BUCKET_NAME}`")
        st.write(f"**S3 Prefix:** `{S3_PREFIX}`")
        st.write("**Data refresh interval:** 30 seconds")
        st.write(f"**Records loaded:** {total_requests:,}")
        st.write(
            "**Dashboard execution time (UTC):** "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        st.info(
            "This dashboard reads JSON request records from S3 using "
            "the AWS credentials available to the Python process. "
            "It is an access-monitoring prototype; genuine cross-account "
            "role assumption must be configured and verified separately."
        )

    # =====================================================
    # FOOTER
    # =====================================================

    st.markdown(
        """
        <div class="footer-note">
            CLOUD ACCESS MONITOR &nbsp;•&nbsp;
            AWS IDENTITY AND S3 ACCESS MONITORING
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# ERROR HANDLING
# =========================================================

except NoCredentialsError:
    st.error(
        "AWS credentials were not found. Obtain fresh temporary "
        "credentials from AWS Academy Learner Lab and configure them "
        "in the PowerShell terminal running Streamlit."
    )

except ClientError as error:
    error_code = error.response.get(
        "Error", {}
    ).get("Code", "Unknown")

    st.error(f"AWS request failed: {error_code}")

    if error_code in ("AccessDenied", "AccessDeniedException"):
        st.warning(
            "The current AWS identity may not have permission to list "
            "or read the S3 objects. Check the existing LabRole "
            "permissions and Learner Lab restrictions."
        )

except json.JSONDecodeError:
    st.error(
        "An S3 object contains invalid JSON. Check the corresponding "
        "request result before retrying."
    )

except Exception as error:
    st.error(f"Unexpected error: {error}")
