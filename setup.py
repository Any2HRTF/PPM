from setuptools import setup

version = '2.0'

setup(
    name='PyBezierPPM',
    version=version,
    description='Python PPM module.',
    url='https://github.com/Any2HRTF/PPM',
    author='The BezierPPM authors',
    license='EUPL-1.2',
    license_files = ('LICENSE',),
    packages=['bezierppm'],
    package_data={
        'bezierppm': ['resources/*.csv', 'resources/*.blend'],
    },
    include_package_data=True,
    python_requires='==3.10.*',
    zip_safe=False,
    install_requires=[
        "numpy",
        "bpy",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent",
    ]
)
