#This makefile assumes existence of a copy (which may be hard linked) of the raw corpus
#This makefile assumes that OCRNormalizer has been run on the corpus (I think this should treat the input files as read-only, hence the safety of "copying" as hard link)

include header.mk

#remaining makefiles listed here in expected order of invocation
#the whole shebang can be built using this makefile, but you are
#likely better off working in stages
include gather.mk
include topics.mk
include postproc.mk
include analyze.mk

all: topics subjects dataframes clouds
