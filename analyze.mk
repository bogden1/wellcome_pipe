include header.mk

TOPIC_NUMS := $(shell seq 0 $$(($(TOPICS_COUNT) - 1)))
TOPIC_CLOUD_IMGS   := $(patsubst %, $(CLOUDS)/topic_%.svg,          $(TOPIC_NUMS))
TOPIC_CLOUD_DATA   := $(patsubst %, $(CLOUDS)/topic_%.csv,          $(TOPIC_NUMS)) 
SUBJECT_CLOUD_IMGS := $(patsubst %, $(CLOUDS)/topic_%_subjects.svg, $(TOPIC_NUMS))
SUBJECT_CLOUD_DATA := $(patsubst %, $(CLOUDS)/topic_%_subjects.csv, $(TOPIC_NUMS))
DOC_CLOUD_IMGS     := $(patsubst %, $(CLOUDS)/topic_%_docs.svg,     $(TOPIC_NUMS))
DOC_CLOUD_DATA     := $(patsubst %, $(CLOUDS)/topic_%_docs.csv,     $(TOPIC_NUMS))
#SUMMARY_DOC_FIGS := $(patsubst %, $(FIGS)/topic_%_docs40.svg, $(TOPIC_NUMS)) $(patsubst %, $(FIGS)/topic_%_topdocs.svg, $(TOPIC_NUMS))
SUMMARY_DOC_FIGS := $(patsubst %, $(FIGS)/doclist_topic_%.html, $(TOPIC_NUMS))
#INDIVIDUAL_DOC_FIGS = $(shell cat $(TITLES).json | jq -r 'keys[]' | sed 's#.*#$(FIGS)/&.svg#')
INDIVIDUAL_DOC_FIGS = $(shell cat $(TITLES).json | jq -r 'keys[]' | sed 's#.*#$(FIGS)/&.div#')
#FINAL_FIGS   = $(patsubst %, $(FIGS)/pp_%,   $(notdir $(INDIVIDUAL_DOC_FIGS) $(SUMMARY_DOC_FIGS)))
FINAL_FIGS   = $(patsubst %.div, $(FIGS)/wrapper_%.html, $(notdir $(INDIVIDUAL_DOC_FIGS))) $(patsubst %, $(FIGS)/%, $(notdir $(SUMMARY_DOC_FIGS))) #$(patsubst %, $(FIGS)/pp_%,   $(notdir $(SUMMARY_DOC_FIGS)))
FINAL_CLOUDS = $(patsubst %, $(CLOUDS)/pp_%, $(notdir $(SUBJECT_CLOUD_IMGS) $(DOC_CLOUD_IMGS)))
#WRAPPED_FIGS = $(patsubst pp_%.svg, $(FIGS)/wrapper_%.html, $(notdir $(FINAL_FIGS)))
#WRAPPED_FIGS = $(patsubst %.div, $(FIGS)/wrapper_%.html, $(notdir $(FINAL_FIGS)))
WEB_DIR := web

explore: final_figs final_clouds | $(WEB_DIR)
	./explore.sh $(BASE_PREFIX)_$(TOPICS_COUNT) $(TOP_DIR) $(WEB_DIR)

#wrappers: $(WRAPPED_FIGS)

final_figs: $(FINAL_FIGS)

figs: $(INDIVIDUAL_DOC_FIGS) $(SUMMARY_DOC_FIGS)

final_clouds: $(FINAL_CLOUDS) topic_clouds #FINAL_CLOUDS implicitly pulls in subject_clouds and doc_clouds

topic_clouds: $(TOPIC_CLOUD_IMGS) $(TOPIC_CLOUD_DATA)

subject_clouds: $(SUBJECT_CLOUD_IMGS) $(SUBJECT_CLOUD_DATA)

doc_clouds: $(DOC_CLOUD_IMGS) $(DOC_CLOUD_DATA)

clean:
	rm -rf $(CLOUDS)/ $(FIGS)/ $(WEB_DIR)/$(BASE_PREFIX)_$(TOPICS_COUNT)/

