This is most of the pipeline that turns OCR text from Wellcome Collection into data suited for HaToRI to digest.

The missing bit is the part where you build your own subcorpus, which is still a manual process, but might start
with something like e.g.:

```
cat works.json | jq -c 'select(((.languages | length) == 1) and (.languages[].id=="eng"))' > data/corpora/works_with_only_english_as_language/normalized/english_only.jsonl
```

`works.json` being the JSON form of Wellcome's catalogue data, available at TBD.

Otherwise, the process is:

* Put work.json, or some lines from it, in inputs/
  * "some lines from it" might have come from a jq trick like the one above
  * A very small example is provided
* ./quaff.py to get the text from Wellcome
  * This will collect text from Wellcome for each file in inputs/
  * Doing this for the whole of `works.json` will take some time
* Do any post-processing on what comes back to get the sub-corpus that you want:
  * In the simplest case, where you only collected what you actually wanted, this could be just:
  * `mkdir -p data/corpora/example/normalized; cp -rl data/text/example/ data/corpora/example/normalized/example; cp -l data/inputs/example.json data/corpora/example/normalized/example.jsonl`
  * And then run Ted Underwood's OCRNormalizer (https://github.com/tedunderwood/DataMunging.git) on data/corpora/example/normalized/example
* Install the dependencies for lemmastemma (e.g. in a virtualenv)
  * `pip install -r lemmastemma/requirements.txt`
* `make -j topics`

After which you need to pull them into hatori, which is a separate process. See the hatori repo.
