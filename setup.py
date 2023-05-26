from setuptools import setup, find_packages

version = '0.1'

setup(
    name='PyPPM',
    version=version,
    description='Python PPM library.',
    url='https://github.com/Any2HRTF/PPM',
    author='Felix Perfler',
    author_email='felix.perfler@oeaw.ac.at',
    license='EUPL-1.2',
    license_files = ('LICENSE.txt',),
    readme='README.md',
    packages=find_packages(),
    package_data={
        'ppm': ['resources/*.csv', 'resources/*.blend'],
    },
    include_package_data=True,
    python_requires='<3.10',
    zip_safe=False,
    install_requires=[
        "numpy",
        "bpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent",
    ]
)
