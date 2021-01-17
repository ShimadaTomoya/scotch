import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ktamido",
    version="0.0.1",
    author="ktamido",
    author_email="ng3rdstmadgke@gmail.com",
    description="web site crawler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ng3rdstmadgke/scotch.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
