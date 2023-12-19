# quick-update

[<img src="https://user-images.githubusercontent.com/382557/168976483-6698150f-beba-4072-a790-aed10224b0d7.png" width="50%">](https://youtu.be/oWZyX_Ee2Tc "QuickUpdate")


Keep track of your work in a simple text file, generate reports from it (last week, currently open, etc.)

Some nice features:
  * arbitrary number of tasks/projects/subprojects hierarchical levels
  * quickly write updates of hierarchical tasks, easily including hyperlinks
  * report completed and open tasks, report elapsed time since beginning of a task
  * reports automatically copy its content to the clipboard in MarkDown format
  * write scrap text anywhere


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

### scrap block
start a scrap block with three or more #,
write anything here, won't be parsed until a new ###+ line is found
 
# blah
 not parsed... 
###

#2020-01-01
XFP: discussed with Phoebe
XFP: drew data flow diagrams
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
  commands              open, pending, standby, closed, y[esterday], today, thisweek, [last]week, <k>weeks, span <date-start> <date-end>, tasks, todo

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

### CONCEPTS

  * A "task" is synonym of a project, subproject, subsubproject, it's all just a tree of tasks, you decide what to call each level. 
  * You can keep adding updates to a task, it becomes the task "log" or history. 
  * You can mark a task either "open", "closed", or in "standby". (Any tasks having an update with a pending tag will be in "pending" mode.) 
  * You tag updates if you want to group them or find them easily.

### FILE FORMAT:
  * Being an update block with a date heading: `# 2020-01-01`
  * Give an update in each line, prefixed by the task name: `Your task name:: your sub task name:: your update`
  * Tasks can have an arbitrary number of "hierarchical levels", just separate them by `::`. The last `::` marks the end of the task name and the beginning of the udpate. For example `Main Project::Sub Project::Task::Sub Task:: your update to this sub task`
  * A task is marked as "closed" by adding '(CLOSED)' or '(.)' at the end of its update string. It can be reopened simply by adding a new update.
  * A task is marked as "standby" by adding '(STANDBY)' or '(,)' at the end of its update string. It can be reopened simply by adding a new update.
  * A task is marked as "pending" if it contains an update with '(!)'.
  * You can define aliases for tasks. Afterward you can use the alias instead of the task names: ```MyAlias: your update``` 
    * An alias definition line begins with the alias name in square bracket followed by the full task (or subtask) name. For example: `[MyAlias] Cooking:: Bake a Cake::` 
    * An alias definition can be decorated with:
      * a URL to be linked with every update for this (sub)task.
      * a posfix string (to be added to every update of this task)
      * an order prefix (prefix to be used when sorting alphabetically)
      * Example: `[MyAlias] Cooking:: Bake a Cake:: http://bake_a_cake.com POSFIX<(DONE)> ORDER<zzz>`    
  * Any lines starting with #TODO are stored in batch and can be reported.
  

### MISC:

Tip: I use this crontab line on my MacOS to reming myself to update frequently on what I am working on:
```
0 9-19/3 * * * open ~/Desktop/updates.tsv -a 'Sublime Text'
```

### TODO: 
- inherit parent task properties like order, done?
