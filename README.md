# example-package

This contains ...

## Cutting a release

The example-package uses [semantic versioning](https://semver.org), so all versions should follow that format.

### Standard Release

The process to release a new version requires a chore branch be created to increment the version. A Pull Request should then be created to merge it back into master.
Once in master, Jenkins will build and tag the release.

Once the release has been built and tagged, a new release should be created in [Github](https://github.com/Katlean/example-package/releases) to document the release.

### Bug Release for a specific minor version

If any non-fix changes have been merged to master since the minor version in question, a version branch will need to
be created if one doesn't already exist. For example, if v1.5.0 is released and we need to release v1.5.1, but a feat request has since been merged into master, a `v1.5` branch needs to be created (unless one already exists).

For each bug fix to put into the new release, the fix should first be merged into master. Then, a branch should be created from the version branch, named like:
`fix/v1.5/MS-###-my-branch-name`. The change should then be cherry-picked into the new branch, and a pull request
opened with the target branch being the version branch (in this example, `v1.5`).

After all pull requests are merged into the version branch, the version can be updated on the version branch to the
appropriate version number and committed. After a successful build, a release branch should be created for the release:
`release/1.5.1` and pushed.

This will trigger a Jenkins job that will build and tag the release.

Once the release has been built and tagged, a new release should be created in [Github](https://github.com/Katlean/example-package/releases) to document the release.

TL;DR:

* Checkout/Create version branch `v{x.y}`
* Create branch for bug fix `fix/v{x.y}/MS-###-my-branch-name`
* cherry-pick fix from master into fix branch
* Create PR & Merge after approvals
* Update VERSION in version branch, commit, and push
* create release branch for version `release/{x.y.z}` and push

### One-off Release

When a temporary release is needed to fix a specific issue or test a specific set of code, a release branch (a branch beginning with 'release/') can be used.
Jenkins will build and tag a release it finds in the release branch.

## Installation

Install locally or with zest private PyPI (<https://zaml-zest-dev.jfrog.io/artifactory/api/pypi/zest_pypi_private/simple>):

```shell
pip install example_package
```

### For local development

example-package should be installed in editable mode with dev dependencies so the code in your working copy is run:

```bash
pip install -e '.[dev]'
```

## Usage

To use the example package, you will ...

## Pytest unit tests

### Testing

Run tests with:
`pytest --cov=example_package tests`

or

Run tests with code coverage report

```bash
coverage run -m --source=example_package pytest --verbose --color=yes tests

coverage report -mi
```

### Snapshots

The unit tests use syrupy to check response data vs previously recorded snapshots (in `tests/__snapshots__`).

#### Updating Snapshots

When the code changes, there may be cases that these snapshots need to be updated (after proper verification that the failure is not due to a bug). To update these snapshots, simply run:
`pytest --snapshot-update tests/`

This will update the snapshots in `tests/__snapshots__` and these changes can then be committed to the repository.
