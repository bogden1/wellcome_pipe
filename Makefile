#This makefile assumes existence of a copy (which may be hard linked) of the raw corpus
#This makefile assumes that OCRNormalizer has been run on the corpus (I think this should treat the input files as read-only, hence the safety of "copying" as hard link)

SHELL := bash
CORPUS := example
OUT_SUFFIX := sorted
NORMALIZED := $(abspath data/corpora/$(CORPUS)/normalized/)
METADATA  := $(NORMALIZED)/$(CORPUS).jsonl
PREMALLET := $(NORMALIZED)/$(CORPUS)$(OUT_SUFFIX).tsv
SUBJECTS  := $(NORMALIZED)/$(CORPUS)$(OUT_SUFFIX)_subjects
CLEAN   := $(wildcard $(NORMALIZED)/$(CORPUS)/*.clean.txt) #I am assuming the OCRNormalizer has been run
DEPUNCTUATED := $(addsuffix .depunctuated, $(CLEAN))
STEMMED := $(addsuffix .stemmed, $(DEPUNCTUATED))
LEMMATIZED := $(addsuffix $(STRIP_ENTITIES).lemmatized, $(DEPUNCTUATED))

TRUNCATED := $(LEMMATIZED) #change these two together -- must be STEMMED/stemmed or LEMMATIZED/lemmatized
TRUNC_SUFFIX := lemmatized

DESTOPPED := $(addsuffix .destopped, $(TRUNCATED))
MALLETIZED = $(abspath $(NORMALIZED)/../malletized)
CLOUD_DIR := $(abspath $(NORMALIZED)/../clouds)
TOPICS_COUNT := 500
BASE_PREFIX := $(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)
CLOUDS := $(CLOUD_DIR)/$(BASE_PREFIX)
PREFIX := $(MALLETIZED)/$(BASE_PREFIX)
MALLET_FILE        := $(PREFIX).mallet
TOPICS_PREFIX      := $(PREFIX)-topic_state_$(TOPICS_COUNT)
TOPICS_FILE        := $(TOPICS_PREFIX).gz
TOPICS_KEYS        := $(PREFIX)-keys_$(TOPICS_COUNT).txt
TOPICS_DOC         := $(PREFIX)-composition_$(TOPICS_COUNT).txt
TOPICS_WEIGHTS     := $(PREFIX)-topic_work_weights_$(TOPICS_COUNT)
TOPICS_DIAGNOSTICS := $(PREFIX)-diagnostics_$(TOPICS_COUNT).txt
MALLET_BIN := /home/bogden/Downloads/Mallet-202108/bin/mallet
MALLET_MEM := 10g

DATAFRAMES := $(TOPICS_PREFIX).df $(TOPICS_PREFIX)_counts.df $(TOPICS_PREFIX)_sums.df $(TOPICS_PREFIX)_freqs.df $(TOPIC_PREFIX)_freqs.csv

TOPIC_NUMS := $(shell seq 0 $$(($(TOPICS_COUNT) - 1)))
CLOUD_TOPICS   := $(patsubst %, $(CLOUDS)/topic_%.csv,          $(TOPIC_NUMS)) $(patsubst %, $(CLOUDS)/topic_%.png,          $(TOPIC_NUMS)) $(patsubst %, $(CLOUDS)/topic_%.svg,          $(TOPIC_NUMS))


all: topics subjects dataframes clouds

dataframes: $(DATAFRAMES)

clouds: $(CLOUD_TOPICS) #$(CLOUD_SUBJECTS)

$(CLOUD_TOPICS) &: topic_clouds.py _wordcloud.py $(TOPICS_PREFIX)_counts.df
	python3 topic_clouds.py --force --prefix $(PREFIX) --output-dir $(CLOUD_DIR) $(TOPICS_COUNT)

subjects: $(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG

topics: $(TOPICS_FILE)

mallet_file: $(MALLET_FILE)

tsv: $(PREMALLET)

#Grouped target: one invocation builds all targets
#TODO: Add args to the tool to allow building the targets independently
$(DATAFRAMES) &: dataframes.py $(TOPICS_FILE)
	python3 $< $(TOPICS_FILE) --force

$(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG &: decorate_subjects.py $(PREMALLET)
	python3 $< --pre-mallet $(PREMALLET) --output $(SUBJECTS).json &> $(SUBJECTS).LOG

$(TOPICS_FILE): $(MALLET_FILE)
	MALLET_MEMORY=$(MALLET_MEM) $(MALLET_BIN) train-topics --input $< --num-topics $(TOPICS_COUNT) --optimize-interval 10 --output-state $@ --output-topic-keys $(TOPICS_KEYS) --output-doc-topics $(TOPICS_DOC) --random-seed 999 --topic-word-weights-file $(TOPICS_WEIGHTS) --diagnostics-file $(TOPICS_DIAGNOSTICS)

$(MALLET_FILE): $(PREMALLET) | $(MALLETIZED)
	$(MALLET_BIN) import-file --input $< --output $@ --keep-sequence

$(PREMALLET): hatori_data.py $(METADATA) $(DESTOPPED)
	python3 $< $(METADATA) --text-dir $(NORMALIZED)/$(CORPUS) --text-suffix .clean.txt.$(TRUNC_SUFFIX).destopped --strip-json $(METADATA).stripped > $@

depunctuated: $(DEPUNCTUATED)

destopped: $(DESTOPPED)

stemmed: $(STEMMED)

lemmatized: $(LEMMATIZED)

%.depunctuated: lemmastemma/depunctuator.py
	$< $*

%.destopped: lemmastemma/destopper.py %
	$< $*

%.stemmed: lemmastemma/stemmer.py %
	$< $*

#make STRIP_ENTITIES='--strip_entities' to get the lemmatizer to strip all named entities
%.lemmatized: lemmastemma/lemmatizer.py %
	$< $(STRIP_ENTITIES) $*

$(MALLETIZED):
	mkdir $@
