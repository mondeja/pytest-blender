#!/usr/bin/env sh

STDOUT=/tmp/pytest-blender-integration-stdout.log

testSigIntPropagation() {
  _blender_executable_arg=""
  if [ -n "$BLENDER_EXECUTABLE" ]; then
    _blender_executable_arg="--blender-executable $BLENDER_EXECUTABLE"
  fi;
  python3 -m pytest -svv $_blender_executable_arg tests/integration/sigint.py > $STDOUT &

  # wait some time to start the test suite execution
  sleep 3

  # send sigint
  pid="$(cat /tmp/pytest-blender-integration-sigint.pid)"
  kill -s 2 $pid
  sleep 1

  printf "HOLA " && cat "$STDOUT"
}

prepare() {
  if [ ! -f "shunit2" ]; then
    curl -sSL https://raw.githubusercontent.com/kward/shunit2/master/shunit2 \
      -o shunit2
  fi
}

prepare && . ./shunit2
