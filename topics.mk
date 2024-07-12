include header.mk

topics: $(TOPICS_FILE)

mallet_file: $(MALLET_FILE)

$(TOPICS_FILE): $(MALLET_FILE)
	MALLET_MEMORY=$(MALLET_MEM) $(MALLET_BIN) train-topics --input $< --num-topics $(TOPICS_COUNT) --optimize-interval 10 --output-state $@ --output-topic-keys $(TOPICS_KEYS) --output-doc-topics $(TOPICS_DOC) --random-seed 999 --topic-word-weights-file $(TOPICS_WEIGHTS) --diagnostics-file $(TOPICS_DIAGNOSTICS)

$(MALLET_FILE): $(PREMALLET) | $(MALLETIZED)
	$(MALLET_BIN) import-file --input $< --output $@ --keep-sequence

$(MALLETIZED):
	mkdir $@
