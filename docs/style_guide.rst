django-fixturless Programming Style Guide
===============================

The focus of this style guide is to keep consistency within the
django-fixtureless project. Most of the style guide will be inherited
from Python's style guide,
`PEP-8 <http://www.python.org/dev/peps/pep-0008/>`_, and
`Django's Coding Style <http://tinyurl.com/6753zmc>`_.

PEP-8
-----
This is a highlight of the important pieces of the PEP-8 document. You should
still read the whole document to familiarize yourself with all rules.
`PEP-8 <http://www.python.org/dev/peps/pep-0008/>`_

- Two good reasons to break a particular rule:
    - When applying the rule would make the code less readable, even for
      someone who is used to reading code that follows the rules.
- Use 4 spaces per indentation level. Not a tab character.
- Limit all lines to a maximum of 79 characters.
- Imports should usually be on separate lines.
- Avoid extraneous whitespace in the following situations:
    - Immediately inside parentheses, brackets or braces.
    - Immediately before a comma, semicolon, or colon.
    - Immediately before the open parenthesis that starts the argument list
      of a function call.
    - Immediately before the open parenthesis that starts an indexing or
      slicing.
- Use spaces around arithmetic, comparison and binary operators.
- Do not use spaces when around the assignment operator '=' when used to
  indicate a keyword argument or a default parameter value.
- Compound statements (multiple statements on the same line) are discouraged.

Git usage
---------
Master branch is always considered live. Never push to master, if it is
not ready for live at that moment.

Create your own remote branch from the dev branch all commits. Then create
a Pull Request on github to the respective branch on the ricomoss github repo.

Tests
-----------------------
Each class being tested should include tests for each condition in each method.

Module-level functions should be tested in these files, as well.

Try to keep these methods and functions as specific (within reason) to it's
purpose. If the functionality starts getting north of 10 lines of code, then
some refactoring may need to be in store. This will keep the tests simple to
write and maintain.

Should never push code to the master git branch where any of these required
tests are failing.

If a bug is found, you should first build a test to replicate the cause of
the bug. Then, write the code to pass that test, therefore fixing the bug.
