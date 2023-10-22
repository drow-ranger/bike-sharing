import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency


def create_ren_monthly_df(df):
    return df.resample("M", on="dteday").sum()


def create_ren_cas_df(df):
    return df.groupby("weekday").casual.sum().sort_values(ascending=False).reset_index()


def create_ren_reg_df(df):
    return (
        df.groupby("weekday")
        .registered.sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def create_byweather_df(df):
    return (
        df.groupby("weather_situation")["count"]
        .count()
        .sort_values(ascending=False)
        .reset_index()
    )


def create_rfm():
    recent_date = hour_df["dteday"].max()
    hour_df["recency"] = (recent_date - hour_df["dteday"]).dt.days
    rfm_df = hour_df.groupby("hour", as_index=False).agg(
        monetary=("count", "sum"),
        frequency=("count", "count"),
        recency=("recency", "min"),
    )
    return rfm_df[["hour", "frequency", "monetary", "recency"]]


def plot_rfm(df, column, title, ax, n=5):
    sns.barplot(
        y=column,
        x="hour",
        data=df.sort_values(by=column, ascending=False).head(n),
        palette=sns.color_palette("Spectral"),
        ax=ax,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title(title, loc="center", fontsize=18)
    ax.tick_params(axis="x", labelsize=15)


hour_df = pd.read_csv("hour_data.csv")
datetime_columns = ["dteday"]
hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)

for column in datetime_columns:
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date = hour_df["dteday"].min()
max_date = hour_df["dteday"].max()

with st.sidebar:
    st.image("bike-sharing.png")

    date_range = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        main_df = hour_df[
            (hour_df["dteday"] >= str(start_date))
            & (hour_df["dteday"] <= str(end_date))
        ]
    elif date_range and len(date_range) == 1:
        st.warning("Pilih rentang waktu terlebih dahulu.")
        main_df = hour_df[
            (hour_df["dteday"] >= str(min_date)) & (hour_df["dteday"] <= str(max_date))
        ]

ren_monthly_df = create_ren_monthly_df(main_df)
ren_cas_df = create_ren_cas_df(main_df)
ren_reg_df = create_ren_reg_df(main_df)
byweather_df = create_byweather_df(main_df)
rfm_df = create_rfm()

title = "Bike Sharing Dashboard"
st.header(title)

# Subheader 1
st.subheader("Rental By Months")
col1, col2, col3 = st.columns(3)
with col1:
    total_casual = ren_monthly_df.casual.sum()
    st.metric("Total Casual Rental", value=f"{total_casual:,}")

with col2:
    total_registered = ren_monthly_df.registered.sum()
    st.metric("Total Registered Rental", value=f"{total_registered:,}")

with col3:
    total_rental = ren_monthly_df["count"].sum()
    st.metric("Total Rental", value=f"{total_rental:,}")


plt.figure(figsize=(10, 4))
plt.plot(ren_monthly_df.index, ren_monthly_df[["registered", "casual"]], marker="o")
plt.xlabel(None)
plt.ylabel(None)
plt.title("Total Rental Per Months")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend(["Registered", "Casual"])
plt.tight_layout()
st.pyplot(plt)

# Subheader 2
st.subheader("Performing Casual and Registered Consumer")
fig, axes = plt.subplots(1, 2, figsize=(35, 15))

datasets = [
    ("casual", ren_cas_df, "Performing Casual Rental by Day"),
    ("registered", ren_reg_df, "Performing Registered Rental by Day"),
]

for i, (column, data, title) in enumerate(datasets):
    ax = axes[i]
    sns.barplot(
        x=column, y="weekday", data=data, palette=sns.color_palette("Spectral"), ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel("Count", fontsize=30)
    ax.set_title(title, loc="center", fontsize=50)
    ax.tick_params(axis="y", labelsize=25)
    ax.tick_params(axis="x", labelsize=20)

axes[1].invert_xaxis()
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
st.pyplot(fig)


# Subheader 3
st.subheader("Total Rental by Conditions")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 4))

    sns.pointplot(
        data=hour_df[["hour", "count", "weather_situation"]],
        x="hour",
        y="count",
        hue="weather_situation",
        palette=sns.color_palette("Spectral"),
        ax=ax,
    )
    plt.xlabel(None)
    plt.ylabel(None)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.title("Total Rental Per Hour By Weather Situation")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(35, 15))

    sns.barplot(
        y="count",
        x="weather_situation",
        data=byweather_df,
        palette=sns.color_palette("Spectral"),
        ax=ax,
    )
    ax.set_title("Total Rental by Weather Situation", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)


# Subheader 4
st.subheader("RFM Analysis")
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "IDR", locale="id_ID")
    st.metric("Average Monetary", value=avg_frequency)
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

plot_rfm(rfm_df, "recency", "By Recency (days)", ax[0])
plot_rfm(rfm_df, "frequency", "By Frequency", ax[1])
plot_rfm(rfm_df, "monetary", "By Monetary", ax[2])

st.pyplot(fig)

copyright = f"Copyright © 2023 Only For Education. All Rights Reserved."
st.caption(copyright)
