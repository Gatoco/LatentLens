# setup.py
from setuptools import setup, find_packages

setup(
    name="LatentLens",
    version="0.1.0",
    description="LatentLens movie recommendation system",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[],
)