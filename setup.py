from setuptools import find_packages, setup


# Minimum requirements for using this library in another project.
requirements = []


setup(
    name="fml",
    version="0.0.1",
    # description="",
    # author_email="",
    # author="",
    # url="https://github.com/<account>/fml",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
)
