# quick-update

[<img src="https://user-images.githubusercontent.com/382557/168976483-6698150f-beba-4072-a790-aed10224b0d7.png" width="50%">](https://www.youtube.com/watch?v=Hc79sDi3f0U "QuickUpdate")

Keep track of your work in a simple text file, generate reports from it (last week, currently open, etc.)

Some nice features:
  * quickly write updates of hierarchical tasks, easily including hyperlinks
  * report completed and open tasks, report elapsed time since beginning of a task
  * reports automatically copy its content to the clipboard in MarkDown format


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
> alias qu="python src/sample_update.txt -f update.txt"
> qu open

_________________________________________________________________________________

OPEN TASKS
      ◯ Project One / Documentation   	: Working on chapter one. (13m)
      ◯ Project Two / Infra / Data Pipelne	: Design doc completed. (13m)

_________________________________________________________________________________
```

Another example using more features:
```
[XFP] Project-X:: First Proposal::
[11]  Management:: 1:1s:: POSFIX<(DONE)> ORDER<zzz>

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
>qu open
_________________________________________________________________________________
OPEN TASKS
      ◯ Project-X / First Proposal    	: Drew data flow diagrams. (22m)
      ◯ Project-X / Recruiting        	: Contacted 20 canidates. (22m)
_________________________________________________________________________________

>qu --now 2020-01-01 thisweek
_________________________________________________________________________________

This Week #1: 2020 / 1 / 30-5
  ◯ Another Top Level Task :
    ◯ Shipped documentation [SIM](https://blah.com).  ✓
  ◯ Project-X / First Proposal :
    ◯ Discussed with Phoebe.
    ◯ Drew data flow diagrams.
  ◯ Project-X / First Proposal / Legal :
    ◯ Cleared with legal.  ✓
  ◯ Project-X / Recruiting :
    ◯ Contacted 20 canidates.
  ◯ Management / 1:1s :
    ◯ Met with Rachel.  ✓
_________________________________________________________________________________

>qu --help
usage: quick_update.py [-h] -f UPDATE_FILE [--now NOW] [--task TASK] commands [commands ...]

QuickUpdate v1.1: https://github.com/hugozaragoza/quick-update

positional arguments:
  commands              log, open, standby, closed, y[esterday], today, thisweek, [last]week, <k>weeks, span <date-start> <date-end>, tasks, todo

optional arguments:
  -h, --help            show this help message and exit
  -f UPDATE_FILE, --update_file UPDATE_FILE
                        Update file
  --now NOW             Use a different date for today (for reports relative to today). Use format %Y-%m-%d
  --task TASK           Filter to only this task (or task alias)
```

### INSTALLATION and USAGE:
This is how I install locally:
```php
git clone https://github.com/hugozaragoza/quick-update.git
cd quick-update
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

And I setup these aliases in my .zshenv:
```bash
update_file=path_to_my_update_file
qu='python src/quick_update.py -f $update_file'
```

Usage is then:
```bash
qu week
```

(For MacOS:) Also I typically setup an iTerm2 profile (with a shortcut ^⌘U) starting on the directory where I have installed quickupdate, with the "send text at start:" as 'activate; PROMPT=">"; qu yesterday'. This way I can get look at muy updates with a keystroke.


### FILE FORMAT:
  * Being an update block with a date heading: `# 2020-01-01`
  * Give an update in each line, prefixed by the task name: `Your task name:: your sub task name:: your update`
  * You can add or remove sub task levels at any line.
  * A task is marked as "done" by adding '(DONE)' or '(.)' in its update. It can be reopened simply by adding a new update
  * A task is marked as "standby" by adding '(STANDBY)' or '(o)' in its update. It can be reopened simply by adding a new update
  * You can define aliases for tasks. Afterwards you can use the alias instead of the task names: ```ALIAS:: your update``` 
    * An alias line begins with `[ALIAS] ` followed by the full task (or subtask) name.
    * You can add an optional URL to be linked with every update for this (sub)task.
    * You can add an optional posfix and order prefix (prefix to be used when sorting alphabetically)
    * Example: `[ALIAS] Task name:: sub task name:: OPTIONAL_URL POSFIX<optional_posfix> ORDER<optional_order_prefix_string>`
    * if you define a posfix, it will be added at the end of every update for this key (useful for tasks that you want to mark always as DONE with every update)
    * if you define an order, task alphabetical order will prefix this string (e.g. use ::ORDER:zzz: to push to the bottom)
  * Update description will be formatted as follows: 
    * first letter is upper-cased, a period is added at the end if it does not have one.
    * links of the form word:URL are converted to Markup's usual [word](url)
  * Lines starting with #TODO are stored and reported.
  

### MISC:

Tip: I use this crontab line on my MacOS to reming myself to update frequently on what I am working on:
```
0 9-19/3 * * * open ~/Desktop/updates.tsv -a 'Sublime Text'
```

### TODO: 
- inherit parent task properties like order, done?
