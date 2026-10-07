# ============================================================
# RETAILSENSE AI
# Retail Sales Forecasting & Inventory Intelligence System
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression

from datetime import datetime, timedelta
import io

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RetailSense AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f8fc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.title {
    font-size: 38px;
    font-weight: 800;
    color: #111827;
}

.subtitle {
    color: #6b7280;
    font-size: 16px;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.07);
    border: 1px solid #e5e7eb;
}

.metric-title {
    color: #6b7280;
    font-size: 14px;
}

.metric-value {
    color: #111827;
    font-size: 28px;
    font-weight: 700;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 20px;
    color: #111827;
}

.alert-danger {
    padding: 15px;
    border-radius: 12px;
    background: #fee2e2;
    border-left: 5px solid #dc2626;
    margin-bottom: 10px;
}

.alert-warning {
    padding: 15px;
    border-radius: 12px;
    background: #fef3c7;
    border-left: 5px solid #f59e0b;
    margin-bottom: 10px;
}

.alert-success {
    padding: 15px;
    border-radius: 12px;
    background: #dcfce7;
    border-left: 5px solid #16a34a;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# GENERATE DEMO DATA
# ============================================================

@st.cache_data
def generate_data():

    np.random.seed(42)

    dates = pd.date_range(
        start="2024-01-01",
        end="2026-09-30",
        freq="D"
    )

    stores = [
        "Mumbai Central",
        "Pune Central",
        "Delhi Central",
        "Bangalore Central",
        "Hyderabad Central"
    ]

    products = {
        "Laptop": "Electronics",
        "Smartphone": "Electronics",
        "Headphones": "Electronics",
        "T-Shirt": "Fashion",
        "Jeans": "Fashion",
        "Shoes": "Fashion",
        "Rice": "Grocery",
        "Cooking Oil": "Grocery",
        "Coffee": "Grocery",
        "Backpack": "Lifestyle"
    }

    rows = []

    for date in dates:

        month = date.month
        weekday = date.weekday()

        # Seasonal factor
        seasonal = 1.0

        if month in [10, 11]:
            seasonal = 1.35
        elif month in [12, 1]:
            seasonal = 1.20
        elif month in [4, 5]:
            seasonal = 1.10

        weekend_factor = 1.15 if weekday >= 5 else 1.0

        for store in stores:

            store_factor = {
                "Mumbai Central": 1.25,
                "Pune Central": 1.05,
                "Delhi Central": 1.20,
                "Bangalore Central": 1.15,
                "Hyderabad Central": 0.95
            }[store]

            for product, category in products.items():

                base_demand = {
                    "Laptop": 22,
                    "Smartphone": 35,
                    "Headphones": 48,
                    "T-Shirt": 55,
                    "Jeans": 42,
                    "Shoes": 38,
                    "Rice": 75,
                    "Cooking Oil": 68,
                    "Coffee": 60,
                    "Backpack": 32
                }[product]

                trend = 1 + (
                    (date - dates[0]).days / len(dates)
                ) * 0.35

                promotion = np.random.choice(
                    [0, 1],
                    p=[0.75, 0.25]
                )

                discount = 0

                if promotion:
                    discount = np.random.choice(
                        [5, 10, 15, 20]
                    )

                demand = (
                    base_demand
                    * store_factor
                    * seasonal
                    * weekend_factor
                    * trend
                )

                if promotion:
                    demand *= 1 + discount / 100 * 0.7

                noise = np.random.normal(
                    0,
                    max(2, demand * 0.12)
                )

                units = max(
                    0,
                    int(demand + noise)
                )

                price = {
                    "Laptop": 65000,
                    "Smartphone": 30000,
                    "Headphones": 2500,
                    "T-Shirt": 900,
                    "Jeans": 1800,
                    "Shoes": 2500,
                    "Rice": 900,
                    "Cooking Oil": 1400,
                    "Coffee": 450,
                    "Backpack": 1800
                }[product]

                price = price * (
                    1 - discount / 100
                )

                inventory = max(
                    0,
                    int(units * np.random.uniform(3, 8))
                )

                holiday = 1 if (
                    month in [10, 11, 12]
                ) else 0

                revenue = units * price

                rows.append([
                    date,
                    store,
                    product,
                    category,
                    units,
                    round(price, 2),
                    discount,
                    promotion,
                    inventory,
                    holiday,
                    round(revenue, 2)
                ])

    df = pd.DataFrame(
        rows,
        columns=[
            "Date",
            "Store",
            "Product",
            "Category",
            "Units_Sold",
            "Price",
            "Discount",
            "Promotion",
            "Inventory",
            "Holiday",
            "Revenue"
        ]
    )

    return df


# ============================================================
# LOAD DATA
# ============================================================

demo_data = generate_data()

st.sidebar.markdown("## 🛒 RetailSense AI")
st.sidebar.caption("Retail Forecasting & Inventory Intelligence")

st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Upload Retail CSV",
    type=["csv"]
)

