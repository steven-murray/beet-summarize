"""Summarize library statistics."""

from __future__ import annotations

from collections import OrderedDict

from beets.plugins import BeetsPlugin
from beets.ui import Subcommand, decargs

summarize_command = Subcommand("summarize", help="summarize library statistics")

summarize_command.parser.add_option(
    "-g", "--group-by", type="string", help="field to group by", default="genre"
)

summarize_command.parser.add_option(
    "-s", "--stats", type="string", help="stats to display", default="count"
)

summarize_command.parser.add_option(
    "-R", "--not-reverse", action="store_true", help="whether to not reverse the sort"
)


def parse_stat(stat):
    """Parse a cmdline stat string.

    Parameters
    ----------
    stat
        string specifying the statistic to obtain. Format is
        "aggregator<:modifier>|field". Available aggregators are {min, max, count, sum,
        avg, range}. Available modifiers are {unique, len, words}, where the final two
        are only available for string fields. Available `fields` are any beets field.

    Returns
    -------
    dict
        The statistics. Keys are 'field' (str field), 'aggregator' (str aggregator),
        'str_converter' (either 'len' or 'words' or None), and 'unique' (bool).
    """
    aggregators = ["min", "max", "count", "sum", "avg", "range"]
    str_converters = ["len", "words"]

    this = {}

    # Special case: count
    if stat.lower() == "count":
        this["field"] = "title"  # irrelevant
        this["aggregator"] = "count"
        this["str_converter"] = None
        this["unique"] = False
        return this

    # Get the field name of the statistic
    this["field"] = stat.split("|")[-1].lower()

    # There doesn't *need* to be any modifiers.
    modifiers = stat.split("|")[0].lower().split(":") if "|" in stat else []

    # Determine the aggregator for this statistic
    aggregator = None
    for agg in aggregators:
        if agg in modifiers:
            if aggregator is None:
                this["aggregator"] = aggregator = agg
            else:
                raise ValueError(f"You have specified more than one aggregator: {stat}")

    if "aggregator" not in this:
        this["aggregator"] = "sum"

    # Get str converter
    this["str_converter"] = [m for m in modifiers if m in str_converters]
    if len(this["str_converter"]) > 1:
        raise ValueError(f"You have specified more than one str conversion: {stat}")
    if "str_converter" in this and this["str_converter"]:
        this["str_converter"] = this["str_converter"][0]
    else:
        this["str_converter"] = None

    # Get specific modifiers
    this["unique"] = "unique" in modifiers

    return this


def parse_stats(stats: str) -> dict[str, dict]:
    """Parse a cmdline stats string.

    Parameters
    ----------
    stats
        string with stats separated by spaces. For format of stats, see
        :func:`parse_stat`.

    Returns
    -------
    OrderedDict
        keys are each full stat string in `stats`. Values are
        dictionaries from `parse_stat` for each stat.
    str
        the first stat.
    """
    stats = stats.split(" ")
    return OrderedDict([(stat, parse_stat(stat)) for stat in stats])


def set_str_converter(stat, stat_type):
    """Set str_converter field for a stat dict.

    Only applies if the field type is str and the converter does not yet exist.
    """
    # For strings arguments, require a way to turn
    # the string into a numerical value. By default,
    # use the length of the string.
    if stat_type is str and not stat["str_converter"]:
        stat["str_converter"] = "len"


def group_by(category: str, items):
    """Group a list of items by a category.

    If the category is one that supports multiple values, split them by ";" and add
    the item to each of the groups.
    """
    multifield_categories = ["albumartist", "artist", "genre"]

    out = {}
    for item in items:
        cat = getattr(item, category)
        if category in multifield_categories:
            cats = [c.strip() for c in cat.split(";")]
        else:
            cats = [cat]

        for cat in cats:

            if cat not in out:
                out[cat] = []

            out[cat].append(item)

    return out


def get_items_stat(items, stat):
    """Get a statistic for a list of items."""
    collection = set() if stat["unique"] else []

    # Collect all the stats
    for item in items:
        val = getattr(item, stat["field"])

        if stat["unique"]:
            collection.add(val)
        else:
            collection.append(val)

    stat_type = type(getattr(items[0], stat["field"]))

    # We can turn the collection into a list now
    collection = list(collection)

    # Convert str stats
    if stat_type is str and stat["aggregator"] != "count":
        if stat["str_converter"] == "len":
            collection = [len(c) for c in collection]
        elif stat["str_converter"] == "words":
            collection = [len(c.split(" ")) for c in collection]

    # Aggregate
    if stat["aggregator"] == "min":
        return min(collection)
    elif stat["aggregator"] == "max":
        return max(collection)
    elif stat["aggregator"] == "count":
        return len(collection)
    elif stat["aggregator"] == "range":
        return max(collection) - min(collection)
    elif stat["aggregator"] == "sum":
        return sum(collection)
    elif stat["aggregator"] == "avg":
        return sum(collection) / len(collection)


def print_dct_as_table(keys, dcts, cat_name=None, col_formats=None) -> str:
    """Pretty print a list of dictionaries as a dynamically sized table.

    If column names aren't specified, they will show in random order.
    """
    columns = list(dcts[0].keys())

    table = [[cat_name] + columns] if cat_name else [[""] + columns]

    for key, item in zip(keys, dcts):
        content = [
            "{val:{fmt}}".format(
                val=item[col], fmt=col_formats[col] if col_formats else ""
            )
            for col in columns
        ]
        table.append([str(key)] + content)

    col_size = [max(map(len, col)) for col in zip(*table)]

    fmt_str = " | ".join([f"{{:<{i}}}" for i in col_size])
    table.insert(1, ["-" * i for i in col_size])  # Seperating line
    txt = "\n".join([fmt_str.format(*row) for row in table])

    print(txt)
    return txt


def print_results(res, cat_name, sort_stat, reverse):
    """Print the results of a summary."""
    keys = sorted(res.keys(), key=lambda x: res[x][sort_stat], reverse=reverse)
    dcts = [res[key] for key in keys]

    return print_dct_as_table(keys, dcts, cat_name)


def show_summary(lib, query, category, stats, reverse):
    """Show a summary of the statistics."""
    # TODO: albums?

    items = lib.items(query)
    stats = parse_stats(stats)
    sort_stat = list(stats.keys())[0]

    for stat in stats.values():
        set_str_converter(stat, type(getattr(items[0], stat["field"])))

    groups = group_by(category, items)

    stat_dct = {
        g: {nm: get_items_stat(items, stat) for nm, stat in stats.items()}
        for g, items in groups.items()
    }
    return print_results(stat_dct, category, sort_stat, reverse)


def summarize(lib, opts, args):
    """Summarize the library by a given field."""
    show_summary(lib, decargs(args), opts.group_by, opts.stats, not opts.not_reverse)


summarize_command.func = summarize


class SuperPlug(BeetsPlugin):
    """Subclass of the BeetsPlugin to create the command."""

    def commands(self):
        """Add the summarize command."""
        return [summarize_command]
