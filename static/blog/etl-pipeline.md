# Building an ETL Pipeline with Python and BigQuery

ETL is the heart of modern data engineering. Here's how I built a sales data pipeline using Pandas and BigQuery.

## Steps

1. Extract CSV from cloud storage
2. Transform using Pandas
3. Load into BigQuery

## Code Example

```python
import pandas as pd
from google.cloud import bigquery

df = pd.read_csv('sales.csv')
df['total'] = df['qty'] * df['price']

client = bigquery.Client()
client.load_table_from_dataframe(df, 'project.dataset.table')
```

## Notes

- Validate your schema before loading.
- Automate with Airflow or Cloud Functions.
