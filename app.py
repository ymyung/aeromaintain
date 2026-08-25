import sqlite3

import altair as alt
import streamlit as st

from src.analytics import (
    database_file,
    get_aircraft_summary,
    get_dataset_summary,
    get_jasc_codes_for_aircraft,
    get_models_for_make,
    get_reports_by_month_for_aircraft,
    get_top_aircraft_makes,
    get_top_parts_for_aircraft,
    search_aircraft_reports,
)
from src.database import build_database

st.set_page_config(
    page_title="AeroMaintain",
    page_icon="✈️",
    layout="wide",
)


if not database_file.exists():
    with st.spinner("Preparing the maintenance report database..."):
        build_database()


# stop the page from becoming extremely wide on large monitors
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1400px;
            margin: 0 auto;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("AeroMaintain")

st.write(
    "Explore reported aircraft maintenance issues "
    "from the 2025 FAA Service Difficulty Report dataset."
)


with sqlite3.connect(database_file) as connection:
    # dataset overview
    dataset_summary = get_dataset_summary(
        connection,
    )

    summary = dataset_summary.iloc[0]

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric(
        "Maintenance Reports",
        f"{int(summary['report_count']):,}",
    )

    metric_2.metric(
        "Aircraft Makes",
        f"{int(summary['make_count']):,}",
    )

    metric_3.metric(
        "Aircraft Models",
        f"{int(summary['model_count']):,}",
    )

    # manufacturer overview
    top_makes = get_top_aircraft_makes(
        connection,
        limit=10,
    )

    st.subheader("Top Reported Manufacturers")

    manufacturer_chart = (
        alt.Chart(top_makes)
        .mark_bar()
        .encode(
            x=alt.X(
                "report_count:Q",
                title="Reported Maintenance Issues",
            ),
            y=alt.Y(
                "aircraft_make:N",
                title=None,
                sort="-x",
            ),
            tooltip=[
                alt.Tooltip(
                    "aircraft_make:N",
                    title="Manufacturer",
                ),
                alt.Tooltip(
                    "report_count:Q",
                    title="Reports",
                    format=",",
                ),
            ],
        )
        .properties(
            height=300,
        )
    )

    st.altair_chart(
        manufacturer_chart,
        width="stretch",
    )

    st.caption(
        "Counts represent submitted FAA Service Difficulty Reports, "
        "not manufacturer failure rates."
    )

    st.divider()

    # aircraft explorer
    st.header("Aircraft Explorer")

    st.write(
        "Select an aircraft manufacturer and model to explore "
        "its reported maintenance issues."
    )

    make_column, model_column = st.columns(2)

    with make_column:
        selected_make = st.selectbox(
            "Aircraft manufacturer",
            top_makes["aircraft_make"],
        )

    models = get_models_for_make(
        connection,
        selected_make,
    )

    with model_column:
        selected_model = st.selectbox(
            "Aircraft model",
            models["aircraft_model"],
        )

    st.subheader(
        f"{selected_make} {selected_model}"
    )

    # selected aircraft summary
    aircraft_summary = get_aircraft_summary(
        connection,
        selected_make,
        selected_model,
    )

    aircraft = aircraft_summary.iloc[0]

    aircraft_metric_1, aircraft_metric_2, aircraft_metric_3 = st.columns(3)

    aircraft_metric_1.metric(
        "Reports",
        f"{int(aircraft['report_count']):,}",
    )

    aircraft_metric_2.metric(
        "Unique Parts Reported",
        f"{int(aircraft['unique_parts']):,}",
    )

    aircraft_metric_3.metric(
        "JASC Codes",
        f"{int(aircraft['unique_jasc_codes']):,}",
    )

    # selected aircraft charts
    chart_column_1, chart_column_2 = st.columns(2)

    with chart_column_1:
        st.subheader(
            "Most Commonly Reported Parts"
        )

        top_parts = get_top_parts_for_aircraft(
            connection,
            selected_make,
            selected_model,
            limit=10,
        )

        parts_chart = (
            alt.Chart(top_parts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "report_count:Q",
                    title="Reports",
                ),
                y=alt.Y(
                    "part_name:N",
                    title=None,
                    sort="-x",
                ),
                tooltip=[
                    alt.Tooltip(
                        "part_name:N",
                        title="Part",
                    ),
                    alt.Tooltip(
                        "report_count:Q",
                        title="Reports",
                        format=",",
                    ),
                ],
            )
            .properties(
                height=330,
            )
        )

        st.altair_chart(
            parts_chart,
            width="stretch",
        )

    with chart_column_2:
        st.subheader(
            "Reports by Month"
        )

        monthly_reports = (
            get_reports_by_month_for_aircraft(
                connection,
                selected_make,
                selected_model,
            )
        )

        monthly_chart = (
            alt.Chart(monthly_reports)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "month:N",
                    title="Month",
                ),
                y=alt.Y(
                    "report_count:Q",
                    title="Reports",
                ),
                tooltip=[
                    alt.Tooltip(
                        "month:N",
                        title="Month",
                    ),
                    alt.Tooltip(
                        "report_count:Q",
                        title="Reports",
                        format=",",
                    ),
                ],
            )
            .properties(
                height=330,
            )
        )

        st.altair_chart(
            monthly_chart,
            width="stretch",
        )

    st.divider()

    # aircraft system breakdown
    st.header("Aircraft System Breakdown")

    st.caption(
        "JASC codes identify aircraft systems and components "
        "used in FAA maintenance reporting."
    )

    jasc_codes = get_jasc_codes_for_aircraft(
        connection,
        selected_make,
        selected_model,
    )

    st.dataframe(
        jasc_codes[
            [
                "jasc_code",
                "code_name",
                "category_name",
                "report_count",
            ]
        ],
        column_config={
            "jasc_code": "JASC Code",
            "code_name": "System / Component",
            "category_name": "Category",
            "report_count": st.column_config.NumberColumn(
                "Reports",
                format="%d",
            ),
        },
        hide_index=True,
        width="stretch",
        height=300,
    )

    st.divider()

    # maintenance report browser
    st.header("Maintenance Reports")

    st.write(
        "Search the original maintenance descriptions "
        "or filter reports by JASC system."
    )

    filter_column_1, filter_column_2 = st.columns(2)

    with filter_column_1:
        search_text = st.text_input(
            "Search maintenance descriptions",
            placeholder=(
                "e.g. crack, landing gear, corrosion"
            ),
        )

    # the user sees a readable label,
    # but the database still receives the original code
    jasc_labels = {
        row["jasc_code"]: (
            f"{row['jasc_code']} — "
            f"{row['code_name']}"
        )
        for _, row in jasc_codes.iterrows()
    }

    jasc_options = (
        ["All"]
        + list(jasc_labels.keys())
    )

    with filter_column_2:
        selected_jasc = st.selectbox(
            "JASC system",
            jasc_options,
            format_func=lambda code: (
                "All"
                if code == "All"
                else jasc_labels[code]
            ),
        )

    if selected_jasc == "All":
        selected_jasc = None

    aircraft_reports = search_aircraft_reports(
        connection,
        selected_make,
        selected_model,
        search_text=search_text,
        jasc_code=selected_jasc,
        limit=100,
    )

    st.caption(
        f"Showing {len(aircraft_reports)} matching reports. "
        "A maximum of 100 reports are displayed."
    )

    st.dataframe(
        aircraft_reports,
        column_config={
            "difficulty_date": "Date",
            "jasc_code": "JASC Code",
            "jasc_name": "System / Component",
            "jasc_category": "Category",
            "part_name": "Part",
            "part_condition": "Condition",
            "discrepancy": "Maintenance Report",
        },
        hide_index=True,
        width="stretch",
        height=450,
    )

    st.caption(
        "Report counts represent submitted maintenance reports, "
        "not aircraft failure rates."
    )
