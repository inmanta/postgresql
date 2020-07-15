# Postgresql module


## Running tests

1. set environment variables to point to a machine with postgres installed
```
export PG_TEST_HOST=192.168.2.112
export PG_TEST_HOST_USER=centos
```

without the environment variables a docker container is started and used for the tests.