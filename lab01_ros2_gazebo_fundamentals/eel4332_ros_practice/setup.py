from glob import glob
import os

from setuptools import find_packages, setup


package_name = "eel4332_ros_practice"


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="EEL 4332 Course Staff",
    maintainer_email="maintainer@example.com",
    description="Minimal ROS 2 publisher/subscriber practice for EEL 4332.",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "counter_publisher = eel4332_ros_practice.counter_publisher:main",
            "counter_subscriber = eel4332_ros_practice.counter_subscriber:main",
        ],
    },
)
