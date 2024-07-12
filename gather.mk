#This makefile assumes existence of a copy (which may be hard linked) of the raw corpus
#This makefile assumes that OCRNormalizer has been run on the corpus (I think this should treat the input files as read-only, hence the safety of "copying" as hard link)

include header.mk

tsv: $(PREMALLET)

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
