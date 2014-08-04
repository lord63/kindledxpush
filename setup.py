from setuptools import setup

setup(
    name='kindlepush',
    version='0.1.0',
    description='Automatically send your doc to your kindle without clicking the deliver button',
    url='https://github.com/lord63/kindledxpush',
    author='lord63',
    author_email='lord63.j@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='kindle push automatically 3G',
    package=['kindlepush'],
    install_requires=['requests', 'beautifulsoup4', 'terminal'],
    entry_points={
        'console_scripts': [
            'kindlepush=kindlepush.kindlepush:main']
        }
)