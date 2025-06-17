import pandas as pd
import altair as alt

def make_delays_heatmap(df:pd.DataFrame) -> alt.Chart:
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
    ).properties(
        width=200,
        height=400
    )
    return heatmap