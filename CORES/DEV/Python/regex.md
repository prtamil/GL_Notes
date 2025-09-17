""" REGEX """

pattern = re.compile("pattern")
pattern.match  -> Searches only first of String returns match object
pattern.search  -> Searches anywhere in string  returns match object
pattern.findall -> find all accourences but returns pattern text
pattern.finditer -> find all accourences but returns generator with match object

Match object  methods
---------------------
group  ->  return string matched by RE
start  ->  Starting position of the Match
end   ->   Ending position of the match
span  ->   Tuple of (start, end)
