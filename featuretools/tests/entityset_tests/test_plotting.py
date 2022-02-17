import os
import re

import graphviz
import pandas as pd
import pytest
from dask import dataframe as dd

import featuretools as ft
from featuretools.utils.gen_utils import Library


@pytest.fixture
def pd_simple():
    es = ft.EntitySet("test")
    df = pd.DataFrame({"foo": [1]})
    es.add_dataframe(df, dataframe_name='test')
    return es


@pytest.fixture
def dd_simple():
    es = ft.EntitySet("test")
    df = pd.DataFrame({"foo": [1]})
    df = dd.from_pandas(df, npartitions=2)
    es.add_dataframe(df, dataframe_name='test')
    return es


@pytest.fixture
def ks_simple():
    ks = pytest.importorskip('databricks.koalas', reason="Koalas not installed, skipping")
    es = ft.EntitySet("test")
    df = ks.DataFrame({'foo': [1]})
    es.add_dataframe(df, dataframe_name='test')
    return es


@pytest.fixture(params=[
    pytest.param('pd_simple', marks=pytest.mark.pandas),
    pytest.param('dd_simple', marks=pytest.mark.dask),
    pytest.param('ks_simple', marks=pytest.mark.koalas)
])
def simple_es(request):
    return request.getfixturevalue(request.param)


def test_returns_digraph_object(es):
    graph = es.plot()

    assert isinstance(graph, graphviz.Digraph)


def test_saving_png_file(es, tmpdir):
    output_path = str(tmpdir.join("test1.png"))

    es.plot(to_file=output_path)

    assert os.path.isfile(output_path)
    os.remove(output_path)


def test_missing_file_extension(es):
    output_path = "test1"

    with pytest.raises(ValueError) as excinfo:
        es.plot(to_file=output_path)

    assert str(excinfo.value).startswith("Please use a file extension")


def test_invalid_format(es):
    output_path = "test1.xzy"

    with pytest.raises(ValueError) as excinfo:
        es.plot(to_file=output_path)

    assert str(excinfo.value).startswith("Unknown format")


def test_multiple_rows(es):
    plot_ = es.plot()
    result = re.findall(r"\((\d+\srows?)\)", plot_.source)
    expected = ["{} rows".format(str(i.shape[0])) for i in es.dataframes]
    if es.dataframe_type == Library.DASK.value:
        # Dask does not list number of rows in plot
        assert result == []
    else:
        assert result == expected


def test_single_row(simple_es):
    plot_ = simple_es.plot()
    result = re.findall(r"\((\d+\srows?)\)", plot_.source)
    expected = ["1 row"]
    if simple_es.dataframe_type == Library.DASK.value:
        # Dask does not list number of rows in plot
        assert result == []
    else:
        assert result == expected