if uploaded_file:

    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Date",
            "Store",
            "Product",
            "Category",
            "Units_Sold",
            "Price",
            "Discount",
            "Promotion",
            "Inventory",
            "Holiday",
            "Revenue"
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            st.error(
                "Missing columns: " +
                ", ".join(missing)
            )
            df = demo_data.copy()
        else:
            df["Date"] = pd.to_datetime(df["Date"])

    except Exception:
        st.error("Unable to read CSV. Using demo dataset.")
        df = demo_data.copy()

else:
    df = demo_data.copy()


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df["Date"] = pd.to_datetime(df["Date"])

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day
df["DayOfWeek"] = df["Date"].dt.dayofweek
df["Week"] = df["Date"].dt.isocalendar().week.astype(int)

df = df.sort_values("Date")


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📊 Sales Analytics",
        "🔮 Forecasting",
        "📦 Inventory Intelligence",
        "🏷️ Product Analysis",
        "🏪 Store Analysis",
        "🤖 Model Performance",
        "⚠️ Alerts",
        "📄 Reports"
    ]
)


# ============================================================
# COMMON FILTERS
# ============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

selected_category = st.sidebar.multiselect(
    "Category",
    sorted(df["Category"].unique()),
    default=list(df["Category"].unique())
)

selected_store = st.sidebar.multiselect(
    "Store",
    sorted(df["Store"].unique()),
    default=list(df["Store"].unique())
)

filtered_df = df[
    (df["Category"].isin(selected_category)) &
    (df["Store"].isin(selected_store))
].copy()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):
    if value >= 10000000:
        return f"₹{value / 10000000:.2f} Cr"
    elif value >= 100000:
        return f"₹{value / 100000:.2f} L"
    elif value >= 1000:
        return f"₹{value / 1000:.1f}K"
    else:
        return f"₹{value:,.0f}"


