import os

import setuptools

# Need to install campaigns and data/*
# http://peak.telecommunity.com/DevCenter/PythonEggs#accessing-package-resources
# https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files

def find_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

with open('requirements/can4docker-pip.txt') as fp:
    requirements = fp.read().split('\n')

setuptools.setup(
    name="can4docker",
    version="0.0.1",
    author="Christian Gagneraud",
    author_email="chgans@gmail.com",
    description="Docker NetworkDriver plugin providing CAN connectivity",
    long_description="""
can4docker provides CAN connectivity to docker containers.
It is implemented as a docker NetworkDriver plugin
""",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/chgans/can4docker/",
    packages=setuptools.find_packages(exclude=['docs', 'tests']),
    install_requires=requirements,
    python_requires='>=3',
    
    # data_files=[
    #     ('', find_files('data/')),
    #     ('campaigns', find_files('campaigns/')),
    # ]
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Networking",
        "Topic :: System :: Operating System Kernels :: Linux",
        "Framework :: Flask",
    ),
)
