import setuptools
import sys
import subprocess
from setuptools.command.install import install


with open("requirements.txt", "r", encoding="utf-8") as fr:
    install_requires = fr.readlines()


class pip_install(install):
    def run(self):
        for package in install_requires:
            subprocess.call([
                sys.executable, 
                '-m', 
                'pip', 
                'install', 
                package
            ])
        install_requires.clear()
        install.run(self)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="aiven_exercise",
    version="0.0.1",
    author="Jesse Aapro",
    author_email="jesse.j.aapro@gmail.com",
    description="Website availability monitor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jjaapro/websiteavailabilitymonitor/",
    project_urls={
        "Bug Tracker": "https://github.com/jjaapro/websiteavailabilitymonitor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=install_requires,
    cmdclass={
        'pip_install': pip_install}
)
