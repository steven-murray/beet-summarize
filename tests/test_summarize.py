"""Tests for summarize plugin."""

import sys

import pytest

from beetsplug import summarize as sm


class MockItem:
    """Mock item for testing summarize plugin."""

    def __init__(
        self,
        title: str,
        year: int,
        artist: str,
        album: str,
        bitrate: int,
        lyrics: str,
        genres=None,
    ):
        self.title = title
        self.year = year
        self.artist = artist
        self.album = album
        self.bitrate = bitrate
        self.lyrics = lyrics
        self.genres = genres if genres is not None else []


class MockLibrary:
    """Mock library for testing summarize plugin."""

    def __init__(self):
        self._items = []

    def add(self, item: MockItem):
        """Add an item to the library."""
        self._items.append(item)

    def items(self, query):
        """Return all items in the library."""
        return self._items  # ignore query for now


@pytest.fixture(scope="module")
def lib():
    """Library with some mock items for testing."""
    lib = MockLibrary()
    lib.add(MockItem("song1", 2000, "artist1", "album1", 128, "lyrics1"))
    lib.add(MockItem("song2", 2001, "artist2", "album2", 256, "lyrics2"))
    lib.add(MockItem("song3", 2002, "artist3", "album3", 512, "lyrics3"))
    lib.add(
        MockItem(
            "song4",
            2003,
            "artist3; artist4",
            "album4",
            700,
            "so many lyrics in this song",
        )
    )

    return lib


def test_parse_stat():
    """Test the parse_stat function."""
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


def test_show_summary(lib):
    """Test the show_summary function with various stats and categories."""
    stats = "count avg|bitrate unique:words|lyrics range:unique:words|artist"
    txt = sm.show_summary(lib, "query", category="year", stats=stats, reverse=False)

    assert "2000 |" in txt
    assert "2001 |" in txt
    assert "2002 |" in txt


def test_show_summary_artist(lib):
    """Test grouping by artist, including multi-field artists separated by ';'."""
    stats = "count"
    txt = sm.show_summary(lib, "query", category="artist", stats=stats, reverse=False)

    assert "artist1 | 1" in txt
    assert "artist2 | 1" in txt
    assert "artist3 | 2" in txt  # in the multi-field
    assert "artist4 | 1" in txt  # in the multi-field


@pytest.fixture(scope="module")
def lib_with_genres():
    """Library with genres stored as lists (beets >= 2.7.0 style)."""
    lib = MockLibrary()
    lib.add(
        MockItem("song1", 2000, "artist1", "album1", 128, "lyrics1", ["Rock", "Pop"])
    )
    lib.add(MockItem("song2", 2001, "artist2", "album2", 256, "lyrics2", ["Jazz"]))
    lib.add(
        MockItem("song3", 2002, "artist3", "album3", 512, "lyrics3", ["Rock", "Jazz"])
    )
    lib.add(MockItem("song4", 2003, "artist4", "album4", 700, "lyrics4", []))
    return lib


def test_show_summary_genres_as_list(lib_with_genres):
    """Test grouping by genres when stored as a list (beets >= 2.7.0)."""
    stats = "count"
    txt = sm.show_summary(
        lib_with_genres, "query", category="genres", stats=stats, reverse=False
    )

    assert "Rock   | 2" in txt
    assert "Jazz   | 2" in txt
    assert "Pop    | 1" in txt
    # Items with empty genres list should not appear as a category
    assert "song4" not in txt
