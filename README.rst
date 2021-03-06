IATI Stats
==========

Requirements
------------

-  Git
-  Python 2.7
-  python-virtualenv
-  gcc
-  Development files for libxml and libxslt e.g. ``libxml2-dev``,
   ``libxslt-dev``

Getting started
---------------

.. code-block:: bash

    git clone git@github.com:Bjwebb/IATI-Data-Snapshot.git data

    virtualenv pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
    ./get_schemas.sh

    # Square brackets indicate optional argument
    python loop.py [--folder publisher-registry-id]
    python aggreagate.py
    python invert.py

    # Test it worked correctly
    python posttests.py

    # Do the above for every new commit in the data git repository
    # WARNING: This takes a long time (hours) and produces a lot of data (GBs)
    mkdir gitout
    ./git.sh

Commandline options
-------------------

Run ``python loop.py --help`` and ``python aggregate.py --help`` for a
summary of commandline options.

Structure of stats
------------------

Tests are located in a python module, by default ``stats.py`` (although
this can be changed with the ``--stats-module`` flag to loop.py and
aggregate.py). This module must contain the following classes:

-  PublisherStats
-  ActivityStats
-  ActivityFileStats
-  OrganisationStats
-  OrganisationFileStats

Each function within these clases is considered to be a stats function,
unless it begins with an underscore (``_``). In the appropriate context,
an object is created for each of these classes, and each of the stats
functions are called.

The functions will also be called with ``self.blank = True``, and should
return an empty version of their normal output, for aggregation
purposes. The ``returns_intdict`` and ``returns_int`` decorators are
provided for this purpose.

To calculate a new stat, add a function to the appropriate class in
``stats.py``.

Outputted JSON
~~~~~~~~~~~~~~

``loop.py`` produces json for each file, in the ``out`` directory. This
contains the stats calculated for each individual Activity and
Organisation, as well as by file.

``aggregated.py`` produces json aggregated at the publisher level, in
the ``aggregated`` directory. It also produces ``aggregated.json``,
which is the same, but for the entire dataset.

``invert.py`` produces ``inverted.json``, which has a list of publishers
for each stat.

License
-------

::

    Copyright (C) 2013-2014 Ben Webb <bjwebb67@googlemail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Included Data
-------------

(these are not released under the same license as the software)

-  ``exchange_rates.csv`` derived from `Exchange
   rates.xls <http://www.oecd.org/dac/stats/Exchange%20rates.xls>`__

