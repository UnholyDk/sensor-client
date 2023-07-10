from setuptools import setup

if __name__ == '__main__':
    setup(
        name='sensor_client',
        version='0.0.1',
        packages=['sensor_client'],
        description='Great descriprion about sensor-client',
        install_requires=[i.strip() for i in open("requirements.txt").readlines()]
    )
