from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='Video File Renamer',
    version='0.0.1b',
    python_requires='>=3.6',
    description="""Renames for video files""",
    long_description=readme(),
    url='https://github.com/Scheercuzy/video-file-renamer',
    author='MX',
    author_email='maxi730@gmail.com',
    license='MIT',
    packages=['video_file_renamer'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'vfr = video_file_renamer.__main__:main'
        ]
    },
)
