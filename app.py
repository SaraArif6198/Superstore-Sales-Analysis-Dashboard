import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import json
import time
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import numpy as np

# --- Config ---
st.set_page_config(page_title="Superstore Dashboard", layout="wide")

st.markdown("""
    <style>
    [data-testid="stHeader"] { height: 0px !important; }
    .stApp { animation: fadeIn 0.8s ease-in; }

    /* Layout Padding Reduction */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .section-title {
    background: linear-gradient(to right, #ff6b6b, #ffb88c, #f9f871); /* Tutti Frutti Gradient */
    padding: 0.7rem 1.5rem;
    border-radius: 1rem;
    color: #1E1E1E; /* Dark Text */
    font-size: 26px;
    font-weight: bold;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    margin-bottom: 1rem;
    text-align: center;
    animation: slideFadeIn 0.8s ease-out;
    transform-origin: top center;
}
    .stApp {
    animation: fadeIn 0.8s ease-in;
    background-color: #FFFBEA !important; /* Banana Cream */
}
            
    @keyframes slideFadeIn {
        0% {
            opacity: 0;
            transform: translateY(-20px) scale(0.98);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Subtitle */
    .subtitle {
        font-size: 16px;
        color: #555;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Plot & Table spacing */
    .stPlotlyChart, .stDataFrame {
        margin-bottom: 0.5rem !important;
    }

    /* Metric spacing */
    .stMetric {
        margin-bottom: 0.3rem !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 14px;
        margin-top: 1.5rem;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_superstore.csv", parse_dates=["order_date"])
    df['order_period'] = df['order_date'].dt.to_period("M").astype(str)
    return df

df = load_data()

# --- Lottie ---
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_dashboard = load_lottiefile("lottie/dashboard.json")

# --- Initialize Session State ---
if "selected_region" not in st.session_state:
    st.session_state.selected_region = df["region"].unique().tolist()
if "selected_category" not in st.session_state:
    st.session_state.selected_category = df["category"].unique().tolist()
if "selected_segment" not in st.session_state:
    st.session_state.selected_segment = df["segment"].unique().tolist()

# --- Sidebar ---
with st.sidebar:
    
    selected = option_menu(
        "Main Menu",
        [" Home", " Sales", " Customers", " Products", " Trends", " Category", " Location", " Shipping"," Forecast"],
        icons=["house", "bar-chart", "people", "box", "graph-up", "calculator", "geo", "truck"],
        menu_icon="cast",
        default_index=0,
    )

     with st.sidebar.expander("👩‍💻 About Author", expanded=False):
    st.markdown("""
        <div style="
            background: linear-gradient(90deg, #ffb88c, #f9f871);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            ">
            <h3 style="margin-bottom: 0.3rem; color: #1E1E1E;">Sara Arif</h3>
            <p style="font-size: 14px; color: #333; margin: 0;">
                A passionate <b>Data Enthusiast 🚀</b><br>
                Skilled in <em>SQL, Power BI, Python & AI</em><br>
                I love turning raw data into meaningful insights.
            </p>
            <p style="margin-top: 0.5rem;">
                🌐 <a href="https://github.com/SaraArif6198" target="_blank" style="color:#FF4B4B; text-decoration: none;">GitHub</a> |
                💼 <a href="https://www.linkedin.com/in/sara-arif-7922642b8/" target="_blank" style="color:#0077b5; text-decoration: none;">LinkedIn</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- Global Filters ---
    selected_region = st.multiselect(
        " Filter by Region:",
        options=df["region"].unique(),
        default=st.session_state.selected_region,
        help="Select one or more regions to view region-specific sales and profit data."
    )
    st.session_state.selected_region = selected_region

    selected_category = st.multiselect(
        " Filter by Category:",
        options=df["category"].unique(),
        default=st.session_state.selected_category,
        help="Choose product categories to focus the dashboard on specific types of products."
    )
    st.session_state.selected_category = selected_category

    selected_segment = st.multiselect(
        " Filter by Segment:",
        options=df["segment"].unique(),
        default=st.session_state.selected_segment,
        help="Segment refers to the type of customers (e.g., Corporate, Consumer, Home Office)."
    )
    st.session_state.selected_segment = selected_segment
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()

    date_range_help = (
        f" Dataset contains orders from **{min_date.date()}** to **{max_date.date()}**.\n"
        "Use the date picker below to filter records within this time period."
    )

    selected_date = st.date_input(
        " Select Date Range:",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
        help=date_range_help
    )

filtered_df = df[
    (df["region"].isin(selected_region)) &
    (df["category"].isin(selected_category)) &
    (df["segment"].isin(selected_segment)) &
    (df["order_date"] >= pd.to_datetime(selected_date[0])) &
    (df["order_date"] <= pd.to_datetime(selected_date[1]))
]

# --- Animated Counter ---
def simple_animated_number(value, prefix="", format_type="int"):
    placeholder = st.empty()
    steps = 20
    delay = 0.02
    increment = value // steps if value > steps else 1
    for i in range(0, value, increment):
        formatted = f"{prefix}{i:,}" if format_type == "int" else f"{prefix}{i:,.2f}"
        placeholder.markdown(f"### {formatted}")
        time.sleep(delay)
    final_value = f"{prefix}{value:,}" if format_type == "int" else f"{prefix}{value:,.2f}"
    placeholder.markdown(f"### {final_value}")

# ===============================
#             PAGES
# ===============================

# --- HOME ---
if selected == " Home":
    
    st.markdown("<div class='section-title'>Global Superstore Dashboard</div>", unsafe_allow_html=True)
    st.markdown(" This page gives a quick snapshot of overall performance. You can instantly see how much was sold, how much profit was earned, and how much quantity was moved across all orders.", unsafe_allow_html=True)
    st_lottie(lottie_dashboard, height=250, key="dashboard")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🧾 Total Sales**")
        simple_animated_number(int(filtered_df['sales'].sum()), prefix="$", format_type="float")
    with col2:
        st.markdown("**💰 Total Profit**")
        simple_animated_number(int(filtered_df['profit'].sum()), prefix="$", format_type="float")
    with col3:
        st.markdown("**📦 Total Quantity**")
        simple_animated_number(int(filtered_df['quantity'].sum()), format_type="int")

# --- SALES ---
elif selected == " Sales":
    st.markdown("<div class='section-title'> Sales Overview</div>", unsafe_allow_html=True)
    st.markdown(" Here we dive deeper into sales and profit by region and segment. This helps us identify which markets and customer types are performing best or need attention.", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(filtered_df.groupby('region')['sales'].sum().reset_index(),
                      x='region', y='sales', title=' Sales by Region', color='region')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(filtered_df.groupby('segment')['profit'].sum().reset_index(),
                      x='segment', y='profit', title=' Profit by Segment', color='segment')
        st.plotly_chart(fig2, use_container_width=True)

    monthly = filtered_df.groupby('order_period')['sales'].sum().reset_index()
    fig3 = px.line(monthly, x='order_period', y='sales', title=' Monthly Sales Trend', markers=True)
    st.plotly_chart(fig3, use_container_width=True)

# --- CUSTOMERS ---
elif selected == " Customers":
    st.markdown("<div class='section-title'> Customer Insights</div>", unsafe_allow_html=True)
    st.markdown(" This section tells the story of our customers—who are buying the most, who's giving us the most profit, and who might be less profitable. Great for identifying high-value customers.", unsafe_allow_html=True)
    
    customer_sales = filtered_df.groupby('customer_name').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order_id': 'count',
        'discount': 'mean'
    }).reset_index()
    customer_sales['avg_order_value'] = customer_sales['sales'] / customer_sales['order_id']
    high_value_threshold = customer_sales['sales'].quantile(0.75)
    filter_type = st.radio("Select Customer Segment:", ["All", "High-Value", "Low-Value"])
    if filter_type == "High-Value":
        customer_sales = customer_sales[customer_sales['sales'] >= high_value_threshold]
    elif filter_type == "Low-Value":
        customer_sales = customer_sales[customer_sales['sales'] < high_value_threshold]
    st.metric(" Avg. Order Value", f"${customer_sales['avg_order_value'].mean():,.2f}")
    st.metric(" Avg. Discount", f"{customer_sales['discount'].mean():.2%}")
    search_name = st.text_input(" Search Customer by Name")
    if search_name:
        customer_sales = customer_sales[customer_sales['customer_name'].str.contains(search_name, case=False)]
    top_profit = customer_sales.nlargest(10, 'profit')
    bottom_profit = customer_sales.nsmallest(10, 'profit')
    tab1, tab2 = st.tabs([" Visuals", " Full Table"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(top_profit, x='profit', y='customer_name', orientation='h', title=" Top 10 Customers by Profit")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.bar(bottom_profit, x='profit', y='customer_name', orientation='h', title=" Bottom 10 Customers by Profit")
            st.plotly_chart(fig2, use_container_width=True)
    with tab2:
        st.dataframe(customer_sales.sort_values(by='sales', ascending=False))
        csv = customer_sales.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Customer Data", csv, "customers.csv", "text/csv")

# --- PRODUCTS ---
elif selected == " Products":
    st.markdown("<div class='section-title'> Product Performance</div>", unsafe_allow_html=True)
    st.markdown(" This page shows which products are generating high sales and profit—and flags any products with high sales but negative profit. Helps in product-level decision-making.", unsafe_allow_html=True)
    
    cat = st.selectbox("Choose Category:", options=filtered_df['category'].unique())
    subcat = st.multiselect("Choose Sub-Category:", options=filtered_df[filtered_df['category'] == cat]['sub-category'].unique())
    prod_df = filtered_df[filtered_df['category'] == cat]
    if subcat:
        prod_df = prod_df[prod_df['sub-category'].isin(subcat)]
    st.metric(" Avg. Discount", f"{prod_df['discount'].mean():.2%}")
    search_product = st.text_input("🔍 Search Product by Name")
    if search_product:
        prod_df = prod_df[prod_df['product_name'].str.contains(search_product, case=False)]
    tab1, tab2 = st.tabs([" Visuals", " Full Table"])
    with tab1:
        pivot = prod_df.pivot_table(values='profit', index='product_name', columns='discount', aggfunc='sum', fill_value=0)
        fig = px.imshow(pivot, title=" Discount vs. Profit Heatmap")
        st.plotly_chart(fig, use_container_width=True)
        alerts = prod_df.groupby('product_name').agg({'sales': 'sum', 'profit': 'sum'})
        alerts = alerts[(alerts['sales'] > 5000) & (alerts['profit'] < 0)].reset_index()
        st.warning(f" {len(alerts)} Products have High Sales but Negative Profit")
        st.dataframe(alerts)
    with tab2:
        all_products = prod_df.groupby('product_name')[['sales', 'profit']].sum().reset_index()
        st.dataframe(all_products.sort_values(by='sales', ascending=False))
        csv = all_products.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Product Data", csv, "products.csv", "text/csv")

# --- TRENDS ---
elif selected == " Trends":
    st.markdown("<div class='section-title'> Trend Analysis</div>", unsafe_allow_html=True)
    st.markdown(" This section reveals trends over time—monthly, quarterly, or yearly—so we can track growth, seasonality, or dips in sales and profit across categories.", unsafe_allow_html=True)
    

    view_by = st.radio(" View By:", ["Month", "Quarter", "Year"])
    if view_by == "Month":
        filtered_df['period'] = filtered_df['order_date'].dt.to_period("M")
    elif view_by == "Quarter":
        filtered_df['period'] = filtered_df['order_date'].dt.to_period("Q")
    else:
        filtered_df['period'] = filtered_df['order_date'].dt.to_period("Y")

    trends = filtered_df.groupby(['period', 'category'])[['sales', 'profit', 'quantity']].sum().reset_index()
    trends['period'] = trends['period'].astype(str)

    tab1, tab2 = st.tabs([" Sales Trends", " Full Data"])
    with tab1:
        fig = px.line(trends, x='period', y='sales', color='category', title=' Sales Trends by Category')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.dataframe(trends.sort_values(by='period'))
        csv = trends.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Trend Data", csv, "trends.csv", "text/csv")

# --- CATEGORY ---
elif selected == " Category":
    st.markdown("<div class='section-title'> Category Insights</div>", unsafe_allow_html=True)
    st.markdown(" We break down performance by category and sub-category here. You can explore which combinations are selling more and which offer better profit margins.", unsafe_allow_html=True)
    
    cat_data = filtered_df.groupby(['category', 'sub-category']).agg({
        'sales': 'sum', 'profit': 'sum', 'quantity': 'sum'
    }).reset_index()
    cat_data['avg_order_size'] = cat_data['quantity'] / len(filtered_df['order_id'].unique())
    cat_data['profit_margin'] = (cat_data['profit'] / cat_data['sales']) * 100
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        st.metric(" Avg Order Size", f"{cat_data['avg_order_size'].mean():.2f}")
    with kpi2:
        st.metric(" Avg Profit Margin", f"{cat_data['profit_margin'].mean():.2f}%")
    tab1, tab2 = st.tabs([" Visual Analysis", " Data Table"])
    with tab1:
        fig1 = px.treemap(
            cat_data,
            path=['category', 'sub-category'],
            values='sales',
            color='profit_margin',
            color_continuous_scale='RdYlGn',
            hover_data={'sales': ':.2f', 'profit': ':.2f', 'avg_order_size': True, 'profit_margin': ':.2f'}
        )
        fig1.update_layout(title=' Sales & Profit Margin by Category/Sub-Category')
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        search = st.text_input("🔎 Search Sub-Category:")
        filtered = cat_data[cat_data['sub-category'].str.contains(search, case=False)] if search else cat_data
        st.dataframe(filtered[['category', 'sub-category', 'sales', 'profit', 'avg_order_size', 'profit_margin']])
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Table as CSV", csv, "category_summary.csv", "text/csv")

# --- LOCATION ---
elif selected == " Location":
    st.markdown("<div class='section-title'> Location Performance</div>", unsafe_allow_html=True)
    st.markdown(" This page visualizes performance by state. It tells us where we’re doing well geographically and highlights locations that may need attention.", unsafe_allow_html=True)
    
    loc_summary = filtered_df.groupby('state')[['sales', 'profit']].sum().reset_index()
    loc_summary['text'] = loc_summary['state'] + '<br>Sales: $' + loc_summary['sales'].round().astype(str)
    tab1, tab2 = st.tabs([" Map", " State Data"])
    with tab1:
        fig = px.scatter_geo(loc_summary, locations="state", locationmode="USA-states", scope="usa",
                             size="sales", hover_name="state", color="profit", title=" Sales & Profit by State")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        loss_states = loc_summary.sort_values(by='profit').head(5)
        st.warning(" Top 5 Loss-Making States")
        st.dataframe(loss_states[['state', 'profit']])
        st.dataframe(loc_summary.sort_values(by='sales', ascending=False))
        csv = loc_summary.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Location Data", csv, "locations.csv", "text/csv")

# --- SHIPPING ---
elif selected == " Shipping":
    st.markdown("<div class='section-title'> Shipping Analytics</div>", unsafe_allow_html=True)
    st.markdown(" Here, we analyze how different shipping modes impact sales, profit, and average quantity. This helps understand delivery preferences and their business impact.", unsafe_allow_html=True)
   
    shipping_summary = filtered_df.groupby('ship_mode').agg({
        'order_id': 'count',
        'sales': 'sum',
        'quantity': 'mean',
        'profit': 'sum'
    }).reset_index()
    shipping_summary['reorder_rate'] = shipping_summary['order_id'] / shipping_summary['quantity']
    tab1, tab2 = st.tabs([" Visuals", " Shipping Data"])
    with tab1:
        fig1 = px.pie(shipping_summary, names='ship_mode', values='sales', title=' Sales Share by Shipping Mode')
        st.plotly_chart(fig1, use_container_width=True)
        fig2 = px.bar(shipping_summary, x='ship_mode', y='profit', title=' Profit by Shipping Mode')
        st.plotly_chart(fig2, use_container_width=True)
    with tab2:
        st.dataframe(shipping_summary[['ship_mode', 'quantity', 'reorder_rate']])
        csv = shipping_summary.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Shipping Data", csv, "shipping.csv", "text/csv")

# --- FORECAST ---
elif selected == " Forecast":
    st.markdown("<div class='section-title'> Sales Forecast with Evaluation</div>", unsafe_allow_html=True)
    with st.expander("📌 Final Conclusion & Key Business Insights"):
         st.markdown("""
    After performing exploratory data analysis, building an interactive dashboard, and implementing a forecasting model, here are the major business insights derived from the Global Superstore dataset:

    | **Insight Area**                        | **Observation**                                                                                              | **Recommendation**                                                                 |
    |----------------------------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
    | **1. Most Profitable Regions**         | West and East regions show higher total sales and profit. South lags behind.                                 | Focus marketing in West & East; analyze cost structures in South.                  |
    | **2. Top Customer Segments**           | Consumer segment leads in revenue. Corporate follows.                                                        | Target Consumer segment with loyalty/upsell programs.                              |
    | **3. Low-Profit High-Sale Products**   | Phones and Machines (Technology) show high sales but low or negative profits.                                | Reassess pricing and discounting; review supplier contracts.                       |
    | **4. Time-Based Seasonal Trends**      | Sales peak during Nov-Dec, but profits dip due to excessive discounts.                                       | Adjust discount strategies; manage inventory for Q4 spikes.                        |
    | **5. Forecasting & Accuracy**          | Prophet model forecasts show stable growth. MAPE = 6.56%, RMSE = $20,267.07.                                 | Rely on forecasts for strategic planning and target setting.                       |
    | **6. Profit Alignment with Forecasts** | Profit trend follows predicted sales, indicating consistent business flow.                                   | Continue current operations but monitor deviations monthly.                        |
    | **Final Thoughts**                     | Dashboard includes historical + predictive analysis in one place.                                            | Use it to drive strategic decisions in marketing, product mix, and logistics.      |
    """, unsafe_allow_html=True)
    st.markdown(" This page forecasts future sales using Prophet and evaluates the model with MAPE and RMSE. You can also see the historical sales and profit over time.", unsafe_allow_html=True)

    # Filters
    filter_type = st.selectbox(" Forecast By:", ["region", "category", "segment"])
    value = st.selectbox(f"Select {filter_type.title()}:", options=df[filter_type].unique())
    months = st.slider(" Months to Forecast:", 3, 12, 6)

    # Filter + group data
    filtered = df[df[filter_type] == value]
    monthly = filtered.groupby(filtered['order_date'].dt.to_period("M"))['sales'].sum().reset_index()
    monthly['order_date'] = monthly['order_date'].dt.to_timestamp()
    ts = monthly.rename(columns={'order_date': 'ds', 'sales': 'y'})

    # Fit Prophet model
    model = Prophet()
    model.fit(ts)

    # Make future df and forecast
    future = model.make_future_dataframe(periods=months, freq='M')
    forecast = model.predict(future)

    # Merge actuals with forecast for evaluation
    merged = ts.merge(forecast[['ds', 'yhat']], on='ds', how='left').dropna()
    mape = mean_absolute_percentage_error(merged['y'], merged['yhat']) * 100
    rmse = np.sqrt(mean_squared_error(merged['y'], merged['yhat']))

    # Show metrics
    st.metric(" MAPE (Accuracy)", f"{mape:.2f}%")
    st.metric(" RMSE", f"${rmse:,.2f}")

    # Forecast Plot
    fig = px.line(forecast, x='ds', y='yhat', title=f" Forecasted Sales for {value}")
    fig.add_scatter(x=ts['ds'], y=ts['y'], mode='lines', name='Historical Sales')
    st.plotly_chart(fig, use_container_width=True)

    # Profit over time
    profit_monthly = filtered.groupby(filtered['order_date'].dt.to_period("M"))['profit'].sum().reset_index()
    profit_monthly['order_date'] = profit_monthly['order_date'].dt.to_timestamp()
    fig2 = px.line(profit_monthly, x='order_date', y='profit', title=" Profit Over Time")
    fig.update_xaxes(dtick="M1", tickformat="%b %Y")
    st.plotly_chart(fig2, use_container_width=True)

# --- FOOTER ---
st.markdown("""
    <hr style="margin-top: 2rem; margin-bottom: 1rem;">
    <div class='footer'>
        Built with ❤️ using Streamlit | Created by 
        <a href="https://github.com/SaraArif6198" target="_blank" style="text-decoration: none; color: #FF4B4B;"><strong>Sara Arif</strong></a>
    </div>
""", unsafe_allow_html=True)



