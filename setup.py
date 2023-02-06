"""BMS Analytics setup"""
from setuptools import setup, find_packages

setup(
    name="group_chat_app",
    version="1.0",
    description="Group chat service",
    long_description="Group chat service",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9.0",
        "Framework :: Django :: 3.2",
    ],
    author="Rishikesh Jha",
    author_email="rishijha424@gmail.com",
    url="",
    keywords="group chat",
    license=None,
    packages=find_packages(""),
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools", "django"],
    extras_require={"docs": ["Sphinx"], "tests": ["django-pytest", "pytest"]},
)
