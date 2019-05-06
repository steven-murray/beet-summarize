from beets.plugins import BeetsPlugin
from beets.ui import Subcommand, decargs

summarize_command = Subcommand('summarize', help='summarize library statistics')

summarize_command.parser.add_option(
    u'-g', u'--group-by', type='string',
    help=u'field to group by', default='genre'
)

summarize_command.parser.add_option(
    u'-s', u'--stats', type='string',
    help=u'stats to display', default='count',
)

summarize_command.parser.add_option(
    u'-R', u'--not-reverse', action='store_true',
    help='whether to not reverse the sort'
)


def parse_stats(stats):
    """Parse a cmdline stats string"""
    stats = stats.split(" ")

    aggregators = ['min', 'max', 'count', 'sum', 'avg', 'range']
    str_converters = ['len', 'words']

    out_dct = {}
    for stat in stats:
        this = out_dct[stat] = {}

        # Special case: count
        if stat.lower() == 'count':
            this['field'] = 'title'  # irrelevant
            this['aggregator'] = 'count'
            this['str_converter'] = None
            this['unique'] = False
            continue

        # Get the field name of the statistic
        this['field'] = stat.split("|")[-1].lower()

        # There doesn't *need* to be any modifiers.
        modifiers = stat.split("|")[0].lower() if "|" in stat else []

        # Determine the aggregator for this statistic
        aggregator = None
        for agg in aggregators:
            if agg in modifiers:
                if aggregator is None:
                    this['aggregator'] = aggregator = agg
                else:
                    raise ValueError("You have specified more than one aggregator: {}".format(stat))

        # Get str converter
        this['str_converter'] = [m for m in modifiers if m in str_converters]
        if len(this['str_converter']) > 1:
            raise ValueError("You have specified more than one str conversion: {}".format(stat))
        else:
            this['str_converter'] = this['str_converter'][0] if this['str_converter'] else None

        # Get specific modifiers
        this['unique'] = "unique" in modifiers

    return out_dct, stats[0]


def validate_stat(stat, stat_type):
    """Validate a stat dict (from parse_stats), and update it according to the type
    of the statistic"""

    # Make the default aggregator 'sum'
    if "aggregator" not in stat:
        stat['aggregator'] = 'sum'

    # For strings arguments, require a way to turn
    # the string into a numerical value. By default,
    # use the length of the string.
    if stat_type is str and not stat['str_converter']:
        stat['str_converter'] = 'len'


def group_by(category, items):
    out = {}
    for item in items:
        cat = getattr(item, category)

        if cat not in out:
            out[cat] = []

        out[cat].append(item)

    return out


def get_items_stat(items, stat):
    if stat['unique']:
        collection = set()
    else:
        collection = []

    # Collect all the stats
    for item in items:
        val = getattr(item, stat['field'])

        if stat['unique']:
            collection.add(val)
        else:
            collection.append(val)

    stat_type = type(getattr(items[0], stat['field']))

    # We can turn the collection into a list now
    collection = list(collection)

    # Convert str stats
    if stat_type is str and stat['aggregator'] != "count":
        if stat['str_converter'] == "len":
            collection = [len(c) for c in collection]
        elif stat['str_converter'] == 'words':
            collection = [len(c.split(" ")) for c in collection]

    # Aggregate
    if stat['aggregator'] == 'min':
        return min(collection)
    elif stat['aggregator'] == 'max':
        return max(collection)
    elif stat['aggregator'] == 'count':
        return len(collection)
    elif stat['aggregator'] == 'range':
        return max(collection) - min(collection)
    elif stat['aggregator'] == 'sum':
        return sum(collection)
    elif stat['aggregator'] == 'avg':
        return sum(collection) / len(collection)


def print_dct_as_table(keys, dcts, cat_name=None, col_formats=None):
    """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
    If column names (colList) aren't specified, they will show in random order.

    """
    columns = list(dcts[0].keys())

    if cat_name:
        table = [[cat_name] + columns]  # 1st row = header
    else:
        table = [[""] + columns]

    for key, item in zip(keys, dcts):
        table.append(["{}".format(key)] +
                     ["{val:{fmt}}".format(
                         val=item[col],
                         fmt=col_formats[col] if col_formats else "")
                         for col in columns])

    col_size = [max(map(len, col)) for col in zip(*table)]

    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in col_size])
    table.insert(1, ['-' * i for i in col_size])  # Seperating line
    for item in table: print(formatStr.format(*item))


def print_results(res, cat_name, sort_stat, reverse):
    keys = sorted(res.keys(), key=lambda x: res[x][sort_stat], reverse=reverse)
    dcts = [res[key] for key in keys]

    print_dct_as_table(keys, dcts, cat_name)


def show_summary(lib, query, category, stats, reverse):
    """
    # TODO: albums?
    """
    items = lib.items(query)
    stats, sort_stat = parse_stats(stats)

    for stat in stats.values():
        validate_stat(stat, type(getattr(items[0], stat['field'])))

    groups = group_by(category, items)

    stat_dct = {}
    for g, items in groups.items():
        stat_dct[g] = {}

        for nm, stat in stats.items():
            stat_dct[g][nm] = get_items_stat(items, stat)

    print_results(stat_dct, category, sort_stat, reverse)


def summarize(lib, opts, args):
    show_summary(lib, decargs(args), opts.group_by, opts.stats, not opts.not_reverse)


summarize_command.func = summarize


class SuperPlug(BeetsPlugin):
    def commands(self):
        return [summarize_command]
