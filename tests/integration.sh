#!/usr/bin/env sh

_testSigIntPropagation() {
    _blender_executable_arg=""
    if [ -n "$BLENDER_EXECUTABLE" ]; then
      _blender_executable_arg="--blender-executable $BLENDER_EXECUTABLE"
    fi;
    python3 -m pytest -svv --noconftest $_blender_executable_arg tests/integration/sigint.py &
    # wait some time to start the test suite execution
    sleep 3

    # send sighup
    pid="$(cat /tmp/pytest-blender-integration-sigint.pid)"
    kill -s $1 $pid
    sleep 1

    # due to the current Bash process has not the same STDIN of sys.stdin in plugin,
    # we must send here two SIGINTs to make this test work
    if [ "$1" -eq 2 ]; then
      kill -s 2 $pid
      sleep 1
    fi;

    # check process was killed
    ps -p $pid | grep foo
    assertEquals "Process was not killed by SIGHUP" "1" "$?"
}

testSigIntPropagation() {
  _testSigIntPropagation 2
}

testSigHupPropagation() {
  _testSigIntPropagation 1
}

testSigTermPropagation() {
  _testSigIntPropagation 15
}

prepare() {
  if [ ! -f "shunit2" ]; then
    curl -sSL https://raw.githubusercontent.com/kward/shunit2/master/shunit2 \
      -o shunit2
  fi
}

prepare && . ./shunit2
