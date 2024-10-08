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
  phase "${identifier}" gather_truncated_serial  make -f gather.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@" truncated_serial
  phase "${identifier}" gather                   make -f gather.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  phase "${identifier}" topics                   make -f topics.mk   -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"

  workon wellcome_pipe
  phase "${identifier}" postproc                 make -f postproc.mk -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  phase "${identifier}" analyze                  make -f analyze.mk  -l 18 -j CORPUS=${corpus} TOPICS_COUNT=${count} "$@"
  echo "Finished ${identifier}"
}

for x in 10 50 100 250 500; do
  build 17xx_rebuild                        "${x}"
  build 17xx_rebuild_split                  "${x}"
  build 17xx_rebuild_entitystripped         "${x}" 'STRIP_ENTITIES=--strip-entities'
  build 17xx_rebuild_split_entitystripped   "${x}" 'STRIP_ENTITIES=--strip-entities'
  build 17xx_rebuild_stemmed                "${x}"                                   'TRUNC_SUFFIX=stemmed'
  build 17xx_rebuild_split_stemmed          "${x}"                                   'TRUNC_SUFFIX=stemmed'

  #In principle this would make sense, but I'd first have to rewrite the stemmer to be able to strip entities
  #Or make entity stripping independent of truncation
  #build 17xx_rebuild_stemmed_entitystripped "${x}" 'STRIP_ENTITIES=--strip-entities' 'TRUNC_SUFFIX=stemmed'
done

#index has to run after everything else is finished (or at least after all of the _title.json files are generated)
workon wellcome_pipe
python3 index.py web data/corpora/17xx_rebuild/normalized/17xx_rebuildsorted_titles.json \
	             data/corpora/17xx_rebuild_entitystripped/normalized/17xx_rebuild_entitystrippedsorted_titles.json \
	             data/corpora/17xx_rebuild_stemmed/normalized/17xx_rebuild_stemmedsorted_titles.json \
		     > LOGS/"${PREFIX}"_index_OUT 2> LOGS/"${PREFIX}"_index_ERR
echo $? > LOGS/"${PREFIX}"_index_XIT
python3 index.py web_split data/corpora/17xx_rebuild_split/normalized/17xx_rebuild_splitsorted_titles.json \
	             data/corpora/17xx_rebuild_entitystripped/normalized/17xx_rebuild_split_entitystrippedsorted_titles.json \
	             data/corpora/17xx_rebuild_stemmed/normalized/17xx_rebuild_split_stemmedsorted_titles.json \
		     > LOGS/"${PREFIX}"_index_split_OUT 2> LOGS/"${PREFIX}"_index_split_ERR
echo $? > LOGS/"${PREFIX}"_index_split_XIT
