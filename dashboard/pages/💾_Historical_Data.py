"""Dashboard for historical data."""


### ROUGH HEATMAP NEEDS EDITING ###
delay_heatmap = delays[["delay_time", "scheduled_dep_time", "operator_name"]]
delay_heatmap["hour"] = delay_heatmap["scheduled_dep_time"].dt.hour
delay_heatmap = delay_heatmap.groupby(["hour", "operator_name"])["delay_time"].mean().reset_index()
delay_heatmap = delay_heatmap.rename(columns={"delay_time": "avg_delay"})

heatmap = alt.Chart(delay_heatmap).mark_rect().encode(
    x=alt.X('hour:Q', title="Hour in the day"),
    y=alt.Y('operator_name:N', title="Operator"),
    color=alt.Color('avg_delay:Q', title="Average Delay")
).properties(
    width=200,
    height=400
)