# setup.py

from setuptools import setup, find_packages

setup(
    name='aemo_to_tariff',
    version='0.7.20',
    description='Convert spot prices from $/MWh to c/kWh for different networks and tariffs',
    author='Ian Connor',
    author_email='ian@powston.com',
    license='MIT',
    packages=find_packages(exclude=["custom_components", "custom_components.*"]),
    install_requires=[
        'pytz',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
