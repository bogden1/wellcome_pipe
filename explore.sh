#!/bin/bash
#example: ./browse_svg.sh 17xx_lemmatized_sorted_50
name="${1:?Must give a name to build from, such as 17xx_lemmatized_sorted_50}"
input="${2:-.}"
output="${3:-.}"
mkdir -p "${output}/${name}/figures"
{
cat <<EOF
<html>
<head>
<style>
  table { border-spacing: 75px; }
  td { font-size: 20px; font-weight: bold; text-align: center; vertical-align: top }
</style>
</head>
<body>
<p><a href="../index.html">Home</a></p>
<table>
<tr><td>#</td><td>Topic Cloud</td><td>Subject Cloud</td><td>Doc Cloud</td></tr>
EOF
topic_count="${name##*_}"
topic_count=$((topic_count - 1))
for topic in `seq 0 ${topic_count}`; do
  cat <<EOF
<td>
  <p><a name='topic_${topic}'/></p>
  <p><a href='#topic_${topic}'>${topic}</a></p>
  <p><a href='figures/wrapper_topic_${topic}_topdocs.html'>Top 10 docs</a></p>
  <p><a href='figures/wrapper_topic_${topic}_docs40.html'>&gt; 40% docs</a></p>
</td>
EOF
  echo '<td style="border: 1px solid">'; cat ${input}/clouds/${name}/topic_${topic}.svg; echo '</td>'
  echo '<td style="border: 1px solid">'; cat ${input}/clouds/${name}/pp_topic_${topic}_subjects.svg; echo '</td>'
  echo '<td style="border: 1px solid">'; cat ${input}/clouds/${name}/pp_topic_${topic}_docs.svg; echo '</td>'
  echo '</tr>'
done
echo '</table></body></html>'
} > "${output}/${name}/topics.html"

cp -l "${input}"/figures/"${name}"/wrapper*.html "${output}/${name}/figures/"
