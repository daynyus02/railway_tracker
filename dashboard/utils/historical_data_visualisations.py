"""Contains functions which produce the visualisations for the historical data page."""
import pandas as pd
import altair as alt

def make_delays_heatmap(df:pd.DataFrame) -> alt.Chart:
    """Produces a heatmap showing average delay time per hour."""
    delay_heatmap = df[["delay_time", "scheduled_dep_time", "operator_name"]].copy()
    delay_heatmap["hour"] = delay_heatmap["scheduled_dep_time"].dt.hour
    delay_heatmap = delay_heatmap.groupby(["hour", "operator_name"])["delay_time"].mean().reset_index()
    delay_heatmap = delay_heatmap.rename(columns={"delay_time": "avg_delay"})
    delay_heatmap["avg_delay"] = delay_heatmap["avg_delay"].round(decimals=1)

    heatmap = alt.Chart(delay_heatmap).mark_rect().encode(
        x=alt.X('hour:O', title="Hour in the day"),
        y=alt.Y('operator_name:N', title="Operator"),
        color=alt.Color('avg_delay:Q', title="Average Delay (min)",
                    scale=alt.Scale(domain=[0, delay_heatmap["avg_delay"].max()],
                                    range=["#f2f1ec", "#df543b"])
        )
    )
    return heatmap

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

def make_cancellations_per_station_bar(df: pd.DataFrame) -> alt.Chart:
    """Makes a pie chart showing cancellation counts per station compared to the mean."""
    station_cancellation_bar = alt.Chart(df).mark_bar(size=30, color="#d5caca").encode(
        y=alt.Y('station_name', title="Station"),
        x=alt.X('delay_time', title="Avg. Delay time (min)"),
        tooltip=[alt.Tooltip('station_name', title="Station Name: "),
                alt.Tooltip('delay_time', title="Average Delay Time: ")]
    ).properties(height = 300)
    rule = alt.Chart(df).mark_rule(color='#df543b').encode(
    x=alt.X('mean(delay_time):Q'),
    tooltip=[alt.Tooltip('mean(delay_time):Q', title="Mean delay")]
    )
    return station_cancellation_bar + rule

if __name__ == '__main__':
    pass
