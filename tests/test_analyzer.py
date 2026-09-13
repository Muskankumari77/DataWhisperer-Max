import pandas as pd
from services.analyzer import execute_analysis_code

def test_basic_analysis():
    df = pd.DataFrame({'city':['Delhi','Delhi','Pune'], 'sales':[10,20,5]})
    out = execute_analysis_code("result = df.groupby('city')['sales'].sum().to_dict()", df)
    assert out['error'] is None
    assert out['result']['Delhi'] == 30

def test_blocks_import():
    df = pd.DataFrame({'x':[1]})
    out = execute_analysis_code("import os\nresult = 1", df)
    assert out['error'] is not None
