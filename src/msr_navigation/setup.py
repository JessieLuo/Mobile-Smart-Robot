from setuptools import setup
from glob import glob
import os

package_name = "msr_navigation"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="Jesse",
    maintainer_email="jessiescrew98@gmail.com",
    description="Navigation package for mobile sorting robot.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "semantic_nav_server = msr_navigation.semantic_nav_server:main",
            "nav2_goal_client = msr_navigation.nav2_goal_client:main",
        ],
    },
)