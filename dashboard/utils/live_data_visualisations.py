"""Visualisations for the live dashboard."""
import altair as alt
import pandas as pd

def highlight_operators(row) -> str:
    """Returns colour configuration for the service operators."""
    operator = row.get("Operator")
    operator_colours = {"Elizabeth line": 'background-color: #6950a1',
                       "CrossCountry": 'background-color: #CA123F',
                       "Great Western Railway": 'background-color: #0A493E'
                       }
    if operator in operator_colours:
        return operator_colours[operator]
    return ''

def highlight_interruption(row) -> list[str]:
    """Returns colour configuration based on interruption type."""
    colours = [''] * len(row)
    if row.get('Status') == "Cancelled":
        colours = ['background-color: #3e0100'] * len(row)
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    elif row.get("Status") == "Delayed":
        colours[row.index.get_loc("Status")] = 'background-color: #FF6961'
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    else:
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    return colours

def make_live_train_table(df: pd.DataFrame, cancelled: bool):
    live_trains = df[[
        "service_uid",
        "station_name",
        "destination_name",
        "actual_arr_time",
        "actual_dep_time",
        "Status",
        "cancel_reason",
        "platform",
        "operator_name"
    ]].copy()

    live_trains.rename(columns={
        "service_uid": "Service ID",
        "station_name": "Arrival Station",
        "destination_name": "Destination",
        "platform": "Platform",
        "operator_name": "Operator",
        "cancel_reason": "Reason"
    }, inplace=True)
    if cancelled:
        live_trains["Reason"] = live_trains["Reason"].apply(lambda x: x.capitalize())
    if not cancelled:
        live_trains = live_trains.drop(columns=["Reason"])
    live_trains['Arrival Time'] = live_trains['actual_arr_time'].dt.time
    live_trains['Departure Time'] = live_trains['actual_dep_time'].dt.time
    live_trains = live_trains.drop(columns=["actual_dep_time", "actual_arr_time"])

    live_trains = live_trains.fillna('-')
    live_trains = live_trains.sort_values(by='Departure Time')
    styled_trains = live_trains.style.apply(highlight_interruption, axis=1)
    return styled_trains

def make_operator_cancellations_pie(df: pd.DataFrame) -> pd.DataFrame:
    operator_colour_scale = alt.Scale(range=['#0A493E','#6950a1', '#CA123F'])
    cancellations_pie = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta("Count:Q"),
        color=alt.Color("Operator:N", scale=operator_colour_scale),
        tooltip=[alt.Tooltip("Operator"), alt.Tooltip("Count", title="Count")]
    )
    return cancellations_pie

def make_interruptions_bar(df: pd.DataFrame) -> alt.Chart:
    interruption_colour_scale = alt.Scale(domain=['Cancelled','Delayed', 'On Time'], 
                                        range=['#f2f1ec', '#df543b', '#808080'])
    interruptions_chart = alt.Chart(df).mark_bar(size=30).encode(
        x=alt.X('Status:N', axis=None),
        y=alt.Y('percentage_of_trains:Q', title="% of trains"),
        color=alt.Color('Status:N',scale=interruption_colour_scale),
        column=alt.Column('operator_name:N', title='Operator'),
        tooltip=[alt.Tooltip('operator_name', title="Operator Name"),
                alt.Tooltip('Status'),
                alt.Tooltip('percentage_of_trains', title="% of trains")]
    ).properties(width=100)
    return interruptions_chart

