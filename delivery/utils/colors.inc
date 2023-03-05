function echoGreen {
  echo -e "\033[0;32m$*\033[0m" 1>&2
}

function echoCyan {
  echo -e "\033[0;36m$*\033[0m" 1>&2
}

function success() {
  echoGreen "$*"
}

function error() {
  echoRed "$*"
}

function echoRed {
  echo -e "\033[0;31m$*\033[0m" 1>&2
}

function echoYellow {
  echo -e "\033[0;33m$*\033[0m" 1>&2
}
