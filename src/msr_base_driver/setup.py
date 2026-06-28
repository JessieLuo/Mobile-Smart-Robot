from setuptools import setup
from glob import glob
import os

package_name = 'nav_base'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),

        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),

        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml') + glob('config/*.pgm')
        ),

        (
            os.path.join('share', package_name),
            ['package.xml']
        ),
    ],

    install_requires=[
        'setuptools',
        'pyserial',
    ],

    zip_safe=True,

    maintainer='jessie',
    maintainer_email='jessie@example.com',

    description='Minimal real base control MVP for MSR.',

    license='MIT',

    entry_points={
        'console_scripts': [
            'safety_filter = nav_base.safety_filter:main',
            'c30d_base_driver = nav_base.c30d_base_driver:main',
        ],
    },
)
