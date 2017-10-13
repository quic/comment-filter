## Contributing to Comment Filter

Hi there!
We’re thrilled that you’d like to contribute to this project.
Your help is essential for keeping this project great and for making it better.

## Branching Strategy

In general, contributors should develop on branches based off of `master` and pull requests should be made against `master`.

## Submitting a pull request

1. Please read our [code of conduct](code-of-conduct.md] and [license](LICENSE.txt).
1. [Fork](https://github.com/codeauroraforum/comment-filter/fork) and clone the repository.
1. Create a new branch based on `master`: `git checkout -b <my-branch-name> master`.
1. Make your changes, add tests, and make sure the tests still pass.
1. Push to your fork and [submit a pull request](https://github.com/codeauroraforum/comment-filter/compare) from your branch to `master`.
1. Pat yourself on the back and wait for your pull request to be reviewed.

Here are a few things you can do that will increase the likelihood of your pull request to be accepted:

- Follow the existing style where possible. We try and adhere to [pep8](https://www.python.org/dev/peps/pep-0008/).
- Write tests.
- Keep your change as focused as possible.
  If you want to make multiple independent changes, please consider submitting them as separate pull requests.
- Write a [good commit message](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).


## Developer Certification of Origin (DCO)
Comment Filter requires the Developer Certificate of Origin (DCO) process to be followed.

The DCO is an attestation attached to every contribution made by every developer. In the commit message of the contribution, the developer simply adds a Signed-off-by statement and thereby agrees to the DCO, which you can find below or at http://developercertificate.org/.

Comment Filter does not merge any pull requests made until each commit has been signed for the DCO.

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
 ```

### DCO commit example

After committing your changes with `git commit -s`, your message should look something like:
```
commit 442deae270bf585052be012b064ed92299e221c4
Author: Random Developer <random@developer.org>
Date:   Sat Oct 21 08:33:15 2017 -0700

    My example commit message

    Signed-off-by: Random Developer <random@developer.org>
```
