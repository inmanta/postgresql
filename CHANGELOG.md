# Changelog

## v1.0.9 - ?


## v1.0.8 - 2024-03-29


## v1.0.7 - 2024-01-03

- update GPG key

## v1.0.6 - 2023-12-07


## v1.0.5 - 2023-12-07


## v1.0.4 - 2023-12-07


## v1.0.3 - 2023-11-22

- Use the same python inside and outside of container while running the tests

## v1.0.2 - 2023-11-16

- Updated tests for iso 7

## v1.0.1 - 2023-10-12


## v1.0.0 - 2023-09-05

- Install PG13 by default instead of PG10

## v0.4.3 - 2023-06-30


## v0.4.2 - 2023-05-03

- Don't execute the apt-get upgrade command in the Dockerfile for the tests to prevent issue with invalid locale

## v0.4.1 - 2023-04-04


## v0.4.0 - 2023-02-20

- Support PG13



## v0.3.3
- Fixed Dockerfile missing python executable

## v0.3.2
- Updated Dockerfile to use Debian 11 (bullseye) image

## v0.3.0
- Add support for stat statement and slow query logging

## V0.2.2
- add ENV DEBIAN_FRONTEND=noninteractive to dockerfile

## V0.2.1
- Add pyproject.toml file and set asyncio_mode to auto

## V0.2.0
- Added HA support

## V0.1.10
- Work around for issue with exec module

## V0.1.9
- Release dependency updates
## V0.1.8
- Added support to run the tests against the V2 module of this module
## V0.1.7
- Fixed bug in RHEL 8 support
## V0.1.6
- Added RHEL 8 support
## V0.1.4
- Ensure same python packages are installed inside and outside of the container
## V0.1.3
- Use inmanta-dev-dependencies package

## V0.1.2
 - added fixture to run tests in docker
