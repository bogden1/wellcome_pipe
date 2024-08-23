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
  phase "${identifier}" gather_depunctuated      make -f gather.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@" depunctuated
  echo '  gather_depunctuated done'
  phase "${identifier}" gather_truncated_serial  make -f gather.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@" truncated_serial
  echo '  gather_truncated_serial done'
  phase "${identifier}" gather                   make -f gather.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  echo '  gather done'
  phase "${identifier}" topics                   make -f topics.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  echo '  topics done'

  workon wellcome_pipe
  phase "${identifier}" postproc                 make -f postproc.mk -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  echo '  postproc done'
  phase "${identifier}" analyze                  make -f analyze.mk  -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} WEB_DIR=example_web "$@"
  echo '  analyze done'
  echo "Finished ${identifier}"
}

for x in 10; do
  build example_split "${x}" 'TRUNC_SUFFIX=stemmed'
done

#index has to run after everything else is finished (or at least after all of the _title.json files are generated)
workon wellcome_pipe
python3 index.py example_web data/corpora/example_split/normalized/example_splitsorted_titles.json \
		     > LOGS/"${PREFIX}"_index_OUT 2> LOGS/"${PREFIX}"_index_ERR
echo $? > LOGS/"${PREFIX}"_index_XIT
