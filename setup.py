# pylint: disable=all

from setuptools import setup, find_packages

setup(
    name="agingbrains",
    version="0.0",
    packages=find_packages(exclude=['test', 'data', 'plots']),
    install_requires=[
        'google-cloud-dataflow',
        'nibabel',
        'scikit-learn',
        'scipy',
        'numpy',
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
    },
    # metadata for upload to PyPI
    author="Matteo Abis",
    author_email="",
    description="machine learning course, first problem",
    license="MIT",
    keywords="",
    # project home page, if any
    url="",
    entry_points="""
    """
    # could also include long_description, download_url, classifiers, etc.
)
