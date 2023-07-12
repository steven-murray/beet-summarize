import sys

from beetsplug import summarize as sm


def test_parse_stat():
    print(sys.path)

    out = sm.parse_stat("count")

    assert out["aggregator"] == "count"
    assert out["str_converter"] is None
    assert not out["unique"]

    out = sm.parse_stat("avg|bitrate")
    assert out["aggregator"] == "avg"
    assert out["str_converter"] is None
    assert not out["unique"]
    assert out["field"] == "bitrate"

    out = sm.parse_stat("bitrate")
    assert out["aggregator"] == "sum"  # default aggregator
    assert out["str_converter"] is None
    assert not out["unique"]
    assert out["field"] == "bitrate"

    out = sm.parse_stat("unique:words|lyrics")
    assert out["aggregator"] == "sum"
    assert out["str_converter"] == "words"
    assert out["unique"]
    assert out["field"] == "lyrics"

    out = sm.parse_stat("range:unique:words|artist")
    assert out["aggregator"] == "range"
    assert out["str_converter"] == "words"
    assert out["unique"]
    assert out["field"] == "artist"
