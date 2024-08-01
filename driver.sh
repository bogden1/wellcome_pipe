#!/bin/bash

. /usr/share/virtualenvwrapper/virtualenvwrapper.sh
PREFIX="`basename $0`"
PREFIX="${PREFIX%.*}"

trap 'if [ -e SHUTDOWN ]; then shutdown -h +15; fi' EXIT

phase() {
  log="LOGS/${PREFIX}_${2}_${1}"
  shift 2
  echo "$@" > "${log}_OUT"
  "$@" >> "${log}_OUT" 2> "${log}_ERR"
  errcode=$?
  echo ${errcode} > "${log}_XIT"
  if [ x"${errcode}" != x0 ]; then exit ${errcode}; fi
}

build() {
  corpus="$1"
  count="$2"
  identifier="${corpus}_${count}"
  shift 2

  echo "Started ${identifier}"
  workon lemmastemma2
  phase "${identifier}" gather_depunctuated      make -f gather.mk   -l 12 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@" depunctuated
  phase "${identifier}" gather_lemmatized_serial make -f gather.mk   -l 12 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@" lemmatized_serial
  phase "${identifier}" gather                   make -f gather.mk   -l 12 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  phase "${identifier}" topics                   make -f topics.mk   -l 12 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"

  workon wellcome_pipe
  phase "${identifier}" postproc                 make -f postproc.mk -l 12 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  phase "${identifier}" analyze                  make -f analyze.mk  -l 12 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  echo "Finished ${identifier}"
}

for x in 10 50 100 250 500; do
  build 17xx_rebuild "${x}"
  build 17xx_rebuild_entitystripped "${x}" 'STRIP_ENTITIES=--strip-entities'
done
