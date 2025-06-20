"""Contains functions which produce the visualisations for the historical data page."""
import pandas as pd
import altair as alt

def make_delay_heatmap(df: pd.DataFrame, station: str) -> alt.Chart:
    """Produces a heatmap showing average delay time per hour."""
    delay_heatmap = df[["delay_time", "scheduled_dep_time", "station_name"]].copy()
    delay_heatmap["hour"] = delay_heatmap["scheduled_dep_time"].dt.hour

    all_avg = delay_heatmap.groupby(["hour", "station_name"])["delay_time"].mean().reset_index()
    all_avg["avg_delay"] = all_avg["delay_time"].round(1)
    max_delay = all_avg["avg_delay"].max()
    # delay_heatmap = delay_heatmap[delay_heatmap["delay_time"] > 0]
    # max_delay = delay_heatmap["delay_time"].max()
    if station != "All":
        delay_heatmap = delay_heatmap[delay_heatmap["station_name"] == station]
        delay_heatmap = delay_heatmap.groupby("hour")["delay_time"].mean().reset_index()
        delay_heatmap["station_label"] = station

    else:
        delay_heatmap = delay_heatmap.groupby("hour")["delay_time"].mean().reset_index()
        delay_heatmap["station_label"] = "All Stations"

    delay_heatmap = delay_heatmap.rename(columns={"delay_time": "avg_delay"})
    delay_heatmap["avg_delay"] = delay_heatmap["avg_delay"].round(1)

    heatmap = alt.Chart(delay_heatmap).mark_rect().encode(
        x=alt.X('hour:O', title="Hour in the day"),
        y=alt.Y("station_label:N", title=None),
        color=alt.Color('avg_delay:Q', title="Minutes Delayed",
                        scale=alt.Scale(domain=[0, max_delay],
                                        range=["#f2f1ec", "#df543b"]))
    )
    return heatmap

def make_delays_area_chart(df:pd.DataFrame) -> alt.Chart:
    """Produces a heatmap showing average delay time per hour."""
    delay_area = df[["scheduled_dep_time", "Status"]].copy()
    delay_area["hour"] = delay_area["scheduled_dep_time"].dt.hour
    delay_area = delay_area.groupby(["hour", "Status"]).count().reset_index()

    area_chart_colours = alt.Scale(domain=df["Status"].tolist(), range=["#df543b", "#3d3d3d", "#d5caca"])
    delays_area = alt.Chart(delay_area).mark_area().encode(
        x=alt.X('hour:O', title="Hour in the day"),
        y=alt.Y('scheduled_dep_time', title="Count"),
        color=alt.Color("Status", scale=area_chart_colours)
        )
    return delays_area

def make_stations_cancellations_pie(df: pd.DataFrame) -> alt.Chart:
    """Produces a pie chart showing cancellation counts per station."""
    station_colour_scale = alt.Scale(domain=df["Station"].to_list(),
                                    range=["#df543b",
                                        "#a3321d",
                                        "#f26842",
                                        "#ff7f50",
                                        "#ff9966",
                                        "#ffb380",
                                        "#ffd1b3",
                                        "#f7a072",
                                        "#d96e30",
                                        "#ff6633",
                                        "#cc4400",
                                        "#ff8552",
                                        "#e67300",  
                                        "#fce5d5",   
                                        "#732619"
                                    ])

    cancellations_pie = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta("Count:Q"),
        color=alt.Color("Station:N", scale=station_colour_scale),
        tooltip=[alt.Tooltip("Station"), alt.Tooltip("Count", title="Count")]
    )
    return cancellations_pie

def make_delay_per_station_bar(df: pd.DataFrame) -> alt.Chart:
    """Makes a pie chart showing delay times per station compared to the mean."""
    delay_scale = alt.Scale(domain=df["station_name"].tolist(), range=["#df543b", "#3d3d3d", "#d5caca"])
    station_cancellation_bar = alt.Chart(df).mark_bar(size=30).encode(
        y=alt.Y('station_name', title="Station").sort("x"),
        x=alt.X('delay_time', title="Average delay time by minute."),
        tooltip=[alt.Tooltip('station_name', title="Station Name: "),
                alt.Tooltip('delay_time', title="Average Delay Time: ")],
        color=alt.Color("station_name", scale=delay_scale),
    ).properties(height = 300)
    rule = alt.Chart(df).mark_rule(color='#df543b').encode(
    x=alt.X('mean(delay_time):Q'),
    tooltip=[alt.Tooltip('mean(delay_time):Q', title="Mean delay")]
    )
    return station_cancellation_bar + rule

def make_cancellations_per_station_bar(df: pd.DataFrame) -> alt.Chart:
    """Makes a pie chart showing cancellation counts per station compared to the mean."""
    cancellations_scale = alt.Scale(domain=df["Station"].tolist(), range=["#df543b","#d5caca", "#3d3d3d"])
    station_cancellation_bar = alt.Chart(df).mark_bar(size=30).encode(
        y=alt.Y('Station').sort("x"),
        x=alt.X('Count', title="Number of cancelled trains."),
        tooltip=[alt.Tooltip('Station', title="Station Name: "),
                alt.Tooltip('Count', title="Number of cancelled trains:")],
        color=alt.Color("Station", scale=cancellations_scale)
    ).properties(height = 300)
    rule = alt.Chart(df).mark_rule(color='#df543b').encode(
    x=alt.X('mean(Count):Q'),
    tooltip=[alt.Tooltip('mean(Count):Q', title="Mean cancellation count: ")]
    )
    return station_cancellation_bar + rule

if __name__ == '__main__':
    pass
