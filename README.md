# xfail


The (main) module **explain.py** can be run as follows:
```
python3 explain.py event event_logs
```
for explaining an `event` in from given `event_logs`.
It does so by coordinating the following components
* `parser` -> It parses the input `event_logs` and generates the file `logged_events.pl` containing their representation in Prolog
* `explainer` -> It loads the facts in the file `logged_events.pl` and runs the Prolog explainer (viz., `explain.pl`) on such facts to determine the possible root causes for the `event` being explained.
* `post_processor` -> It takes the root causes determined by `explainer` and beautifies (and sorts?) them to show them to the end user.