clean_topic_clouds:
	rm -f $(TOPIC_CLOUD_IMGS) $(TOPIC_CLOUD_DATA)

clean_subject_clouds:
	rm -f $(SUBJECT_CLOUDS_IMGS) $(SUBJECT_CLOUD_DATA) $(DOC_CLOUD_IMGS) $(DOC_CLOUD_DATA)

clean_doc_figs:
	rm -f $(INDIVIDUAL_DOC_FIGS) $(SUMMARY_DOC_FIGS)

$(TOPIC_CLOUD_IMGS) $(TOPIC_CLOUD_DATA) &: topic_clouds.py   _wordcloud.py $(TOPICS_PREFIX)_counts.df | $(CLOUD_DIR)
	python3 topic_clouds.py   --force --prefix $(PREFIX) --output-dir $(CLOUD_DIR) --colorize $(TOPICS_COUNT)

$(SUBJECT_CLOUD_IMGS) $(SUBJECT_CLOUD_DATA) $(DOC_CLOUD_IMGS) $(DOC_CLOUD_DATA) &: meta_clouds.py _wordcloud.py $(TOPICS_DOC) $(PREMALLET) $(SUBJECTS).json $(SUBJECTS)_map.json
	python3 meta_clouds.py --force --prefix $(PREFIX) --output-dir $(CLOUD_DIR) --mallet-metadata $(PREMALLET) --subject-labels $(SUBJECTS)_map.json --doc-subjects $(SUBJECTS).json --doc-labels $(TITLES).json --colorize $(TOPICS_COUNT)

$(INDIVIDUAL_DOC_FIGS) &: meta_bars.py $(PREMALLET) $(TOPICS_DOC) | $(FIG_DIR)
	python3 meta_bars.py    --force --prefix $(PREFIX) --output-dir $(FIG_DIR) --mallet-metadata $(PREMALLET) --force $(TOPICS_COUNT) --documents

$(SUMMARY_DOC_FIGS) &:   list_members.py $(PREMALLET) $(TOPICS_DOC) $(INDIVIDUAL_DOC_FIGS) | $(FIG_DIR)
	python3 list_members.py --force --prefix $(PREFIX) --output-dir $(FIG_DIR) --mallet-metadata $(PREMALLET) --force $(TOPICS_COUNT)

#$(SUMMARY_DOC_FIGS) &:    meta_bars.py $(PREMALLET) $(TOPICS_DOC) $(INDIVIDUAL_DOC_FIGS) | $(FIG_DIR) #INDIVIDUAL_DOC_FIGS just to force this to run after that, so we don't risk two incantations writing to the same file
#	python3 meta_bars.py   --force --prefix $(PREFIX) --output-dir $(FIG_DIR)   --mallet-metadata $(PREMALLET) --force $(TOPICS_COUNT) --topics

$(CLOUDS)/pp_topic_%_subjects.svg: $(CLOUDS)/topic_%_subjects.svg svg_postproc.py
	python3 svg_postproc.py --doc-labels $(TITLES)_short.json $<

$(CLOUDS)/pp_topic_%_docs.svg: svg_postproc.py $(TITLES)_short.json $(CLOUDS)/topic_%_docs.svg
	python3 svg_postproc.py --doc-labels $(TITLES)_short.json $(CLOUDS)/topic_$(*)_docs.svg

$(FIGS)/pp_%.svg:              svg_fixup.py    $(TITLES).json       $(FIGS)/%.svg
	python3 svg_fixup.py --doc-labels $(TITLES).json $(FIGS)/$(*).svg
	scour -i $(FIGS)/pp_$(*).svg -o $(FIGS)/ppp_$(*).svg
	mv $(FIGS)/ppp_$(*).svg $(FIGS)/pp_$(*).svg

$(FIGS)/wrapper_%.html: $(FIGS)/%.div wrapper_head.html wrapper_foot.html
	cat wrapper_head.html $< wrapper_foot.html > $@

$(FIG_DIR):
	mkdir $@

$(CLOUD_DIR):
	mkdir $@

$(WEB_DIR):
	mkdir $@
