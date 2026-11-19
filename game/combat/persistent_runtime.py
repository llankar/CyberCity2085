"""One Godot process owned by the application, never started by mission submission."""
from __future__ import annotations
import atexit
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from .session_protocol import atomic_json


class CombatRuntime:
    def __init__(self, *, project_dir=Path('godot/combat_missions_ui'), directory=Path('runtime/godot_runtime'), executable=None, headless=False):
        self.project_dir=Path(project_dir).resolve()
        self._base_directory=Path(directory).resolve()
        self.directory=self._base_directory/uuid4().hex
        self.runtime_id=self.directory.name
        self.executable=executable
        self.headless=headless
        self.process=None
        self.hwnd=None
        self.owner_hwnd=None
        self.error=''
        self._sequence=0
        self._closed=False
        self.active_session=None
        atexit.register(self.close)

    def start(self, viewport=(1280,720)):
        """Called at application startup or an explicit repair, never by submit()."""
        if self.process is not None and self.process.poll() is None:return True
        if self.process is not None or self._closed:
            self.directory=self._base_directory/uuid4().hex
            self.runtime_id=self.directory.name
            self.process=None;self.hwnd=None;self.active_session=None
            if hasattr(self,"_log"):self._log.close()
        from .godot_bridge import find_godot_executable,copy_audio_assets
        executable=self.executable or find_godot_executable()
        if not executable:
            self.error='Godot executable unavailable at application startup'
            return False
        try:
            self.directory.mkdir(parents=True,exist_ok=True)
            copy_audio_assets()
        except OSError as exc:
            self.error=f"Godot startup preparation failed: {exc}"
            return False
        command=[executable,'--path',str(self.project_dir),'--position','-32000,-32000','--borderless',
            '--resolution',f'{viewport[0]}x{viewport[1]}','res://scenes/runtime_host.tscn']
        if self.headless:command+=['--headless','--audio-driver','Dummy']
        command+=['--','--runtime-dir',str(self.directory),'--runtime-id',self.runtime_id,'--owner-pid',str(os.getpid()),'--asset-root',str(Path.cwd().resolve())]
        kwargs={}
        if sys.platform=='win32':
            startup=subprocess.STARTUPINFO()
            startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow=0
            kwargs['startupinfo']=startup
        try:
            self._log=(self.directory/'godot.log').open('a',encoding='utf-8')
            self.process=subprocess.Popen(command,stdout=self._log,stderr=subprocess.STDOUT,**kwargs)
        except OSError as exc:
            self.error=str(exc)
            if hasattr(self,'_log'):self._log.close()
            return False
        self.error=''
        self._closed=False
        self.tick(0)
        return True

    def status(self):
        if self.process is None or self.process.poll() is not None:return {'state':'stopped','message':self.error}
        try:data=json.loads((self.directory/'status.json').read_text(encoding='utf-8'))
        except (OSError,ValueError):return {'state':'booting'}
        if isinstance(data,dict) and data.get('protocol_version')==2 and data.get('runtime_id')==self.runtime_id:return data
        return {'state':'booting'}

    def tick(self, _delta=0):
        if self._closed or self.process is None or self.process.poll() is not None:return
        if sys.platform=='win32':
            from .win32_embed import get_process_hwnd,get_current_process_hwnd,attach_owned_window,hide_window
            if self.hwnd is None:self.hwnd=get_process_hwnd(self.process.pid,include_hidden=True)
            if self.owner_hwnd is None:self.owner_hwnd=get_current_process_hwnd()
            if self.hwnd and self.owner_hwnd:attach_owned_window(self.hwnd,self.owner_hwnd)
            if self.hwnd and self.status().get('state') in {'booting','idle','error'}:hide_window(self.hwnd)
        self._sequence+=1
        try:atomic_json(self.directory/'heartbeat.json',dict(runtime_id=self.runtime_id,sequence=self._sequence))
        except OSError as exc:self.error=f'Godot heartbeat unavailable: {exc}'

    def _command(self,event,**fields):
        if self.process is None or self.process.poll() is not None:
            raise ValueError('Godot was not started with the application or has stopped; use explicit retry/repair')
        atomic_json(self.directory/'command.json',dict(protocol_version=2,runtime_id=self.runtime_id,
            command_id=uuid4().hex,event=event,**fields))

    def submit(self,handoff_path,session_id,viewport,position=None):
        self._command('mission',handoff_path=str(Path(handoff_path).resolve()),session_id=session_id,
            viewport=list(viewport),position=list(position) if position is not None else None)
        self.active_session=session_id

    def is_idle(self,session_id):
        status=self.status()
        return status.get('state')=='idle' and status.get('session_id')==session_id

    def park(self,session_id):
        if self.is_idle(session_id):return
        if self.process is not None and self.process.poll() is None:
            self._command('park',session_id=session_id)

    def close(self):
        if self._closed:return
        try:
            if self.process is not None and self.process.poll() is None:
                self._command('shutdown')
                try:self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.terminate()
                    try:self.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=1)
        except (OSError,ValueError):pass
        finally:
            self._closed=True
            if hasattr(self,'_log'):self._log.close()


def runtime_for_window(window):
    return vars(window).get('combat_runtime') if window is not None else None
