import pandas as pd

def get_unique_routes(data:pd.DataFrame):
    unique_routes = data[['origin_name', 'destination_name']].drop_duplicates()
    unique_routes_list = unique_routes.apply(
        lambda row: f"{row['origin_name']} to {row['destination_name']}", axis=1
    ).sort_values().tolist()
    return unique_routes_list