import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Insight",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main page spacing */
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Main title */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
        margin-bottom: 0rem !important;
    }

    /* Section headings */
    h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.3px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 1.2rem;
        border-radius: 10px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.15);
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 8px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("◈ Insight")

    st.caption("data analysis in seconds")

    st.divider()

    st.subheader("Dataset")

    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        help="Upload a CSV dataset to begin your analysis."
    )

    st.divider()

    st.caption(
        "Insight automatically profiles your dataset "
        "and helps identify data quality issues."
    )


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.title("Dataset Analysis")

st.write(
    "Explore your dataset's structure, completeness, "
    "quality, trends, and key statistical characteristics."
)

st.divider()


# --------------------------------------------------
# DATA ANALYSIS
# --------------------------------------------------

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        # ------------------------------------------
        # DATASET OVERVIEW
        # ------------------------------------------

        st.subheader("Overview")

        missing_counts = df.isnull().sum()

        total_missing = int(missing_counts.sum())

        columns_affected = int(
            (missing_counts > 0).sum()
        )

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            st.metric(
                "Rows",
                f"{df.shape[0]:,}"
            )

        with metric2:
            st.metric(
                "Columns",
                f"{df.shape[1]:,}"
            )

        with metric3:
            st.metric(
                "Missing Cells",
                f"{total_missing:,}"
            )

        with metric4:
            st.metric(
                "Columns Affected",
                f"{columns_affected:,}"
            )

        st.divider()


        # ------------------------------------------
        # DATASET PREVIEW
        # ------------------------------------------

        st.subheader("Dataset Preview")

        st.caption(
            "A preview of the first five rows in your dataset."
        )

        st.dataframe(
            df.head(),
            width="stretch"
        )

        st.divider()


        # ------------------------------------------
        # COLUMN INFORMATION
        # ------------------------------------------

        st.subheader("Column Information")

        st.caption(
            "Detected columns and their inferred Pandas data types."
        )

        column_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values
        })

        st.dataframe(
            column_info,
            width="stretch",
            hide_index=True
        )

        st.divider()


        # ------------------------------------------
        # MISSING VALUES
        # ------------------------------------------

        st.subheader("Missing Values")

        st.caption(
            "Columns containing incomplete data and "
            "the percentage of values that are missing."
        )

        if total_missing > 0:

            missing_data = pd.DataFrame({
                "Column":
                    missing_counts[missing_counts > 0].index,

                "Missing Values":
                    missing_counts[missing_counts > 0].values,

                "Missing Percentage":
                    (
                        missing_counts[missing_counts > 0].values
                        / len(df)
                        * 100
                    ).round(2)
            })

            st.dataframe(
                missing_data,
                width="stretch",
                hide_index=True
            )

        else:
            st.success(
                "No missing values detected in this dataset."
            )

        st.divider()


        # ------------------------------------------
        # DATA QUALITY ENGINE
        # ------------------------------------------

        st.subheader("Data Quality")

        st.caption(
            "Automated checks for potential data quality issues."
        )


        # ------------------------------------------
        # DUPLICATE ROWS
        # ------------------------------------------

        duplicate_rows = int(
            df.duplicated().sum()
        )

        if len(df) > 0:
            duplicate_percentage = (
                duplicate_rows / len(df) * 100
            )
        else:
            duplicate_percentage = 0


        # ------------------------------------------
        # CONSTANT COLUMNS
        # ------------------------------------------

        constant_columns = [
            column
            for column in df.columns
            if df[column].nunique(dropna=False) <= 1
        ]


        # ------------------------------------------
        # POSSIBLE ID COLUMNS
        # ------------------------------------------

        possible_id_columns = []

        for column in df.columns:

            non_null_values = df[column].dropna()

            if len(non_null_values) == 0:
                continue

            unique_count = non_null_values.nunique()

            if (
                unique_count == len(non_null_values)
                and len(non_null_values) > 1
            ):
                possible_id_columns.append(column)


        # ------------------------------------------
        # SUSPICIOUS / UNNAMED COLUMNS
        # ------------------------------------------

        suspicious_columns = [
            column
            for column in df.columns
            if str(column).lower().startswith("unnamed")
        ]


        # ------------------------------------------
        # POTENTIAL TYPE ISSUES
        # ------------------------------------------

        potential_type_issues = []

        for column in df.select_dtypes(
            include=["object", "string"]
        ).columns:

            non_null_values = df[column].dropna()

            if len(non_null_values) == 0:
                continue

            converted_values = pd.to_numeric(
                non_null_values,
                errors="coerce"
            )

            numeric_percentage = (
                converted_values.notna().mean()
            )

            if numeric_percentage >= 0.8:
                potential_type_issues.append(column)


        # ------------------------------------------
        # OUTLIER DETECTION — IQR METHOD
        # ------------------------------------------

        outlier_results = []

        numerical_column_names = df.select_dtypes(
            include="number"
        ).columns

        for column in numerical_column_names:

            non_null_values = df[column].dropna()

            if len(non_null_values) < 4:
                continue

            q1 = non_null_values.quantile(0.25)
            q3 = non_null_values.quantile(0.75)

            iqr = q3 - q1

            if iqr == 0:
                continue

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_mask = (
                (non_null_values < lower_bound)
                | (non_null_values > upper_bound)
            )

            outlier_count = int(
                outlier_mask.sum()
            )

            if outlier_count > 0:

                outlier_percentage = (
                    outlier_count
                    / len(non_null_values)
                    * 100
                )

                outlier_results.append({
                    "Column": column,
                    "Outliers": outlier_count,
                    "Outlier Percentage":
                        round(outlier_percentage, 2),
                    "Lower Bound":
                        round(lower_bound, 2),
                    "Upper Bound":
                        round(upper_bound, 2)
                })


        # ------------------------------------------
        # CATEGORICAL INCONSISTENCY DETECTION
        # ------------------------------------------

        categorical_inconsistency_results = []

        categorical_columns = df.select_dtypes(
            include=["object", "string"]
        ).columns

        for column in categorical_columns:

            non_null_values = df[column].dropna()

            if len(non_null_values) == 0:
                continue

            original_values = non_null_values.astype(str)

            normalized_values = (
                original_values
                .str.strip()
                .str.lower()
            )

            comparison_data = pd.DataFrame({
                "Original": original_values.values,
                "Normalized": normalized_values.values
            })

            for normalized_value, group in comparison_data.groupby(
                "Normalized"
            ):

                unique_original_values = (
                    group["Original"]
                    .drop_duplicates()
                    .tolist()
                )

                if len(unique_original_values) > 1:

                    categorical_inconsistency_results.append({
                        "Column": column,
                        "Normalized Value": normalized_value,
                        "Detected Variations": ", ".join(
                            unique_original_values[:5]
                        ),
                        "Variation Count": len(
                            unique_original_values
                        )
                    })


        # ------------------------------------------
        # DATA QUALITY SUMMARY METRICS
        # ------------------------------------------
        # ------------------------------------------
        # DATA HEALTH SCORE
        # ------------------------------------------

        health_score = 100

        health_score_deductions = []

        # Missing values deduction
        total_cells = df.shape[0] * df.shape[1]

        if total_cells > 0:
            missing_percentage_overall = (
                total_missing / total_cells * 100
            )
        else:
            missing_percentage_overall = 0

        missing_deduction = min(
            25,
            round(missing_percentage_overall)
        )

        if missing_deduction > 0:
            health_score -= missing_deduction

            health_score_deductions.append({
                "Issue": "Missing Values",
                "Points Deducted": missing_deduction
            })


        # Duplicate rows deduction
        duplicate_deduction = min(
            15,
            round(duplicate_percentage)
        )

        if duplicate_deduction > 0:
            health_score -= duplicate_deduction

            health_score_deductions.append({
                "Issue": "Duplicate Rows",
                "Points Deducted": duplicate_deduction
            })


        # Constant columns deduction
        constant_deduction = min(
            10,
            len(constant_columns) * 2
        )

        if constant_deduction > 0:
            health_score -= constant_deduction

            health_score_deductions.append({
                "Issue": "Constant Columns",
                "Points Deducted": constant_deduction
            })


        # Suspicious columns deduction
        suspicious_deduction = min(
            10,
            len(suspicious_columns) * 2
        )

        if suspicious_deduction > 0:
            health_score -= suspicious_deduction

            health_score_deductions.append({
                "Issue": "Suspicious Columns",
                "Points Deducted": suspicious_deduction
            })


        # Potential data type issues deduction
        type_deduction = min(
            10,
            len(potential_type_issues) * 2
        )

        if type_deduction > 0:
            health_score -= type_deduction

            health_score_deductions.append({
                "Issue": "Potential Type Issues",
                "Points Deducted": type_deduction
            })


        # Outlier deduction
        outlier_deduction = min(
            15,
            len(outlier_results)
        )

        if outlier_deduction > 0:
            health_score -= outlier_deduction

            health_score_deductions.append({
                "Issue": "Columns with Potential Outliers",
                "Points Deducted": outlier_deduction
            })


        # Categorical inconsistency deduction
        inconsistent_column_count = len(
            set(
                result["Column"]
                for result
                in categorical_inconsistency_results
            )
        )

        categorical_deduction = min(
            15,
            inconsistent_column_count * 2
        )

        if categorical_deduction > 0:
            health_score -= categorical_deduction

            health_score_deductions.append({
                "Issue": "Categorical Inconsistencies",
                "Points Deducted": categorical_deduction
            })


        # Ensure score stays between 0 and 100
        health_score = max(
            0,
            min(100, health_score)
        )
                # ------------------------------------------
        # AI ANALYST — STRUCTURED ANALYSIS REPORT
        # ------------------------------------------

        analysis_report = {
            "dataset_overview": {
                "rows": len(df),
                "columns": len(df.columns),
                "missing_cells": total_missing,
                "columns_with_missing_values": columns_affected
            },
            "data_quality": {
                "health_score": health_score,
                "duplicate_rows": duplicate_rows,
                "constant_columns": constant_columns,
                "possible_id_columns": possible_id_columns,
                "suspicious_columns": suspicious_columns,
                "potential_type_issues": potential_type_issues,
                "outliers": outlier_results,
                        "categorical_inconsistency_count":
            len(categorical_inconsistency_results),
        "categorical_inconsistency_columns":
            list(
                set(
                    result["Column"]
                    for result
                    in categorical_inconsistency_results
                )
            )
            }
        }
        
                # ------------------------------------------
        # DATA HEALTH SCORE DISPLAY
        # ------------------------------------------

        st.markdown("### Data Health Score")

        st.caption(
            "A transparent quality score based on missing values, "
            "duplicates, constant and suspicious columns, potential "
            "type issues, outliers, and categorical inconsistencies."
        )

        health_col1, health_col2 = st.columns(
            [1, 3]
        )

        with health_col1:

            st.metric(
                "Health Score",
                f"{health_score}/100"
            )

        with health_col2:

            if health_score >= 90:

                st.success(
                    "Excellent — this dataset has very few "
                    "detected quality concerns."
                )

            elif health_score >= 75:

                st.success(
                    "Good — this dataset is generally healthy "
                    "with some issues worth reviewing."
                )

            elif health_score >= 50:

                st.warning(
                    "Fair — several data quality issues were "
                    "detected and should be reviewed."
                )

            else:

                st.error(
                    "Poor — significant data quality issues were "
                    "detected in this dataset."
                )


        # Display score deductions
        if health_score_deductions:

            with st.expander(
                "View Health Score Breakdown"
            ):

                health_score_breakdown = pd.DataFrame(
                    health_score_deductions
                )

                st.dataframe(
                    health_score_breakdown,
                    width="stretch",
                    hide_index=True
                )

                st.caption(
                    "The Data Health Score is a heuristic indicator. "
                    "Potential outliers and other flagged issues may "
                    "be valid observations and should be reviewed "
                    "in context."
                )

        else:

            st.success(
                "No score deductions were applied."
            )

        st.divider()
                # ------------------------------------------
        # ANALYSIS SUMMARY
        # ------------------------------------------

        st.markdown("### Analysis Summary")

        st.caption(
            "A quick overview of the dataset's overall quality "
            "and the issues detected by Insight."
        )

        total_quality_issues = (
            duplicate_rows
            + len(constant_columns)
            + len(suspicious_columns)
            + len(potential_type_issues)
            + len(outlier_results)
            + inconsistent_column_count
        )

        summary1, summary2, summary3, summary4 = st.columns(4)

        with summary1:
            st.metric(
                "Rows Analysed",
                f"{len(df):,}"
            )

        with summary2:
            st.metric(
                "Columns Analysed",
                f"{len(df.columns):,}"
            )

        with summary3:
            st.metric(
                "Missing Cells",
                f"{total_missing:,}"
            )

        with summary4:
            st.metric(
                "Quality Issues",
                f"{total_quality_issues:,}"
            )

        st.divider()
        quality1, quality2, quality3 = st.columns(3)

        with quality1:
            st.metric(
                "Duplicate Rows",
                f"{duplicate_rows:,}"
            )

        with quality2:
            st.metric(
                "Constant Columns",
                f"{len(constant_columns):,}"
            )

        with quality3:
            st.metric(
                "Possible ID Columns",
                f"{len(possible_id_columns):,}"
            )

        quality4, quality5, quality6 = st.columns(3)

        with quality4:
            st.metric(
                "Potential Type Issues",
                f"{len(potential_type_issues):,}"
            )

        with quality5:
            st.metric(
                "Columns with Outliers",
                f"{len(outlier_results):,}"
            )

        with quality6:
            inconsistent_column_count = len(
                set(
                    result["Column"]
                    for result
                    in categorical_inconsistency_results
                )
            )

            st.metric(
                "Categorical Issues",
                f"{inconsistent_column_count:,}"
            )


        # ------------------------------------------
        # DUPLICATE DETAILS
        # ------------------------------------------

        st.markdown("#### Duplicate Rows")

        if duplicate_rows > 0:

            st.error(
                f"Insight detected {duplicate_rows:,} duplicate rows "
                f"({duplicate_percentage:.2f}% of the dataset)."
            )

        else:

            st.success(
                "No duplicate rows detected."
            )


        # ------------------------------------------
        # CONSTANT COLUMN DETAILS
        # ------------------------------------------

        st.markdown("#### Constant Columns")

        if constant_columns:

            constant_data = pd.DataFrame({
                "Column": constant_columns
            })

            st.error(
                "These columns contain only one unique value "
                "and may provide little analytical value."
            )

            st.dataframe(
                constant_data,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No constant columns detected."
            )


        # ------------------------------------------
        # POSSIBLE ID COLUMN DETAILS
        # ------------------------------------------

        st.markdown("#### Possible ID Columns")

        if possible_id_columns:

            id_data = pd.DataFrame({
                "Column": possible_id_columns
            })

            st.info(
                "These columns contain unique values for every "
                "non-missing row and may represent identifiers."
            )

            st.dataframe(
                id_data,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No possible ID columns detected."
            )


        # ------------------------------------------
        # SUSPICIOUS COLUMN DETAILS
        # ------------------------------------------

        st.markdown("#### Suspicious Columns")

        if suspicious_columns:

            suspicious_data = pd.DataFrame({
                "Column": suspicious_columns,
                "Reason": [
                    "Column name suggests an exported index."
                    for _ in suspicious_columns
                ]
            })

            st.error(
                "Insight detected columns that may have been "
                "accidentally created during CSV export."
            )

            st.dataframe(
                suspicious_data,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No suspicious unnamed columns detected."
            )


        # ------------------------------------------
        # POTENTIAL TYPE ISSUE DETAILS
        # ------------------------------------------

        st.markdown("#### Potential Data Type Issues")

        if potential_type_issues:

            type_issue_data = pd.DataFrame({
                "Column": potential_type_issues,
                "Current Type": [
                    str(df[column].dtype)
                    for column in potential_type_issues
                ],
                "Issue": [
                    "Most values appear numeric but the column "
                    "is stored as text."
                    for _ in potential_type_issues
                ]
            })

            st.error(
                "These columns may be stored using an "
                "inappropriate data type."
            )

            st.dataframe(
                type_issue_data,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No obvious data type issues detected."
            )


        # ------------------------------------------
        # POTENTIAL OUTLIER DETAILS
        # ------------------------------------------

        st.markdown("#### Potential Outliers")

        if outlier_results:

            outlier_data = pd.DataFrame(
                outlier_results
            )

            st.error(
                "Insight detected numerical values outside the "
                "expected range using the IQR method. "
                "These values are flagged for review and are "
                "not automatically considered errors."
            )

            st.dataframe(
                outlier_data,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No potential numerical outliers detected "
                "using the IQR method."
            )


        # ------------------------------------------
        # CATEGORICAL INCONSISTENCY DETAILS
        # ------------------------------------------

        st.markdown("#### Categorical Inconsistencies")

        if categorical_inconsistency_results:

            categorical_issue_data = pd.DataFrame(
                categorical_inconsistency_results
            )

            st.error(
                "Insight detected categorical values that may "
                "represent the same category but use different "
                "capitalization or spacing."
            )

            st.dataframe(
                categorical_issue_data,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No obvious categorical inconsistencies detected."
            )

        st.divider()


        # ------------------------------------------
        # NUMERICAL STATISTICS
        # ------------------------------------------

        st.subheader("Numerical Statistics")

        st.caption(
            "Descriptive statistics for numerical columns."
        )

        numerical_columns = df.select_dtypes(
            include="number"
        )

        if not numerical_columns.empty:

            st.dataframe(
                numerical_columns.describe().T,
                width="stretch"
            )

        else:

            st.info(
                "No numerical columns were detected "
                "in this dataset."
            )

        st.divider()


        # ==================================================
        # STEP 7 — TRENDS AND STATISTICAL INSIGHTS
        # ==================================================


        st.subheader("Trends & Statistical Insights")

        st.caption(
            "Explore numerical distributions, relationships, "
            "categorical patterns, and time-based trends."
        )


        # ------------------------------------------
        # NUMERICAL DISTRIBUTIONS
        # ------------------------------------------

        st.markdown("#### Numerical Distributions")

        if not numerical_columns.empty:

            distribution_control1, distribution_control2 = st.columns(2)

            with distribution_control1:
                distribution_column = st.selectbox(
                    "Select a numerical column",
                    numerical_columns.columns,
                    key="distribution_column"
                )

            with distribution_control2:
                distribution_chart_type = st.selectbox(
                    "Select a chart type",
                    [
                        "Histogram",
                        "Box Plot"
                    ],
                    key="distribution_chart_type"
                )

            distribution_data = df[
                distribution_column
            ].dropna()

            if not distribution_data.empty:

                if distribution_chart_type == "Histogram":

                    distribution_figure = px.histogram(
                        df,
                        x=distribution_column,
                        nbins=30,
                        title=f"Distribution of {distribution_column}"
                    )

                else:

                    distribution_figure = px.box(
                        df,
                        y=distribution_column,
                        points="outliers",
                        title=f"Box Plot of {distribution_column}"
                    )

                st.plotly_chart(
                    distribution_figure,
                    width="stretch"
                )

                dist1, dist2, dist3, dist4 = st.columns(4)

                with dist1:
                    st.metric(
                        "Mean",
                        f"{distribution_data.mean():,.2f}"
                    )

                with dist2:
                    st.metric(
                        "Median",
                        f"{distribution_data.median():,.2f}"
                    )

                with dist3:
                    st.metric(
                        "Minimum",
                        f"{distribution_data.min():,.2f}"
                    )

                with dist4:
                    st.metric(
                        "Maximum",
                        f"{distribution_data.max():,.2f}"
                    )

        else:

            st.info(
                "No numerical columns are available "
                "for distribution analysis."
            )


        # ------------------------------------------
        # CORRELATION ANALYSIS
        # ------------------------------------------

        st.markdown("#### Correlation Analysis")

        correlation_columns = numerical_columns.drop(
            columns=[
                column
                for column in possible_id_columns
                if column in numerical_columns.columns
            ],
            errors="ignore"
        )

        if correlation_columns.shape[1] >= 2:

            correlation_matrix = (
                correlation_columns.corr()
            )

            correlation_figure = px.imshow(
                correlation_matrix,
                text_auto=".2f",
                aspect="auto",
                title="Correlation Heatmap"
            )

            st.plotly_chart(
                correlation_figure,
                width="stretch"
            )


            # --------------------------------------
            # STRONGEST CORRELATIONS
            # --------------------------------------

            correlation_pairs = []

            correlation_column_names = (
                correlation_matrix.columns
            )

            for i in range(
                len(correlation_column_names)
            ):

                for j in range(
                    i + 1,
                    len(correlation_column_names)
                ):

                    column_1 = (
                        correlation_column_names[i]
                    )

                    column_2 = (
                        correlation_column_names[j]
                    )

                    correlation_value = (
                        correlation_matrix.loc[
                            column_1,
                            column_2
                        ]
                    )

                    if pd.notna(correlation_value):

                        correlation_pairs.append({
                            "Variable 1": column_1,
                            "Variable 2": column_2,
                            "Correlation":
                                round(
                                    correlation_value,
                                    3
                                ),
                            "Absolute Correlation":
                                abs(correlation_value)
                        })

            if correlation_pairs:

                correlation_pairs_df = pd.DataFrame(
                    correlation_pairs
                )

                correlation_pairs_df = (
                    correlation_pairs_df
                    .sort_values(
                        "Absolute Correlation",
                        ascending=False
                    )
                )

                strongest_relationships = (
                    correlation_pairs_df
                    .head(10)
                    .drop(
                        columns=[
                            "Absolute Correlation"
                        ]
                    )
                )

                st.markdown(
                    "##### Strongest Numerical Relationships"
                )

                st.caption(
                    "The numerical column pairs with the "
                    "strongest linear relationships."
                )

                st.dataframe(
                    strongest_relationships,
                    width="stretch",
                    hide_index=True
                )

        else:

            st.info(
                "At least two suitable numerical columns "
                "are required for correlation analysis."
            )


        # ------------------------------------------
        # NUMERICAL RELATIONSHIP EXPLORER
        # ------------------------------------------

        st.markdown("#### Numerical Relationship Explorer")

        st.caption(
            "Compare two numerical variables using "
            "an interactive scatter plot."
        )

        relationship_columns = [
            column
            for column in numerical_columns.columns
            if column not in possible_id_columns
        ]

        if len(relationship_columns) >= 2:

            relationship_control1, relationship_control2 = st.columns(2)

            with relationship_control1:

                x_axis_column = st.selectbox(
                    "Select X-axis variable",
                    relationship_columns,
                    key="relationship_x"
                )

            with relationship_control2:

                default_y_index = (
                    1
                    if len(relationship_columns) > 1
                    else 0
                )

                y_axis_column = st.selectbox(
                    "Select Y-axis variable",
                    relationship_columns,
                    index=default_y_index,
                    key="relationship_y"
                )

            if x_axis_column != y_axis_column:

                relationship_data = df[
                    [
                        x_axis_column,
                        y_axis_column
                    ]
                ].dropna()

                if not relationship_data.empty:

                    scatter_figure = px.scatter(
                        relationship_data,
                        x=x_axis_column,
                        y=y_axis_column,
                        title=(
                            f"{y_axis_column} vs "
                            f"{x_axis_column}"
                        ),
                        trendline=None
                    )

                    st.plotly_chart(
                        scatter_figure,
                        width="stretch"
                    )

                    relationship_correlation = (
                        relationship_data[
                            x_axis_column
                        ].corr(
                            relationship_data[
                                y_axis_column
                            ]
                        )
                    )

                    if pd.notna(
                        relationship_correlation
                    ):

                        st.metric(
                            "Correlation",
                            f"{relationship_correlation:.3f}"
                        )

            else:

                st.info(
                    "Select two different numerical variables "
                    "to explore their relationship."
                )

        else:

            st.info(
                "At least two suitable numerical columns "
                "are required for relationship analysis."
            )


        # ------------------------------------------
        # CATEGORICAL PATTERNS
        # ------------------------------------------

        st.markdown("#### Top Categories")

        categorical_analysis_columns = [
            column
            for column in categorical_columns
            if column not in possible_id_columns
            and column not in constant_columns
        ]

        if categorical_analysis_columns:

            category_control1, category_control2 = st.columns(2)

            with category_control1:

                selected_category_column = st.selectbox(
                    "Select a categorical column",
                    categorical_analysis_columns,
                    key="category_column"
                )

            with category_control2:

                category_chart_type = st.selectbox(
                    "Select a chart type",
                    [
                        "Bar Chart",
                        "Pie Chart"
                    ],
                    key="category_chart_type"
                )

            category_counts = (
                df[selected_category_column]
                .dropna()
                .astype(str)
                .value_counts()
                .head(10)
                .reset_index()
            )

            category_counts.columns = [
                selected_category_column,
                "Count"
            ]

            if not category_counts.empty:

                if category_chart_type == "Bar Chart":

                    category_figure = px.bar(
                        category_counts,
                        x=selected_category_column,
                        y="Count",
                        title=(
                            f"Top Categories in "
                            f"{selected_category_column}"
                        )
                    )

                else:

                    category_figure = px.pie(
                        category_counts,
                        names=selected_category_column,
                        values="Count",
                        title=(
                            f"Category Distribution in "
                            f"{selected_category_column}"
                        )
                    )

                st.plotly_chart(
                    category_figure,
                    width="stretch"
                )

                st.dataframe(
                    category_counts,
                    width="stretch",
                    hide_index=True
                )

        else:

            st.info(
                "No suitable categorical columns are "
                "available for category analysis."
            )


        # ------------------------------------------
        # DATE COLUMN DETECTION
        # ------------------------------------------

        detected_date_columns = []

        for column in df.columns:

            if column in numerical_column_names:
                continue

            column_name_lower = str(
                column
            ).lower()

            date_name_hint = any(
                keyword in column_name_lower
                for keyword in [
                    "date",
                    "time",
                    "year",
                    "month",
                    "day"
                ]
            )

            if not date_name_hint:
                continue

            non_null_values = (
                df[column]
                .dropna()
            )

            if len(non_null_values) == 0:
                continue

            converted_dates = pd.to_datetime(
                non_null_values,
                errors="coerce"
            )

            valid_date_percentage = (
                converted_dates.notna().mean()
            )

            if valid_date_percentage >= 0.8:

                detected_date_columns.append(
                    column
                )


        # ------------------------------------------
        # TIME-BASED TRENDS
        # ------------------------------------------

        st.markdown("#### Time-Based Trends")

        if (
            detected_date_columns
            and not numerical_columns.empty
        ):

            trend_col1, trend_col2 = st.columns(2)

            with trend_col1:

                selected_date_column = st.selectbox(
                    "Select a date column",
                    detected_date_columns,
                    key="date_column"
                )

            trend_numeric_columns = [
                column
                for column in numerical_columns.columns
                if column not in possible_id_columns
            ]

            if trend_numeric_columns:

                with trend_col2:

                    selected_value_column = st.selectbox(
                        "Select a numerical value",
                        trend_numeric_columns,
                        key="trend_value"
                    )

                trend_data = df[
                    [
                        selected_date_column,
                        selected_value_column
                    ]
                ].copy()

                trend_data[
                    selected_date_column
                ] = pd.to_datetime(
                    trend_data[
                        selected_date_column
                    ],
                    errors="coerce"
                )

                trend_data = trend_data.dropna()

                trend_data = (
                    trend_data
                    .groupby(
                        selected_date_column,
                        as_index=False
                    )[
                        selected_value_column
                    ]
                    .mean()
                    .sort_values(
                        selected_date_column
                    )
                )

                if not trend_data.empty:

                    trend_figure = px.line(
                        trend_data,
                        x=selected_date_column,
                        y=selected_value_column,
                        markers=True,
                        title=(
                            f"{selected_value_column} "
                            f"Over Time"
                        )
                    )

                    st.plotly_chart(
                        trend_figure,
                        width="stretch"
                    )

                    st.caption(
                        "Values with the same date are averaged "
                        "to show the overall time-based trend."
                    )

            else:

                st.info(
                    "No suitable numerical columns are "
                    "available for time-based analysis."
                )

        else:

            st.info(
                "No reliable date column was detected. "
                "Time-based analysis is only shown when Insight "
                "can confidently identify a date or time column."
            )
                    # ==================================================
        # STEP 9 — AI ANALYST
        # ==================================================

        st.divider()

        st.subheader("AI Analyst")

        st.caption(
            "Generate a plain-English interpretation of Insight's "
            "deterministic Python analysis results."
        )

        generate_ai_analysis = st.button(
            "Generate AI Analysis",
            type="primary"
        )
    
        if generate_ai_analysis:

            with st.spinner("AI Analyst is reviewing the results..."):

                try:

                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        instructions=(
                            "You are the AI Analyst for Insight, a data analysis application. "
                            "Interpret only the deterministic analysis results provided to you. "
                            "Do not invent statistics, correlations, trends, or conclusions that "
                            "are not supported by the supplied report. "
                            "Clearly distinguish detected issues from confirmed errors. "
                            "Potential outliers should be described as observations requiring review, "
                            "not automatically as incorrect data. "
                            "Write a concise, professional analysis in plain English. "
                            "Organize the response into: Overall Assessment, Key Findings, "
                            "Data Quality Concerns, and Recommended Next Steps."
                        ),
                        input=str(analysis_report)
                    )

                    st.markdown("### AI Analysis")

                    st.markdown(
                        response.output_text
                    )
                except Exception as e:

                    error_message = str(e).lower()

                    if "insufficient_quota" in error_message or "429" in error_message:
                        st.warning(
                            "The AI Analyst is temporarily unavailable because the API quota "
                            "has been reached. Your dataset analysis is still available above."
                        )
                    else:
                        st.error(
                            "The AI Analyst could not generate an analysis. "
                            "Please try again later."
                        )

    except Exception as e:

                            st.error(
                                "Insight could not read or analyse this CSV file."
                            )

                            st.error(
                                f"Error details: {e}"
                            )


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

else:

    st.info(
        "Upload a CSV file from the sidebar to begin your analysis."
    )