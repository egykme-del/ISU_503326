import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'lab2_controller'


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Khalid',
    maintainer_email='egykme@gmail.com',
    description='Service server and client for laboratory work 2.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'service_server = lab2_controller.service_server:main',
            'service_client = lab2_controller.service_client:main',
        ],
    },
)
