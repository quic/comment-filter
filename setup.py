#  Copyright (c) 2017, Qualcomm Innovation Center, Inc. All rights reserved.
#  SPDX-License-Identifier: BSD-3-Clause

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
