ifndef _HEADER
_HEADER = 1

SHELL := bash
CORPUS := example
OUT_SUFFIX := sorted
NORMALIZED := $(abspath data/corpora/$(CORPUS)/normalized/)
METADATA  := $(NORMALIZED)/$(CORPUS).jsonl #An initial input file
PREMALLET := $(NORMALIZED)/$(CORPUS)$(OUT_SUFFIX).tsv
SUBJECTS  := $(NORMALIZED)/$(CORPUS)$(OUT_SUFFIX)_subjects
TITLES    := $(NORMALIZED)/$(CORPUS)$(OUT_SUFFIX)_titles
CLEAN   := $(wildcard $(NORMALIZED)/$(CORPUS)/*.clean.txt) #I am assuming the OCRNormalizer has been run. These are the initial input files for this Makefile family.
DEPUNCTUATED := $(addsuffix .depunctuated, $(CLEAN))
STEMMED := $(addsuffix .stemmed, $(DEPUNCTUATED))
LEMMATIZED := $(addsuffix .lemmatized, $(DEPUNCTUATED))

TRUNCATED := $(LEMMATIZED) #change these two together -- must be STEMMED/stemmed or LEMMATIZED/lemmatized
TRUNC_SUFFIX := lemmatized

DESTOPPED := $(addsuffix .destopped, $(TRUNCATED))
MALLETIZED = $(abspath $(NORMALIZED)/../malletized)
CLOUD_DIR := $(abspath $(NORMALIZED)/../clouds)
FIG_DIR   := $(abspath $(NORMALIZED)/../figures)
TOP_DIR   := $(abspath $(NORMALIZED)/..) #TODO: Rewrite other *DIRs in terms of TOP_DIR
TOPICS_COUNT := 500
BASE_PREFIX := $(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)
CLOUDS := $(CLOUD_DIR)/$(BASE_PREFIX)_$(TOPICS_COUNT)
FIGS   := $(FIG_DIR)/$(BASE_PREFIX)_$(TOPICS_COUNT)
PREFIX := $(MALLETIZED)/$(BASE_PREFIX)
MALLET_FILE        := $(PREFIX).mallet
TOPICS_PREFIX      := $(PREFIX)-topic_state_$(TOPICS_COUNT)
TOPICS_FILE        := $(TOPICS_PREFIX).gz
TOPICS_KEYS        := $(PREFIX)-keys_$(TOPICS_COUNT).txt
TOPICS_DOC         := $(PREFIX)-composition_$(TOPICS_COUNT).txt
TOPICS_WEIGHTS     := $(PREFIX)-topic_work_weights_$(TOPICS_COUNT)
TOPICS_DIAGNOSTICS := $(PREFIX)-diagnostics_$(TOPICS_COUNT).txt
MALLET_BIN := /home/bogden/Downloads/Mallet-202108/bin/mallet
MALLET_MEM := 20g
endif