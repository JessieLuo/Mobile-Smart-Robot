from setuptools import setup

package_name = 'msr_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jesse Luo',
    maintainer_email='jessiescrew98@gmail.com',
    description='Safety control layer for cmd_vel filtering, speed limiting and emergency stop.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'safety_filter = msr_control.safety_filter:main',
        ],
    },
)