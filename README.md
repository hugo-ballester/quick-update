# quick-update

Keep track of your work in a simple text file, generate reports from it (last week, currently open, etc.)

Some extra nice features:
  * quickly write updates of hierarchical tasks, easily including hyperlinks
  * report completed and open tasks, report elapsed time since beginning of a task


Alpha release, hugo@hugo-zaragoza.net

### Examples of Use

First a very simple example:

```
# sample1.txt

# 2020-10-06 
Project One:: Documentation:: working on chapter one
Project Two:: Infra:: Data Pipelne:: design doc completed
Project Two:: Infra:: AWS Set-up:: completed (.)
```
```
> python src/sample_update.txt -f update.txt open

================================================================================================================================================================
================================================================================================================================================================
================================================================================================================================================================
QuickUpdate v 0.3.0
________________________________________________________________________________________________________________________________________________________________

UPDATE FILE: sample_update.txt

________________________________________________________________________________________________________________________________________________________________
OPEN TASKS
    * Project One / Documentation   	: Working on chapter one. (2m)
    * Project Two / Infra / Data Pipelne	: Design doc completed. (2m)

________________________________________________________________________________________________________________________________________________________________
CLOSED TASKS
    * Project Two / Infra / AWS Set-up	: Completed .

================================================================================================================================================================
```
Another example using more features:
```
[XFP] Project-X:: First Proposal::
[11]  Management:: 1:1s:: POSFIX:(DONE): ORDER:zzz:

#2020-01-01
XFP:: discussed with Phoebe
XFP:: drew data flow diagrams
XFP:: Legal:: cleared with legal (DONE)
Project-X:: Recruiting:: contacted 20 canidates

#2020-01-02
# comment line (will be ignored)
Another Top Level Task:: shipped documentation SIM:https://blah.com (.)
11:: met with Rachel

#TODO write-up doc about a dog
#TODO think about new directions:
```
```
> python src/sample_update.txt -f update.txt week

================================================================================================================================================================
================================================================================================================================================================
================================================================================================================================================================
QuickUpdate v 0.3.0
________________________________________________________________________________________________________________________________________________________________

UPDATE FILE: sample_update.txt
WARNING: NOW is set to 2020-01-13 00:00:00

________________________________________________________________________________________________________________________________________________________________
Last Week #2: 2020 / 1 / 6-12

* Another Top Level Task : Shipped documentation [SIM](https://blah.com) .
* Project-X / First Proposal :
    * Discussed with Phoebe.
    * Drew data flow diagrams.
* Project-X / First Proposal / Legal : Cleared with legal.
* Project-X / Recruiting : Contacted 20 canidates.
* Management / 1:1s : Met with Rachel.


================================================================================================================================================================

> python src/sample_update.txt -f update.txt open

================================================================================================================================================================
================================================================================================================================================================
================================================================================================================================================================
QuickUpdate v 0.3.0
________________________________________________________________________________________________________________________________________________________________

UPDATE FILE: sample_update.txt
WARNING: NOW is set to 2020-01-13 00:00:00

________________________________________________________________________________________________________________________________________________________________
OPEN TASKS
    * Project-X / First Proposal    	: Drew data flow diagrams.
    * Project-X / Recruiting        	: Contacted 20 canidates.


================================================================================================================================================================


```

### UPDATES FILE FORMAT:
  * Dates should be indicated in a line: |#2020-01-01
  * (Dates should be incremental or decremental)
  * Updates are given in a line: |Your task name:: your sub task name:: your update
  * You can add or remove sub task levels at any line, QuickUpdate will keep track of all.
  * Update description will be formatted as follows: first letter is upper-cased, a period is added at the end if it does not have one.
  * A task is marked as done by adding '(DONE)' or '(.)' in its update. It can be reopened simply by adding a new update
  * You can define aliases for tasks as follows
    * ```Task name:: sub task name:: [YOUR_KEY] OPTIONAL_URL POSFIX:OPTIONAL_POSFIX: ::ORDER:your_prefix_string:```
    * afterwards you can use the alias instead of the task names: ```YOUR_KEY:: your update```
    * if you define a url, the task will be linked to URL in reports
    * if you define a posfix, it will be added at the end of every update for this key (useful for tasks that you want to mark always as DONE with every update)
    * if you define an order, task alphabetical order will prefix this string (e.g. use ::ORDER:zzz: to push to the bottom)

  * Lines starting with #TODO are stored and reported. Multilines todos can be done following lines with "#- "
  * Links of the form word:URL are converted to Markup's usual [word](url)



### TODO: 
- inherit parent task properties like order, done?