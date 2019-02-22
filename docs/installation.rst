.. highlight:: shell

Installation
============

For both installation methods described in the following sections the usage of Python virtual environments [1]_
is highly recommended.


Stable release
--------------

To install or upgrade :mod:`htheatpump`, run this command in your terminal:

.. code-block:: shell

    $ pip install htheatpump --upgrade

This is the preferred method to install :mod:`htheatpump`, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for :mod:`htheatpump` can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: shell

    $ git clone https://github.com/dstrigl/htheatpump.git

Or download the `tarball`_:

.. code-block:: shell

    $ curl -OL https://github.com/dstrigl/htheatpump/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: shell

    $ python setup.py install


.. _Github repo: https://github.com/dstrigl/htheatpump
.. _tarball: https://github.com/dstrigl/htheatpump/tarball/master


.. [1] If you need more information about Python virtual environments take a look at this
       `article on RealPython <https://realpython.com/blog/python/python-virtual-environments-a-primer/>`_.
