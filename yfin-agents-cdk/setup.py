import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="agent_cdk",
    version="0.0.1",
    description="An AWS CDK Python app for Yahoo Finance API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "agent_cdk"},
    packages=setuptools.find_packages(where="agent_cdk"),
    install_requires=[
        "aws-cdk-lib>=2.88.0",
        "constructs>=10.0.0,<11.0.0",
        "cdklabs.generative-ai-cdk-constructs"
    ],
    python_requires=">=3.9",
)
