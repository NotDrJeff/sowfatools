#TST-cli --time-col=0 --signal-col=1 <( awk '/^[0-9]/ {print $2 - 20000,$4}' turbineOutput/*/powerRotor )
TST-cli --time-col=0 --signal-col=1 <( awk '/^[0-9]/ {print $2, $4}' turbineOutput/*/powerRotor )
