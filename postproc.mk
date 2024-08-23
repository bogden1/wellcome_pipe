include header.mk

DATAFRAMES := $(TOPICS_PREFIX).df $(TOPICS_PREFIX)_counts.df $(TOPICS_PREFIX)_sums.df $(TOPICS_PREFIX)_freqs.df $(TOPIC_PREFIX)_freqs.csv

postproc: dataframes subjects

dataframes: $(DATAFRAMES)

subjects: $(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG

clean:
	rm -f $(DATAFRAMES) $(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG $(TITLES).json $(TITLES)_short.json

#Grouped target: one invocation builds all targets
#TODO: Add args to the tool to allow building the targets independently
$(DATAFRAMES) &: dataframes.py $(TOPICS_FILE)
	python3 $< $(TOPICS_FILE)

$(SUBJECTS).json $(SUBJECTS)_map.json $(SUBJECTS).LOG $(TITLES).json $(TITLES)_short.json &: metadata.py $(PREMALLET)
	python3 $< --pre-mallet $(PREMALLET) --output-subjects $(SUBJECTS).json --output-titles $(TITLES).json
