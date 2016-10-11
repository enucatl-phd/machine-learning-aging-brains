# pylint: disable=all

from setuptools import setup, find_packages

setup(
    name="machine-learning-aging-brains",
    version="0.0",
    packages=find_packages(exclude=['test', 'data', 'plots']),
    install_requires=[
        'nibabel',
        'click',
        'numpy',
        'scipy',
        'tensorflow',
        'scikit-learn',
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
    },
    # metadata for upload to PyPI
    author="Matteo Abis",
    author_email="",
    description="machine learning course, first problem",
    license="MIT License",
    keywords="",
    # project home page, if any
    url="",
    entry_points="""
    """
    # could also include long_description, download_url, classifiers, etc.
)
