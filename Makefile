#This makefile assumes existence of a copy (which may be hard linked) of the raw corpus
#This makefile assumes that OCRNormalizer has been run on the corpus (I think this should treat the input files as read-only, hence the safety of "copying" as hard link)

SHELL := bash
CORPUS := example
OUT_SUFFIX := sorted
NORMALIZED := $(abspath data/corpora/$(CORPUS)/normalized/)
METADATA  := $(NORMALIZED)/$(CORPUS).jsonl
PREMALLET := $(NORMALIZED)/$(CORPUS)$(OUT_SUFFIX).tsv
CLEAN   := $(wildcard $(NORMALIZED)/$(CORPUS)/*.clean.txt) #I am assuming the OCRNormalizer has been run
STEMMED := $(addsuffix .stemmed, $(CLEAN))
LEMMATIZED := $(addsuffix .lemmatized, $(CLEAN))

TRUNCATED := $(LEMMATIZED) #change these two together -- must be STEMMED/stemmed or LEMMATIZED/lemmatized
TRUNC_SUFFIX := lemmatized

DESTOPPED := $(addsuffix .destopped, $(TRUNCATED))
MALLETIZED = $(abspath $(NORMALIZED)/../malletized)
TOPICS_COUNT := 500
MALLET_FILE        := $(MALLETIZED)/$(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX).mallet
TOPICS_FILE        := $(MALLETIZED)/$(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)-topic_state_$(TOPICS_COUNT).gz
TOPICS_KEYS        := $(MALLETIZED)/$(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)-keys_$(TOPICS_COUNT).txt
TOPICS_DOC         := $(MALLETIZED)/$(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)-composition_$(TOPICS_COUNT).txt
TOPICS_WEIGHTS     := $(MALLETIZED)/$(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)-topic_work_weights_$(TOPICS_COUNT)
TOPICS_DIAGNOSTICS := $(MALLETIZED)/$(CORPUS)_$(TRUNC_SUFFIX)_$(OUT_SUFFIX)-diagnostics_$(TOPICS_COUNT).txt
MALLET_BIN := /home/bogden/Downloads/Mallet-202108/bin/mallet
MALLET_MEM := 10g

topics: $(TOPICS_FILE)

mallet_file: $(MALLET_FILE)

tsv: $(PREMALLET)

$(TOPICS_FILE): $(MALLET_FILE)
	MALLET_MEMORY=$(MALLET_MEM) $(MALLET_BIN) train-topics --input $< --num-topics $(TOPICS_COUNT) --optimize-interval 10 --output-state $@ --output-topic-keys $(TOPICS_KEYS) --output-doc-topics $(TOPICS_DOC) --random-seed 999 --topic-word-weights-file $(TOPICS_WEIGHTS) --diagnostics-file $(TOPICS_DIAGNOSTICS)

$(MALLET_FILE): $(PREMALLET) | $(MALLETIZED)
	$(MALLET_BIN) import-file --input $< --output $@ --keep-sequence

$(PREMALLET): hatori_data.py $(METADATA) $(DESTOPPED)
	python3 $< $(METADATA) --text-dir $(NORMALIZED)/$(CORPUS) --text-suffix .clean.txt.$(TRUNC_SUFFIX).destopped --strip-json $(METADATA).stripped > $@

destopped: $(DESTOPPED)

stemmed: $(STEMMED)

lemmatized: $(LEMMATIZED)

%.destopped: lemmastemma/destopper.py %
	$< $*

%.stemmed: lemmastemma/stemmer.py %
	$< $*

%.lemmatized: lemmastemma/lemmatizer.py %
	$< $*

$(MALLETIZED):
	mkdir $@
