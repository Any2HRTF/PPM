from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name='ppm',
    version=version,
    description='Python PPM library.',
    url='https://github.com/Any2HRTF/PPM',
    author='Felix Perfler',
    author_email='felix.perfler@oeaw.ac.at',
    license='The MIT License',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>3.10',
    install_requires=[
        "bpy",
        "numpy",
        "opencv-python",
        "pyntcloud",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)