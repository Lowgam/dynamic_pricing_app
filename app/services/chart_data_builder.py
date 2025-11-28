# Module chart_data_builder.py
# Purpose : build data for dashboard

from datetime import date, timedelta
from typing import Dict, List

# ---------------------------------------------------
# Fx: Generate sales series for testing purposes
# ---------------------------------------------------
def generate_mock_sales_series(days: int = 14) -> Dict[str, List]:
    """
    parameter:
    days(int) days to be shown

    return:
    dict:
    - labels:
    - values:
    """

    labels = []
    values = []

    for i in range(days):
        day = date.today() - timedelta(days = (days - i))
        labels.append(day.strftime("%d-%m"))
        # Hypothetical sales values, for testings sakes
        values.append((i * 3) % 15 + 5)

    return {
        "labels": labels,
        "values": values,
    }

# ---------------------------------------------------
# Fx: Build data for chart
# ---------------------------------------------------
def build_chart_data(product_id: int) -> Dict:
    """
    parameter:
    product_io int

    return:
    dict structure for chart
    """
    mock_series = generate_mock_sales_series()

    return {
        "product_id": product_id,
        "labels": mock_series["labels"],
        "values": mock_series["values"],
    }