from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name="container_monitor",
    version="1.0.0",
    author="Paul Bargewell",
    author_email="paul.bargewell@opusvl.com",
    license="AGPL-3.0-or-later",
    description="Monitor Docker containers and report to Icinga2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpusVL/container-monitor",
    py_modules=["container_monitor", "icinga2", "app"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        container_monitor=container_monitor:main
    """,
)
