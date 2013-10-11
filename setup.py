from setuptools import setup, find_packages

version = '1.0.1'

setup(name='groundwire.template',
      version=version,
      description="Base template for Groundwire sites.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Groundwire',
      author_email='info@groundwire.org',
      url='http://groundwire.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['groundwire'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.googleanalytics',
          'collective.recaptcha',
          'plone.app.caching',
          'Products.PloneFormGen',
          'setuptools',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
