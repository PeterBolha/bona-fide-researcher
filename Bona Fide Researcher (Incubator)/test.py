import re

pattern = re.compile(r"^[^.]\.?$")

not_initial = "Mihaly"
initial = "M"
initial_period = "M."

if re.match(pattern, not_initial):
    print("not initial")

if re.match(pattern, initial):
    print("initial")

if re.match(pattern, initial_period):
    print("initial period")
