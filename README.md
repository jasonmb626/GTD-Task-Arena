# GTD-Task-Arena
Just one more attempt to implement David Allen's Getting Things Done as FOSS.

## Ideas/notes
This is a WIP for sure, but here are some notes

Concept based on mixing Taskwarrior and Timewarrior more than the hooks allow. Saving to text files would be awesome but even Taskwarrior gave up on that idea by V3 so probably plan to use a sqlite database. Want all actions to be able to take place via command-line calls, but also build a tui like VIT. 

- Tags should be fairly free-form but want a way to enforce all tasks have something like a "billing" tag set, even if set to N/A.
- Similarly it should be able to set context tags easily.
- Maintain separate arenas, work, home etc
- Arena is really just setting a default project base as projects are hierarchal. So /personal/house/lighting with an arena set to personal would only list projects 
with personal at the root, and it would just show house/lighting as project name. Similarly /personal/house could be set as the arena and then lighting would be the full name of the project listed. New tasks also default to project base of whatever is set for arena, so prepend a forward slash to change to set an absolute rather than relative base
- Have option to soft schedule tasks or hard schedule taks. Soft schedule probably displays a little grayed out
- Task manager feature to go through all unscheduled time slots and list all next actions with efforts fitting time slot, in reverse order?
- Task/tag table should allow order, so when filtering by tag tasks show in a particular order
- Filter for things that must get done today
