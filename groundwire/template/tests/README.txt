For more information on unit tests, see http://plone.org/documentation/tutorial/best-practices/unit-testing

There is some info in groundwire.template/docs/customizations-this-product-does.txt
that explains a little about docstrings.

To run the tests in this directory, add a test section to your buildout:

[buildout]
parts +=
    test

[test]
recipe = zc.recipe.testrunner
eggs = ${instance:eggs}

Then, after re-running buildout, run the tests:

bin/test -s groundwire.template