This is most of the pipeline that turns OCR text from Wellcome Collection into data suited for HaToRI to digest, along with tools that digest it in other ways. It's initial development is of course heavily indebted to [HaToRI](https://eight1911.github.io/hansard/page/home/) and likely makes use of HaToRI code at times.

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
  * You might want to run split\_corpus.py to split it into smaller chunks e.g. ./split\_corpus.py example
  * And then run Ted Underwood's OCRNormalizer (https://github.com/tedunderwood/DataMunging.git) on data/corpora/example/normalized/example, e.g. 
    * cd DataMunging/OCRnormalizer
    * python3 OCRnormalizer.py
      * And then answer as follows:
        * Do you want the full spiel? n
        * Do you want to unpack .zip or .txt files? txt
        * Which option do you prefer? 1w
        * Path to the folder that contains source files? (correct answer for you, e.g. ../../wellcome\_pipe/data/corpora/example\_split/normalized/example\_split)
        * 1) Text only or 2) text-plus-wordcounts? 2
    * That last one is REALLY IMPORTANT -- if you select 1 you will be bitten by a bug that cuts off the processing after 200 files
* Install the dependencies for lemmastemma (e.g. in a virtualenv)
  * `pip install -r lemmastemma/requirements.txt`
* `make -j topics`

After which you need to pull them into hatori, which is a separate process. See the hatori repo.

## decorate\_subjects.py

This is for supplementing the `.tsv` file produced by `hatori_data.py`.

Because `works.json` is very large and not suited to random access queries, it relies on conversion of `works.json` into a very simple database (one table, two columns -- primary key, 'id', and 'col1' containing all of the json data for that id). The process to create this is roughly:
1) Install postgresql #the tools I used seem to work with postgres dialect, not mysql dialect
2) `sudo -u postgres createdb wellcome_works`
3) `psql wellcome_works`
4) `create table works(id char(8) primary key, col1 varchar(750000));` #longest line in works.json at time of writing is 497,346 chars. Step (9) below will add a space between fields, but I choose to hope that whatever expansions may happen will not add > 250,000 characters (500,000 empirically was not enough)
5) `pip install spyql` #ideally in some virtualenv. Will use this to convert `works.json` into SQL insert statements
6) `mkdir jsonl json sql` #in some directory where you have a copy of works.json
7) `(cd jsonl; cat ../works.json | split -l 500)` #split `works.json` into files of 500 lines each. Because it is a jsonl file, it is safe to split by line. spyql cannot cope with the whole of `works.json` in one go -- it probably can work with more than 500 lines at a time but I didn't do the experiment.
8) `for x in jsonl/*; do echo "jq -c -s '.' $x > json/`basename $x`"; done | parallel` #convert the jsonl files into json files (spyql does not seem to speak jsonl)
9) `for x in json/*; do echo "spyql -Jworks=$x -O table=works 'select .id as id, * from works to sql' > sql/`basename ${x}`.sql"; done | parallel` #create files of SQL insert statements
10) `for x in sql/*; do echo "psql wellcome_works < $x"; done | sh` #Check output of this for SQL errors (e.g. data column not big enough)

psql installation (steps 1 and 2) may look something like:
1) `sudo apt install postgresql`
2) `sudo -u postgres createdb wellcome_works`
3) `sudo -u postgres createuser $USER`
4) `sudo -u postgres psql wellcome_works`
4) `grant all privileges on database wellcome_works to bogden;` #if bogden is your username
5) `grant all on schema public to bogden;`

## works\_lookup.py

Looks up works (by identifier) in the database described under `decorate_subjects.py`, above. Dumps results as JSON to stdout or to files in a directory.
