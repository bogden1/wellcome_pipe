include header.mk

TOPIC_NUMS := $(shell seq 0 $$(($(TOPICS_COUNT) - 1)))
CLOUD_TOPICS   := $(patsubst %, $(CLOUDS)/topic_%.csv,          $(TOPIC_NUMS)) $(patsubst %, $(CLOUDS)/topic_%.png,          $(TOPIC_NUMS)) $(patsubst %, $(CLOUDS)/topic_%.svg,          $(TOPIC_NUMS))
CLOUD_SUBJECTS := $(patsubst %, $(CLOUDS)/topic_%_subjects.csv, $(TOPIC_NUMS)) $(patsubst %, $(CLOUDS)/topic_%_subjects.png, $(TOPIC_NUMS)) $(patsubst %, $(CLOUDS)/topic_%_subjects.svg, $(TOPIC_NUMS))

clouds: $(CLOUD_TOPICS) $(CLOUD_SUBJECTS)

$(CLOUD_TOPICS)   &: topic_clouds.py   _wordcloud.py $(TOPICS_PREFIX)_counts.df
	python3 topic_clouds.py   --force --prefix $(PREFIX) --output-dir $(CLOUD_DIR) $(TOPICS_COUNT)

$(CLOUD_SUBJECTS) &: subject_clouds.py _wordcloud.py $(TOPICS_DOC) $(PREMALLET) $(SUBJECTS).json $(SUBJECTS)_map.json
	python3 subject_clouds.py --force --prefix $(PREFIX) --output-dir $(CLOUD_DIR) --mallet-metadata $(PREMALLET) --subject-labels $(SUBJECTS)_map.json --doc-subjects $(SUBJECTS).json $(TOPICS_COUNT)

