.. highlight:: shell

Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/dstrigl/htheatpump/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

``htheatpump`` could always use more documentation, whether as part of the
official ``htheatpump`` docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/dstrigl/htheatpump/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up ``htheatpump`` for local development.

1. Fork the ``htheatpump`` repository on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/htheatpump.git

3. Install your local copy into a virtualenv [1]_. Assuming you have ``virtualenvwrapper`` installed,
   this is how you set up your fork for local development under Python 3.7::

    $ mkvirtualenv hthp-py37 -p python3.7
    $ cd htheatpump/
    $ python setup.py develop

4. Install all project dependencies for local development (and testing)::

    $ pip install -r requirements/develop.pip
    $ pip install -r requirements/test.pip

5. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

6. When you're done making changes, check that your changes pass ``flake8`` and the *tests*
   (using ``pytest``), including testing other Python versions with ``tox``::

    $ flake8 htheatpump tests samples setup.py
    $ pytest
    $ tox

   There are also a few tests which only run if a heat pump is connected. These can be executed
   by passing the argument ``--connected`` to the test commands::

    $ pytest --connected
    $ tox -- --connected

   To change the default device (``/dev/ttyUSB0``) and baudrate (115200) use the arguments
   ``--device`` and ``--baudrate``::

    $ pytest --connected --device /dev/ttyUSB1 --baudrate 9600
    $ tox -- --connected --device /dev/ttyUSB1 --baudrate 9600

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "A description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

.. [1] If you need more information about Python virtual environments take a look at this
       `article on RealPython <https://realpython.com/blog/python/python-virtual-environments-a-primer/>`_.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.7 and 3.8. Check
   https://travis-ci.org/dstrigl/htheatpump/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

    $ pytest tests/test_htparams.py
