#!/usr/bin/env python

from distutils.core import setup

setup (name="Distutils",
       version = "1.0",
       description = "PyAppLaunch",
       author = "Andreas Fischer",
       author_email = "andreas@latticepoint.org",
       url = "",
       packages = ["pyapplaunch"],
       package_data = {"pyapplaunch": ["images/*"]},
       scripts = ["pyapplaunch.py"]
)