def create_forecast(data, product, store, days=30):

    temp = data[
        (data["Product"] == product) &
        (data["Store"] == store)
    ].copy()

    daily = temp.groupby("Date")["Units_Sold"].sum().reset_index()

    if len(daily) < 30:
        return None

    daily["lag_1"] = daily["Units_Sold"].shift(1)
    daily["lag_7"] = daily["Units_Sold"].shift(7)
    daily["lag_14"] = daily["Units_Sold"].shift(14)
    daily["rolling_7"] = (
        daily["Units_Sold"]
        .shift(1)
        .rolling(7)
        .mean()
    )
    daily["rolling_14"] = (
        daily["Units_Sold"]
        .shift(1)
        .rolling(14)
        .mean()
    )

    daily["dayofweek"] = daily["Date"].dt.dayofweek
    daily["month"] = daily["Date"].dt.month
    daily["day"] = daily["Date"].dt.day

    model_data = daily.dropna().copy()

    features = [
        "lag_1",
        "lag_7",
        "lag_14",
        "rolling_7",
        "rolling_14",
        "dayofweek",
        "month",
        "day"
    ]

    X = model_data[features]
    y = model_data["Units_Sold"]

    split = int(len(model_data) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        max_depth=12,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    # Future forecasting
    history = daily[
        ["Date", "Units_Sold"]
    ].copy()

    future_rows = []

    for i in range(days):

        next_date = (
            history["Date"].iloc[-1]
            + timedelta(days=1)
        )

        values = history["Units_Sold"].values

        lag1 = values[-1]
        lag7 = values[-7] if len(values) >= 7 else np.mean(values)
        lag14 = values[-14] if len(values) >= 14 else np.mean(values)

        rolling7 = np.mean(values[-7:])
        rolling14 = np.mean(values[-14:])

        X_future = pd.DataFrame([{
            "lag_1": lag1,
            "lag_7": lag7,
            "lag_14": lag14,
            "rolling_7": rolling7,
            "rolling_14": rolling14,
            "dayofweek": next_date.dayofweek,
            "month": next_date.month,
            "day": next_date.day
        }])

        prediction = max(
            0,
            model.predict(X_future)[0]
        )

        future_rows.append([
            next_date,
            prediction
        ])

        history = pd.concat([
            history,
            pd.DataFrame({
                "Date": [next_date],
                "Units_Sold": [prediction]
            })
        ], ignore_index=True)

    forecast = pd.DataFrame(
        future_rows,
        columns=[
            "Date",
            "Forecast"
        ]
    )

    return (
        daily,
        forecast,
        model,
        mae,
        rmse,
        r2
    )


# ============================================================
# PAGE 1: DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="title">RetailSense AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-powered retail sales forecasting and inventory intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    total_revenue = filtered_df["Revenue"].sum()
    total_units = filtered_df["Units_Sold"].sum()
    avg_daily_sales = (
        filtered_df.groupby("Date")["Units_Sold"]
        .sum()
        .mean()
    )

    products_count = filtered_df["Product"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Total Revenue",
            money(total_revenue)
        )

    with col2:
        st.metric(
            "📦 Units Sold",
            f"{total_units:,}"
        )

    with col3:
        st.metric(
            "📈 Avg Daily Sales",
            f"{avg_daily_sales:,.0f}"
        )

    with col4:
        st.metric(
            "🏷️ Products",
            products_count
        )

    st.markdown("### 📈 Sales Trend")

    daily_sales = (
        filtered_df
        .groupby("Date")
        .agg({
            "Units_Sold": "sum",
            "Revenue": "sum"
        })
        .reset_index()
    )

    fig = px.line(
        daily_sales,
        x="Date",
        y="Revenue",
        title="Daily Revenue Trend"
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:

        category_sales = (
            filtered_df
            .groupby("Category")["Revenue"]
            .sum()
            .reset_index()
            .sort_values(
                "Revenue",
                ascending=False
            )
        )

        fig = px.bar(
            category_sales,
            x="Category",
            y="Revenue",
            title="Revenue by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        top_products = (
            filtered_df
            .groupby("Product")["Revenue"]
            .sum()
            .reset_index()
            .sort_values(
                "Revenue",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top_products,
            x="Revenue",
            y="Product",
            orientation="h",
            title="Top 10 Products"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAGE 2: SALES ANALYTICS
# ============================================================

elif page == "📊 Sales Analytics":

    st.title("📊 Sales Analytics")

    col1, col2 = st.columns(2)

    with col1:

        monthly = (
            filtered_df
            .set_index("Date")
            .resample("ME")
            .agg({
                "Revenue": "sum",
                "Units_Sold": "sum"
            })
            .reset_index()
        )

        fig = px.bar(
            monthly,
            x="Date",
            y="Revenue",
            title="Monthly Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        weekday = (
            filtered_df
            .groupby("DayOfWeek")["Units_Sold"]
            .mean()
            .reset_index()
        )

        weekday["Day"] = weekday["DayOfWeek"].map({
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        })

        fig = px.bar(
            weekday,
            x="Day",
            y="Units_Sold",
            title="Average Sales by Day"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("📅 Monthly Performance")

    monthly["Revenue Growth %"] = (
        monthly["Revenue"]
        .pct_change() * 100
    )

    st.dataframe(
        monthly.round(2),
        use_container_width=True
    )


# ============================================================
# PAGE 3: FORECASTING
# ============================================================

elif page == "🔮 Forecasting":

    st.title("🔮 AI Demand Forecasting")

    col1, col2, col3 = st.columns(3)

    with col1:
        product = st.selectbox(
            "Select Product",
            sorted(df["Product"].unique())
        )

    with col2:
        store = st.selectbox(
            "Select Store",
            sorted(df["Store"].unique())
        )

    with col3:
        forecast_days = st.selectbox(
            "Forecast Period",
            [7, 14, 30, 60, 90],
            index=2
        )

    result = create_forecast(
        df,
        product,
        store,
        forecast_days
    )

    if result is None:

        st.error(
            "Not enough historical data for forecasting."
        )

    else:

        daily, forecast, model, mae, rmse, r2 = result

        st.markdown("### 🤖 Model Performance")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "MAE",
            f"{mae:.2f}"
        )

        c2.metric(
            "RMSE",
            f"{rmse:.2f}"
        )

        c3.metric(
            "R² Score",
            f"{r2:.2f}"
        )

        st.markdown("### 📈 Actual vs Forecast")

        recent = daily.tail(90).copy()

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=recent["Date"],
                y=recent["Units_Sold"],
                mode="lines",
                name="Actual Sales"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=forecast["Date"],
                y=forecast["Forecast"],
                mode="lines+markers",
                name="Forecast"
            )
        )

        fig.update_layout(
            title=f"{product} — {store}",
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("### 🔮 Forecast Results")

        display_forecast = forecast.copy()

        display_forecast["Forecast"] = (
            display_forecast["Forecast"]
            .round(0)
            .astype(int)
        )

        st.dataframe(
            display_forecast,
            use_container_width=True
        )

        total_forecast = forecast["Forecast"].sum()
        avg_forecast = forecast["Forecast"].mean()

        c1, c2 = st.columns(2)

        c1.metric(
            "Expected Units",
            f"{total_forecast:,.0f}"
        )

        c2.metric(
            "Average Daily Demand",
            f"{avg_forecast:,.0f}"
        )


# ============================================================
# PAGE 4: INVENTORY
# ============================================================

elif page == "📦 Inventory Intelligence":

    st.title("📦 Inventory Intelligence")

    st.info(
        "Inventory recommendations are based on forecasted demand, "
        "lead time and safety stock."
    )

    lead_time = st.slider(
        "Supplier Lead Time (Days)",
        1,
        30,
        7
    )

    safety_days = st.slider(
        "Safety Stock (Days)",
        1,
        15,
        3
    )

    inventory_data = (
        filtered_df
        .groupby(
            ["Product", "Store"]
        )
        .agg({
            "Inventory": "last",
            "Units_Sold": "mean",
            "Revenue": "sum"
        })
        .reset_index()
    )

    inventory_data["Daily Demand"] = (
        inventory_data["Units_Sold"]
    )

    inventory_data["Reorder Point"] = (
        inventory_data["Daily Demand"]
        * (lead_time + safety_days)
    )

    inventory_data["Recommended Order"] = (
        inventory_data["Reorder Point"]
        - inventory_data["Inventory"]
    ).clip(lower=0)

    def stock_status(row):

        if row["Inventory"] <= row["Daily Demand"] * lead_time:
            return "🔴 Critical"

        elif row["Inventory"] < row["Reorder Point"]:
            return "🟡 Reorder"

        else:
            return "🟢 Healthy"

    inventory_data["Status"] = (
        inventory_data.apply(
            stock_status,
            axis=1
        )
    )

    critical = len(
        inventory_data[
            inventory_data["Status"] == "🔴 Critical"
        ]
    )

    reorder = len(
        inventory_data[
            inventory_data["Status"] == "🟡 Reorder"
        ]
    )

    healthy = len(
        inventory_data[
            inventory_data["Status"] == "🟢 Healthy"
        ]
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🔴 Critical",
        critical
    )

    c2.metric(
        "🟡 Reorder",
        reorder
    )

    c3.metric(
        "🟢 Healthy",
        healthy
    )

    st.subheader("Inventory Status")

    st.dataframe(
        inventory_data.round(1),
        use_container_width=True
    )

    st.subheader("📊 Current Inventory vs Reorder Point")

    chart_data = inventory_data.head(30)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=chart_data["Product"],
            y=chart_data["Inventory"],
            name="Current Inventory"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_data["Product"],
            y=chart_data["Reorder Point"],
            mode="lines+markers",
            name="Reorder Point"
        )
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 5: PRODUCT ANALYSIS
# ============================================================

elif page == "🏷️ Product Analysis":

    st.title("🏷️ Product Analysis")

    product_summary = (
        filtered_df
        .groupby(
            ["Product", "Category"]
        )
        .agg({
            "Units_Sold": "sum",
            "Revenue": "sum",
            "Price": "mean",
            "Discount": "mean"
        })
        .reset_index()
    )

    product_summary = product_summary.sort_values(
        "Revenue",
        ascending=False
    )

    st.dataframe(
        product_summary.round(2),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            product_summary.head(10),
            x="Revenue",
            y="Product",
            orientation="h",
            title="Top Products by Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.scatter(
            product_summary,
            x="Units_Sold",
            y="Revenue",
            size="Price",
            color="Category",
            hover_name="Product",
            title="Product Demand vs Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAGE 6: STORE ANALYSIS
# ============================================================

elif page == "🏪 Store Analysis":

    st.title("🏪 Store Performance")

    store_summary = (
        filtered_df
        .groupby("Store")
        .agg({
            "Revenue": "sum",
            "Units_Sold": "sum",
            "Product": "nunique"
        })
        .reset_index()
    )

    store_summary.columns = [
        "Store",
        "Revenue",
        "Units Sold",
        "Products"
    ]

    st.dataframe(
        store_summary.round(2),
        use_container_width=True
    )

    fig = px.bar(
        store_summary.sort_values(
            "Revenue",
            ascending=False
        ),
        x="Store",
        y="Revenue",
        title="Revenue by Store"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.scatter(
        store_summary,
        x="Units Sold",
        y="Revenue",
        size="Products",
        hover_name="Store",
        title="Store Efficiency"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 7: MODEL PERFORMANCE
# ============================================================

elif page == "🤖 Model Performance":

    st.title("🤖 Forecasting Model Performance")

    st.write(
        "The system compares multiple forecasting approaches "
        "using historical sales."
    )

    product = st.selectbox(
        "Product",
        sorted(df["Product"].unique())
    )

    store = st.selectbox(
        "Store",
        sorted(df["Store"].unique())
    )

    temp = df[
        (df["Product"] == product) &
        (df["Store"] == store)
    ].copy()

    daily = (
        temp.groupby("Date")["Units_Sold"]
        .sum()
        .reset_index()
    )

    if len(daily) > 30:

        values = daily["Units_Sold"].values

        split = int(
            len(values) * 0.8
        )

        train = values[:split]
        test = values[split:]

        # -----------------------------
        # Moving Average
        # -----------------------------

        ma_predictions = []

        for i in range(len(test)):

            history = np.concatenate([
                train,
                test[:i]
            ])

            prediction = np.mean(
                history[-7:]
            )

            ma_predictions.append(
                prediction
            )

        ma_mae = mean_absolute_error(
            test,
            ma_predictions
        )

        ma_rmse = np.sqrt(
            mean_squared_error(
                test,
                ma_predictions
            )
        )

        # -----------------------------
        # Linear Regression
        # -----------------------------

        X = np.arange(
            len(values)
        ).reshape(-1, 1)

        lr = LinearRegression()

        lr.fit(
            X[:split],
            values[:split]
        )

        lr_predictions = lr.predict(
            X[split:]
        )

        lr_mae = mean_absolute_error(
            test,
            lr_predictions
        )

        lr_rmse = np.sqrt(
            mean_squared_error(
                test,
                lr_predictions
            )
        )

        # -----------------------------
        # Random Forest
        # -----------------------------

        result = create_forecast(
            df,
            product,
            store,
            7
        )

        if result:

            _, _, _, rf_mae, rf_rmse, rf_r2 = result

        else:

            rf_mae = 0
            rf_rmse = 0
            rf_r2 = 0

        model_results = pd.DataFrame({
            "Model": [
                "Moving Average",
                "Linear Regression",
                "Random Forest"
            ],
            "MAE": [
                ma_mae,
                lr_mae,
                rf_mae
            ],
            "RMSE": [
                ma_rmse,
                lr_rmse,
                rf_rmse
            ]
        })

        st.dataframe(
            model_results.round(2),
            use_container_width=True
        )

        fig = px.bar(
            model_results,
            x="Model",
            y="MAE",
            title="Model Comparison — Lower MAE is Better"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        best_model = model_results.loc[
            model_results["MAE"].idxmin(),
            "Model"
        ]

        st.success(
            f"🏆 Best performing model: **{best_model}**"
        )


# ============================================================
# PAGE 8: ALERTS
# ============================================================

elif page == "⚠️ Alerts":

    st.title("⚠️ Intelligent Alerts")

    # Inventory alerts

    inventory = (
        filtered_df
        .groupby(
            ["Product", "Store"]
        )
        .agg({
            "Inventory": "last",
            "Units_Sold": "mean"
        })
        .reset_index()
    )

    inventory["Days of Stock"] = (
        inventory["Inventory"] /
        inventory["Units_Sold"].replace(0, np.nan)
    )

    critical_items = inventory[
        inventory["Days of Stock"] < 5
    ]

    low_items = inventory[
        (inventory["Days of Stock"] >= 5) &
        (inventory["Days of Stock"] < 10)
    ]

    st.subheader("🔴 Critical Stock Alerts")

    if len(critical_items) == 0:

        st.success(
            "No critical stock alerts."
        )

    else:

        for _, row in critical_items.iterrows():

            st.markdown(
                f"""
                <div class="alert-danger">
                <b>🔴 {row['Product']}</b><br>
                Store: {row['Store']}<br>
                Current Inventory: {row['Inventory']:.0f}<br>
                Estimated Stock Remaining:
                {row['Days of Stock']:.1f} days
                </div>
                """,
                unsafe_allow_html=True
            )

    st.subheader("🟡 Low Stock Alerts")

    if len(low_items) == 0:

        st.success(
            "No low-stock alerts."
        )

    else:

        for _, row in low_items.iterrows():

            st.markdown(
                f"""
                <div class="alert-warning">
                <b>🟡 {row['Product']}</b><br>
                Store: {row['Store']}<br>
                Estimated Stock:
                {row['Days of Stock']:.1f} days
                </div>
                """,
                unsafe_allow_html=True
            )

    # Demand alerts

    st.subheader("📈 Demand Alerts")

    product_avg = (
        filtered_df
        .groupby("Product")["Units_Sold"]
        .mean()
    )

    highest = product_avg.idxmax()
    highest_value = product_avg.max()

    lowest = product_avg.idxmin()
    lowest_value = product_avg.min()

    st.markdown(
        f"""
        <div class="alert-success">
        📈 <b>Highest Average Demand</b><br>
        {highest}: {highest_value:.0f} units/day
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="alert-warning">
        📉 <b>Lowest Average Demand</b><br>
        {lowest}: {lowest_value:.0f} units/day
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 9: REPORTS
# ============================================================

elif page == "📄 Reports":

    st.title("📄 Business Reports")

    st.write(
        "Generate a downloadable summary of retail performance."
    )

    report = (
        filtered_df
        .groupby("Product")
        .agg({
            "Units_Sold": "sum",
            "Revenue": "sum",
            "Inventory": "mean",
            "Discount": "mean"
        })
        .reset_index()
    )

    report["Average Selling Price"] = (
        report["Revenue"] /
        report["Units_Sold"].replace(0, np.nan)
    )

    st.dataframe(
        report.round(2),
        use_container_width=True
    )

    # CSV download

    csv = report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Product Report CSV",
        data=csv,
        file_name="retailsense_report.csv",
        mime="text/csv"
    )

    # Full dataset

    full_csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Sales Data",
        data=full_csv,
        file_name="retail_sales_data.csv",
        mime="text/csv"
    )

    st.markdown("---")

    st.subheader("💡 AI Business Recommendations")

    total_revenue = filtered_df["Revenue"].sum()

    best_category = (
        filtered_df
        .groupby("Category")["Revenue"]
        .sum()
        .idxmax()
    )

    best_product = (
        filtered_df
        .groupby("Product")["Revenue"]
        .sum()
        .idxmax()
    )

    st.markdown(
        f"""
        ### Recommendations

        **1. Focus on {best_category}**

        This category currently generates the highest revenue.

        **2. Prioritize {best_product}**

        {best_product} is the highest revenue-generating product.

        **3. Use demand forecasting**

        Use the forecasting module before placing large inventory orders.

        **4. Monitor stockout risks**

        Products with low days of inventory should be reordered earlier.

        **5. Optimize promotions**

        Promotions should be focused on products with declining demand.

        **6. Store-level optimization**

        High-performing stores can be used as benchmarks for weaker stores.

        **Total analyzed revenue:** {money(total_revenue)}
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")
st.sidebar.caption(
    "RetailSense AI v1.0 | ML Retail Forecasting"
)

st.sidebar.caption(
    "Built with Python + Streamlit + Scikit-learn"
)