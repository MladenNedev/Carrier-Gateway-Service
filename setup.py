from setuptools import find_packages, setup

setup(
    name="carrier_gateway_service",
    version="0.1.0",
    packages=find_packages(exclude=("tests",)),
)
