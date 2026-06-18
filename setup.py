"""Setup configuration for Drive4Wind package"""
from setuptools import setup, find_packages

setup(
    name="Drive4Wind",
    version="0.1.0",
    packages=find_packages(include=["Drive4Wind*"]),
    include_package_data=True,
)
