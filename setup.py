from setuptools import setup, find_packages


setup(
    name="comment_filter",
    author='Greg Fitzgerald',
    author_email='gregf@codeaurora.org',
    url='https://source.codeaurora.org/external/qostg/comment-filter',
    version='1.0.0',
    packages=find_packages(),
    scripts=['bin/comments']
)
