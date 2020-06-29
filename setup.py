#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

__version__ = '1.0.2'

with open('requirements.txt') as f: 
        requirements = f.readlines() 

setup(name='imagekit-cli',
        description="Tool to migrate Cloudinary storage to Imagekit.io",
        author="cloudmeteor",
        author_email="developer@imagekit.io",
        url="https://github.com/imagekit-developer/imagekit-cli",
        version=__version__,
        license ='MIT', 
        packages = ['imagekitcli'], 
        entry_points ={ 
            'console_scripts': [ 
                'imagekitcli = imagekitcli.migration:main'
            ] 
        }, 
        classifiers =( 
            "Programming Language :: Python :: 3", 
            "License :: OSI Approved :: MIT License", 
            "Operating System :: OS Independent", 
        ), 
        keywords ='imagekit imagekitio cloudinary cli migration storage', 
        install_requires = requirements, 
        zip_safe = False
      )
