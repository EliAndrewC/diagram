# t373: the hook payloads, one JSON file a case, under payloads/. All paths are in the throwaway world.
import json,os,sys
S=os.path.dirname(os.path.abspath(__file__)); C=S+'/w/diagram/.clones/diagram-backlog'; P=S+'/payloads'; os.makedirs(P,exist_ok=True)
def line(path,n):
    return open(C+'/'+path).read().split('\n')[n]
def edit(path,n):
    old=line(path,n); return {'file_path':C+'/'+path,'old_string':old,'new_string':old+' x'}
tools={
 'edit-doc':('Edit',edit('docs/usage.md',10)),
 'edit-rust':('Edit',edit('rust/gate/src/main.rs',0)),
 'edit-plan':('Edit',edit('specs/451-time-retro-and-efficiency/plan.md',4)),
 'write-new':('Write',{'file_path':C+'/dev/measurements/2026-11-26/edit-hook/t373-new.txt','content':'one line\n'}),
 'bash-true':('Bash',{'command':'true'}),
 'read':('Read',{'file_path':C+'/docs/usage.md'}),
 'grep':('Grep',{'pattern':'declared scale','path':C+'/docs'}),
 'agent':('Agent',{'description':'read one file','prompt':'SESSION_MODEL: reads one file\nRead docs/usage.md and say its first heading.','subagent_type':'general-purpose'}),
}
sessions={'sub':{'session_id':'t373-sess-0001','transcript_path':S+'/home/.claude/projects/-diagram/t373-sess-0001.jsonl','agent_id':'a5d7450210f807487','agent_type':'general-purpose'},  # a builder of that session: its agent id, its meta file copied
          'none':{'session_id':'t373-none-0000'},   # T365's form: an id no claim map holds, no transcript
          'sess':{'session_id':'t373-sess-0001','transcript_path':S+'/home/.claude/projects/-diagram/t373-sess-0001.jsonl'},  # 274 MB, the coordinating session's own
          'half':{'session_id':'t373-sess-0002','transcript_path':S+'/home/.claude/projects/-diagram/t373-sess-0002.jsonl'},  # its first 137 MB
          'tenth':{'session_id':'t373-sess-0003','transcript_path':S+'/home/.claude/projects/-diagram/t373-sess-0003.jsonl'}}  # its first 27 MB
sessions['wt']=dict(sessions['sub'])  # a builder in a pool worktree of the clone (a tree whose .git is a file)
WT=S+'/w/diagram/.clones/diagram-backlog-t270'
for sk,sv in sessions.items():
  for tk,(tool,ti) in tools.items():
    for ev in ('PreToolUse','PostToolUse'):
      d=dict(sv); d.update(cwd=C,hook_event_name=ev,tool_name=tool,tool_input=ti,tool_use_id='toolu_t373'+tk.replace('-',''),permission_mode='default')
      if ev=='PostToolUse':
        d['tool_response']={'filePath':ti.get('file_path',''),'oldString':ti.get('old_string',''),'newString':ti.get('new_string',''),'structuredPatch':[],'userModified':False,'replaceAll':False} if tool=='Edit' else ({'type':'create','filePath':ti['file_path'],'content':ti['content'],'structuredPatch':[]} if tool=='Write' else {'stdout':'','stderr':'','interrupted':False})
      text=json.dumps(d)
      if sk=='wt': text=text.replace(C+'/',WT+'/').replace('"cwd": "'+C+'"','"cwd": "'+WT+'"')
      open(f'{P}/{sk}.{tk}.{ev}.json','w').write(text)
print(len(os.listdir(P)),'payloads')
