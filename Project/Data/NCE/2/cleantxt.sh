 #!/bin/bash
for i in $( ls *.TXT); do
    echo $i
    perl -nle 'print if m{^[[:ascii:]]+$}' $i > "T"$i
done
        