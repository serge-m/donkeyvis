from setuptools import setup, find_packages

setup(
    name='donkeyvis',
    version='0.0.1',
    description='Visualization GUI tool for donkey car tubs and model',
    url='https://github.com/serge-m/donkeyvis',
    author='Sergey Matyunin',
    author_email='sbmatyunin@gmail.com',
    license='MIT',
    entry_points={
        'console_scripts': [
            'donkeyvis=donkeyvis.donkey_vis:visualization',
        ],
    },
    install_requires=[
        'donkeycar[tf]',
        'matplotlib',
        'PyQt5'
    ],

    extras_require={},

    include_package_data=True,

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='selfdriving cars donkeycar diyrobocars visualization',

    packages=find_packages(exclude=(['tests', 'docs', 'site', 'env'])),
)
