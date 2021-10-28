#!/usr/bin/env sh

STDERR=/tmp/pytest-blender-integration-stderr.log

testSigIntPropagation() {
  python3 -m pytest -svv tests/integration/sigint.py &2> $STDERR &

  # wait some time to start the test suite execution
  sleep 3

  # send sigint
  pid="$(cat /tmp/pytest-blender-integration-sigint.pid)"
  kill -s 2 $pid
  sleep 1

  printf "HOLA " && cat "$STDERR"
}

prepare() {
  if [ ! -f "shunit2" ]; then
    curl -sSL https://raw.githubusercontent.com/kward/shunit2/master/shunit2 \
      -o shunit2
  fi
}

prepare && . ./shunit2
