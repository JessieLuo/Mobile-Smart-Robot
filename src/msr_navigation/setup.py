from setuptools import setup
from glob import glob
import os

ros_package_name = "msr_navigation"
python_package_name = "nav"

setup(
    name=ros_package_name,
    version="0.0.1",
    packages=[python_package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + ros_package_name]),
        ("share/" + ros_package_name, ["package.xml"]),
        (os.path.join("share", ros_package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", ros_package_name, "launch"), glob("launch/*.launch.py")),
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
            "semantic_nav_server = nav.semantic_nav_server:main",
            "nav2_goal_client = nav.nav2_goal_client:main",
        ],
    },
)