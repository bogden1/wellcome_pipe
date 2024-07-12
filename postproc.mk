include header.mk

DATAFRAMES := $(TOPICS_PREFIX).df $(TOPICS_PREFIX)_counts.df $(TOPICS_PREFIX)_sums.df $(TOPICS_PREFIX)_freqs.df $(TOPIC_PREFIX)_freqs.csv

postproc: dataframes subjects

dataframes: $(DATAFRAMES)

subjects: $(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG

#Grouped target: one invocation builds all targets
#TODO: Add args to the tool to allow building the targets independently
$(DATAFRAMES) &: dataframes.py $(TOPICS_FILE)
	python3 $< $(TOPICS_FILE) --force

$(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG &: decorate_subjects.py $(PREMALLET)
	python3 $< --pre-mallet $(PREMALLET) --output $(SUBJECTS).json &> $(SUBJECTS).LOG
