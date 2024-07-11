#!/bin/bash
#example: ./browse_svg.sh 17xx_lemmatized_sorted_50
name="${1:?Must give a name to build from, such as 17xx_lemmatized_sorted_50}"
output="${2:-.}"
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
<table>
<tr><td>#</td><td>Topic Cloud</td><td>Subject Cloud</td><td>Doc Cloud</td></tr>
EOF
topic_count="${name##*_}"
topic_count=$((topic_count - 1))
for topic in `seq 0 ${topic_count}`; do
  echo "<td><a name='topic_${topic}'/>${topic}</td>"
  echo '<td style="border: 1px solid">'; cat clouds/${name}/topic_${topic}.svg; echo '</td>'
  echo '<td style="border: 1px solid">'; cat clouds/${name}/pp_topic_${topic}_subjects.svg; echo '</td>'
  echo '<td style="border: 1px solid">'; cat clouds/${name}/pp_topic_${topic}_docs.svg; echo '</td>'
  echo '</tr>'
done
echo '</table></body></html>'
} > "${output}/${name}/topics.html"
cp -l figures/"${name}"/pp_* "${output}/${name}"/figures/

#height: 510px; width: 510px; }
#style='width:10px'
