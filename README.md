# Beet Summarize


[![Tests](https://travis-ci.org/steven-murray/beet-summarize.svg?branch=master)](https://travis-ci.org/steven-murray/beet-summarize.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/steven-murray/beet-summarize/badge.svg?branch=master)](https://coveralls.io/github/steven-murray/beet-summarize?branch=master)

**Summarize your beets library**

```
$ beet summarize

genre                  | count
---------------------- | -----
Rock                   | 340  
Classical              | 268  
Folk                   | 248  
Pop                    | 248  
```

``beet-summarize`` is a plugin for the ``beets`` music organisation library,
that provides the ability to summarize statistics according to fields.

## Installation

```
$ pip install git+https://github.com/steven-murray/beet-summarize.git
```


Then add ``summarize`` to your list of ``plugins`` in your beets' ``config.yml``.

## Usage

``beet-summarize`` adds the single sub-command ``summarize``. The interface is
very simple:

```
Options:
  -g GROUP_BY, --group-by=GROUP_BY
                        field to group by
  -s STATS, --stats=STATS
                        stats to display
  -R, --not-reverse     whether to not reverse the sort
```

In a bit more detail, ``-g`` will tell ``summarize`` which beets field it will
summarize over. The default is ``genre``. We could also have grouped by year,
and used the ``-R`` flag to reverse the results:

```
$ beet summarize -g year -R

year | count
---- | -----
1981 | 1    
1991 | 4    
1985 | 9    
1982 | 10   
1990 | 11   
```

Perhaps most importantly, you can specify aggregate statistics to report via 
``-s`` or ``--stats``. Each statistic is a valid field with optional pre-pending 
modifiers. Modifiers include an aggregation function (options are ``MIN``, 
``MAX``, ``SUM``, ``COUNT``, ``AVG``, ``RANGE``), whether to only include 
``UNIQUE`` entries, and converters for when the field is of str type 
(options are ``LEN`` and ``WORDS``). The default statistic is ``count``. 
You can give multiple statistics by enclosing them in quotes. The order of the results will 
be based on the first given statistic. The format for each statistic is 
``aggregator<:modifier>|field``, except for ``count`` which is special
and does not require a field.

As an example:

```
$ beet summarize -g year -s "count avg|bitrate avg:words|lyrics count:unique|artist"

year | count | avg|bitrate       | avg:words|lyrics   | count:unique|artist
---- | ----- | ----------------- | ------------------ | -------------------
2006 | 317   | 648899.5741324921 | 273.51419558359623 | 41                            
2009 | 244   | 709426.0778688524 | 660.7786885245902  | 17                 
2005 | 241   | 754819.5145228215 | 681.6099585062241  | 24                 
2010 | 203   | 747686.5615763547 | 537.1133004926108  | 51    
```

Here the first statistic is just the number of tracks in the library for each 
given year (and this sorts the table). The second column is the average 
bitrate of tracks per year. The third column is the average number of words
in the lyrics of each track per year. The final column is the number of unique
artists on tracks per year.

### String conversions

For string-valued fields (eg. artist, lyrics), if the statistic is not ``count``,
some way to convert the field string to a numerical value is required. A number
of ways could be thought of, but currently ``summarize`` only supports the
number of words or number of characters, specified by the modifiers ``words``
and ``len`` respectively. The latter is default. ``words`` are defined by 
characters separated by spaces.

### ``unique`` modifier

The ``unique`` modifier is always applied directly on the field. This is usually
what is wanted: eg. ``count:unique|artist`` produces the number of *different*
artists. However, it can be a little confusing in scenarios such as 
``sum:unique:words|lyrics``. This does *not* count the total number of unique
words in all the lyrics for tracks in the given category. Instead, it applies
the ``unique`` modifier to the field as a whole. So, it is the sum of the total
number of words for each track that has unique lyrics. 

## Ideas for improvement

- More string conversions (and perhaps even the ability to not convert from
  string to number for some aggregators, eg. range could be defined directly
  on a string by ordering lexically).
- Ability to specify ``unique`` in such a way that it is applied on elements
  of the field rather than the entire field, so that eg. getting the total number
  of unique words in all lyrics for a given year is possible.
- Multi-level categories, i.e. being able to categorize by genre, then by year
  within the genre, and provide statistics at each level.
- Ability to pass an ``-a`` flag to do stats at the album-level. 



