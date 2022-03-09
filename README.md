# Lishgreek
A Greeklish to Greek converter, seamlessly supporting a variety of Greeklish "dialects".

This implementation follows an approach similar
to "All Greek to me! An automatic Greeklish to Greek transliteration system"
by Chalamandaris et al. 2006

The greeklish word, following a number of possible Greeklish conventions,
is tokenized and transformed into a pseudophonetic version (called uglish -
"unified greeklish"). This pseudophonetic version is then used as a key to a
uglish/Greek dictionary to find a number of possible Greek equivalences.

Simple orthographic and probability rules are applied to select the most probable
Greek equivalent word.

# Credits

uglish-dict.json is derived from "Hermit Dave" word list for Greek
available here: https://github.com/hermitdave/FrequencyWords/tree/master/content/2018/el
And it is redistributable under a CC-BY-SA-4.0 license.
