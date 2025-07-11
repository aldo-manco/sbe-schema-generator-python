#!/bin/bash

ulimit -c unlimited

export LD_LIBRARY_PATH="lib64:lib"

./bin/gtech_core_schema_generator output/ xml/$1 v1
