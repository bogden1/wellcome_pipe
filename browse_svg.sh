#!/bin/bash
#example: ./browse_svg.sh clouds/17xx_lemmatized_sorted_50
dirname="$1"
shift
for thing in subjects docs; do
  {
    echo '<html><body>'
    topic=0
    for svg in ${dirname}/pp_*_${thing}.svg; do
      echo "<h1>Topic ${topic}</h1>"
      cat "${svg}"
      echo '<br/><br/>'
      topic=$((topic+1))
    done
    echo '</body></html>'
  } > ${dirname}/${thing}.html
done
