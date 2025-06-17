"""Modules/Functions required to push information to station topics."""
from pandas import DataFrame


def get_delayed_trains(api_train_data: DataFrame) -> DataFrame:
    """Returns a dataframe that contains only delayed trains."""

    api_train_data = api_train_data.dropna(
        subset=["scheduled_dep_time", "actual_dep_time"])

    delayed_trains_mask = (
        api_train_data["actual_dep_time"] >
        api_train_data["scheduled_dep_time"]
    )

    delayed = api_train_data[delayed_trains_mask]

    print(delayed[["scheduled_dep_time", "actual_dep_time"]])

    return api_train_data[delayed_trains_mask]


if __name__ == "__main__":
    pass
