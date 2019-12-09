from setuptools import setup, find_packages

setup(
    name='pedl_deploy',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'pyyaml',
        'botocore'
    ],
    entry_points={
        'console_scripts': [
            'pedl-deploy = pedl_deploy.main:main'
        ]
    }
)