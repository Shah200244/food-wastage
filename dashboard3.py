import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

@st.cache_resource
def get_engine():
    return create_engine(
        "mssql+pyodbc://@SHAHID\\SQLEXPRESS/food?driver=ODBC+Driver+17+for+SQL+Server"
    )

engine = get_engine()

st.set_page_config(layout="wide")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login successful ✅")
        else:
            st.error("Invalid credentials ❌")

def dashboard():
    st.title("📊 Dashboard")

    df = pd.read_sql("SELECT * FROM food_listings_data", engine)

    if df.empty:
        st.warning("No data available")
        return

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(df))
    col2.metric("Total Quantity", int(df["Quantity"].sum()))
    col3.metric("Cities", df["Location"].nunique())

    st.divider()

    # Charts Row 1
    col4, col5 = st.columns(2)

    with col4:
        st.subheader("🍽️ Food Type Distribution")
        st.bar_chart(df["Food_Type"].value_counts())

    with col5:
        st.subheader("🥗 Meal Type Distribution")
        st.bar_chart(df["Meal_Type"].value_counts())

    # Pie Charts
    col6, col7 = st.columns(2)

    with col6:
        st.subheader("🥧 Food Type Share")
        st.pyplot(df["Food_Type"].value_counts().plot.pie(autopct="%1.1f%%").figure)

    with col7:
        st.subheader("🥗 Meal Type Share")
        st.pyplot(df["Meal_Type"].value_counts().plot.pie(autopct="%1.1f%%").figure)

    # City + Top Food
    col8, col9 = st.columns(2)

    with col8:
        st.subheader("🏙️ Food by City")
        st.bar_chart(df.groupby("Location")["Quantity"].sum())

    with col9:
        st.subheader("🔥 Top Food Items")
        st.bar_chart(df["Food_Name"].value_counts().head(10))

    # Trend
    st.subheader("📅 Expiry Trend")
    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors='coerce')
    trend = df.groupby(df["Expiry_Date"].dt.date)["Quantity"].sum()
    st.line_chart(trend)

    # Heatmap
    st.subheader("🌡️ Heatmap")
    pivot = df.pivot_table(
        values="Quantity",
        index="Location",
        columns="Food_Type",
        aggfunc="sum"
    )
    st.dataframe(pivot.style.background_gradient(cmap="coolwarm"))

    # Map
    st.subheader(" Food Locations")
    map_data = df[["Location"]].copy()
    map_data["lat"] = 28.61
    map_data["lon"] = 77.23
    st.map(map_data)


def food_listings():
    st.title("🍱 Food Listings")

    df = pd.read_sql("SELECT * FROM food_listings_data", engine)
    st.dataframe(df)

    # Filter
    st.subheader("🔍 Filter")
    city = st.selectbox("City", ["All"] + list(df["Location"].unique()))

    if city != "All":
        st.dataframe(df[df["Location"] == city])

    # Add
    st.subheader("➕ Add Food")
    name = st.text_input("Food Name")
    qty = st.number_input("Quantity")
    location = st.text_input("City")

    if st.button("Add Food"):
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO food_listings_data (Food_Name, Quantity, Location)
                VALUES (:name, :qty, :loc)
            """), {"name": name, "qty": qty, "loc": location})
        st.success("Food added!")

    # Delete
    delete_id = st.number_input("Food ID to delete")

    if st.button("Delete Food"):
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM food_listings_data WHERE Food_ID = :id
            """), {"id": delete_id})
        st.warning("Deleted!")

def analysis():
    st.title("📈 Analysis")

    df = pd.read_sql("SELECT * FROM food_listings_data", engine)
    claims = pd.read_sql("SELECT * FROM claims_data", engine)

    # Claim status pie
    st.subheader("📌 Claim Status")
    st.pyplot(claims["Status"].value_counts().plot.pie(autopct="%1.1f%%").figure)

    # Bar
    st.bar_chart(claims["Status"].value_counts())

    # Claims per food
    st.subheader(" Claims per Food")

    claims_food = pd.read_sql("""
    SELECT f.Food_Name, COUNT(c.Claim_ID) as total
    FROM claims_data c
    JOIN food_listings_data f ON c.Food_ID = f.Food_ID
    GROUP BY f.Food_Name
    """, engine)

    st.bar_chart(claims_food.set_index("Food_Name"))

    # Top providers
    st.subheader("Top Providers")

    top = pd.read_sql("""
    SELECT Provider_ID, SUM(Quantity) as Total
    FROM food_listings_data
    GROUP BY Provider_ID
    ORDER BY Total DESC
    """, engine)

    st.bar_chart(top.set_index("Provider_ID"))

    # Expiry alert
    st.subheader("⚠ Expiring Soon")

    expiring = pd.read_sql("""
    SELECT * FROM food_listings_data
    WHERE Expiry_Date <= DATEADD(day, 2, GETDATE())
    """, engine)

    st.dataframe(expiring)


if not st.session_state.logged_in:
    login()
else:
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Food Listings", "Analysis"]
    )

    if menu == "Dashboard":
        dashboard()

    elif menu == "Food Listings":
        food_listings()

    elif menu == "Analysis":
        analysis()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        