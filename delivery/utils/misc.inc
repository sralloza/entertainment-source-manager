function echoerr() {
  echo "$@" 1>&2
}

function fatal() {
  error "[error] $@"
  exit 1
}
