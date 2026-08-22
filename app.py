import sqlite3

import streamlit as st

from src.analytics import (
    database_file,
    get_aircraft_summary,
    get_jasc_codes_for_aircraft,
    get_models_for_make,
    get_reports_by_month_for_aircraft,
    get_top_aircraft_makes,
    get_top_parts,
    get_top_parts_for_aircraft,
    get_total_reports,
    search_aircraft_reports,
)

st.set_page_config(
    page_title="AeroMaintain",
    page_icon="✈️",
    layout="wide",
)


st.title("AeroMaintain")

st.write(
    "Explore reported aircraft maintenance issues from "
    "the 2025 FAA Service Difficulty Report dataset."
)


with sqlite3.connect(database_file) as connection:
    # overall dataset information
    total_reports = get_total_reports(connection)

    top_makes = get_top_aircraft_makes(
        connection,
        limit=10,
    )

    metric_column_1, metric_column_2 = st.columns(2)

    metric_column_1.metric(
        "2025 Maintenance Reports",
        f"{total_reports:,}",
    )

    metric_column_2.metric(
        "Aircraft Makes",
        f"{len(top_makes):,}+",
    )

    # overall manufacturer chart
    st.subheader("Reports by Aircraft Manufacturer")

    st.bar_chart(
        top_makes,
        x="aircraft_make",
        y="report_count",
    )

    st.divider()

    # aircraft explorer
    st.header("Aircraft Explorer")

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

    st.subheader(f"{selected_make} {selected_model}")

    # selected aircraft summary
    aircraft_summary = get_aircraft_summary(
        connection,
        selected_make,
        selected_model,
    )

    summary = aircraft_summary.iloc[0]

    aircraft_metric_1, aircraft_metric_2, aircraft_metric_3 = st.columns(3)

    aircraft_metric_1.metric(
        "Reports",
        f"{int(summary['report_count']):,}",
    )

    aircraft_metric_2.metric(
        "Unique Parts Reported",
        f"{int(summary['unique_parts']):,}",
    )

    aircraft_metric_3.metric(
        "JASC Codes",
        f"{int(summary['unique_jasc_codes']):,}",
    )

    # charts for the selected aircraft
    chart_column_1, chart_column_2 = st.columns(2)

    with chart_column_1:
        st.subheader("Most Commonly Reported Parts")

        top_parts = get_top_parts_for_aircraft(
            connection,
            selected_make,
            selected_model,
            limit=10,
        )

        st.bar_chart(
            top_parts,
            x="part_name",
            y="report_count",
        )

    with chart_column_2:
        st.subheader("Reports by Month")

        monthly_reports = get_reports_by_month_for_aircraft(
            connection,
            selected_make,
            selected_model,
        )

        st.line_chart(
            monthly_reports,
            x="month",
            y="report_count",
        )

    st.divider()

    # maintenance report browser
    st.header("Maintenance Reports")

    jasc_codes = get_jasc_codes_for_aircraft(
        connection,
        selected_make,
        selected_model,
    )

    filter_column_1, filter_column_2 = st.columns(2)

    with filter_column_1:
        search_text = st.text_input(
            "Search maintenance descriptions",
            placeholder="e.g. crack, landing gear, corrosion",
        )

    with filter_column_2:
        jasc_options = ["All"] + jasc_codes["jasc_code"].tolist()

        selected_jasc = st.selectbox(
            "JASC code",
            jasc_options,
        )

    # convert All into no JASC filter
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
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    # overall dataset information
    st.header("Overall Dataset")

    st.subheader("Most Commonly Reported Parts")

    overall_parts = get_top_parts(
        connection,
        limit=10,
    )

    st.dataframe(
        overall_parts,
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "Report counts represent submitted maintenance reports, "
        "not aircraft failure rates."
    )
