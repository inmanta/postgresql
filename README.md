# Postgresql module


## Running tests

1. set environment variables to point to a machine with postgres installed
```
export PG_TEST_HOST=192.168.2.112
export PG_TEST_HOST_USER=centos
```


It is also possible to run the tests in a docker container.
This is controlled by the `INMANTA_TEST_INFRA_SETUP` environment variable.
When it's set to `true`, the container is started, and torn down automatically after the tests.
In this case, the test driver (which is the test case in `test_in_docker.py`) is the only one executed outside the container,
while the rest of the test cases are executed inside the container.
The test results can be found in the `junit.xml` file (outside the container).

The cleanup behavior can be changed by the `INMANTA_NO_CLEAN` environment variable,
when set to `true`, the container is not stopped after the tests.
