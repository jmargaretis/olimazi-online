"""Standard-library local status/start server for the Olimazi Launchpad."""
from __future__ import annotations
import hashlib, html, http.client, importlib.util, json, os, re, socket, subprocess, sys, threading, time
from datetime import date, datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

HOST, PORT, TIMEOUT = "127.0.0.1", 8643, 1.5
ROOT = Path(__file__).resolve().parent
HANDOFF_PATH = Path(r"C:\Users\jmarg\OneDrive\Documents\Claude OS\inbox\handoff.md")
REVIEW_PATH = Path(r"C:\Users\jmarg\OneDrive\Documents\Claude OS\Review.md")
DROP_PATHS = [Path(r"C:\Users\jmarg\My Drive\Olimazi Drop")]
APPLICATIONS_PATH = Path(r"C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\resume-tailoring\applications\applications-tracker.md")
SNAPSHOT_PATH, CACHE_SECONDS = ROOT / "mc-state-snapshot.json", 10
CACHE, CACHE_LOCK = {}, threading.Lock()
TRACKER_DIR = Path(r"C:\Users\jmarg\work\olimazi-tracker\fixtures\sample-property")
SERVICES = {"site": ("Site",8399,"/"), "image-picker": ("Image picker",8642,"/picker.html"), "mission-control": ("Mission Control",8643,"/api/health"), "tracker-sample": ("Tracker sample",8744,"/SchE_Dashboard.html")}
PAGES = [("SchE_Dashboard","SchE_Dashboard.html","Sample dashboard"),("SchE_Management","SchE_Management.html","Management page"),("SchE_Organizer","SchE_Organizer.html","Organizer"),("SchE_Reconciliation","SchE_Reconciliation.md","Reconciliation report"),("MatchProposals","MatchProposals.md","Receipt match proposals")]
SITE_REPO = Path(r"C:\Users\jmarg\work\olimazi-online")
HERO_CONTENT = SITE_REPO / "content" / "home-hero.md"
HERO_RENDERER, HERO_TARGET = SITE_REPO / "tools" / "render_hero.py", SITE_REPO / "index.html"
HERO_HASH = SITE_REPO / "tools" / ".hero-content-hash"
HERO_PREVIEW_URL, HERO_LIVE_URL = "http://localhost:8399/index.preview.html", "https://olimazi.online/"
HERO_START, HERO_END = "<!-- content:home-hero:start -->", "<!-- content:home-hero:end -->"
SECTION_RENDERER = SITE_REPO / "tools" / "render_section.py"
COLLECTION_RENDERER = SITE_REPO / "tools" / "render_collection.py"
SECTION_CONTENT_ROOT = SITE_REPO / "content"
SITE_SECTIONS = ("hero-spec","main-work","method","mind","library","contact","story","dialogs")

def read_text(path):
    return path.read_text(encoding="utf-8-sig")

def sections(text):
    matches=list(re.finditer(r"(?m)^##\s+(.+?)\s*$",text)); result={}
    for index,match in enumerate(matches):
        result[match.group(1).strip().lower()]=text[match.end():matches[index+1].start() if index+1<len(matches) else len(text)].strip()
    return result

def parse_handoff(path=HANDOFF_PATH):
    text=read_text(path); parts=sections(text); todos=next((v for k,v in parts.items() if k.startswith("open to-dos")),None)
    prompt=next((v for k,v in parts.items() if k.startswith("exact next prompt to run")),None)
    action=None
    if todos is not None:
        for match in re.finditer(r"(?ms)^\s*\d+[.)]\s+(.*?)(?=^\s*\d+[.)]\s+|\Z)",todos):
            item=" ".join(match.group(1).split())
            if not re.search(r"(?i)(?:^|\W)DONE(?:\W|$)",item): action=item; break
    elif prompt:
        action=" ".join(prompt.strip().strip('"').split())
    return {"next_action":action,"exact_next_prompt":" ".join(prompt.strip().strip('"').split()) if prompt else None,"source_mtime":path.stat().st_mtime}

def parse_review(path=REVIEW_PATH):
    text=read_text(path); headings=list(re.finditer(r"(?m)^##\s+(\d{4}-\d{2}-\d{2})\b([^\n]*)$",text))
    count=items=0; review_flag=False
    for index,heading in enumerate(headings):
        block=text[heading.start():headings[index+1].start() if index+1<len(headings) else len(text)]
        status_lines="\n".join(line for line in block.splitlines() if re.match(r"(?i)^\s*(?:status\s*:|##)",line))
        terminal=bool(re.search(r"(?i)\b(?:DONE|APPLIED|RESOLVED)\b",status_lines))
        unresolved=[line for line in block.splitlines() if re.match(r"^\s*-\s*\[ \]",line) and re.search(r"(?i)\bJohn(?:'s)?\b|AWAITING JOHN",line)]
        awaiting=bool(re.search(r"(?i)\bAWAITING JOHN\b",status_lines)) or bool(unresolved)
        historical=bool(re.search(r"(?i)\b(?:carried|historical)\b.*\bAWAITING JOHN\b",status_lines))
        if awaiting and not terminal and not historical: count+=1; items+=len(unresolved)
        elif re.search(r"(?i)\bAWAITING JOHN\b",block) and not (awaiting or terminal): review_flag=True
    return {"awaiting_john_blocks":count,"unresolved_items":items,"review_this_count":review_flag,"source_mtime":path.stat().st_mtime}

def parse_drop(paths=DROP_PATHS):
    path=next((item for item in paths if item.is_dir()),None)
    if path is None: raise FileNotFoundError("Olimazi Drop is unavailable")
    pending=0
    for item in path.iterdir():
        if not item.is_file(): continue
        name=item.name; lower=name.lower()
        try: hidden=bool(item.stat().st_file_attributes & 0x6) if os.name=="nt" else name.startswith(".")
        except (AttributeError,OSError): hidden=name.startswith(".")
        if hidden or name.startswith((".","~")) or lower=="desktop.ini" or lower.endswith((".tmp",".gdoc")): continue
        pending+=1
    return {"status":"AVAILABLE","pending":pending,"resolved_path":str(path),"source_mtime":path.stat().st_mtime}

def parse_date(cell, today):
    matches=re.findall(r"(?<!\d)(?:(\d{4})-)?(\d{1,2})-(\d{1,2})(?!\d)",cell)
    if not matches: return None
    year,month,day=matches[-1]; return date(int(year) if year else today.year,int(month),int(day))

def parse_applications(path=APPLICATIONS_PATH, today=None):
    today=today or date.today(); lines=read_text(path).splitlines(); table_start=None
    for index,line in enumerate(lines):
        headers=[cell.strip().lower() for cell in line.strip().strip("|").split("|")]
        if "status" in headers and "follow-up" in headers: table_start=index; break
    if table_start is None: raise ValueError("applications table headers not found")
    headers=[cell.strip().lower() for cell in lines[table_start].strip().strip("|").split("|")]
    allowed=("drafting","applied","screening","interview","offer","closed"); counts={key:0 for key in allowed}; rows=[]; warnings=[]
    for number,line in enumerate(lines[table_start+2:],table_start+3):
        if not line.strip().startswith("|"): continue
        cells=[cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells)!=len(headers): warnings.append(f"Row {number}: expected {len(headers)} columns, found {len(cells)}"); continue
        row=dict(zip(headers,cells)); full=row["status"]; token=(re.match(r"[A-Za-z]+",full) or [""])[0].lower()
        if token not in allowed: warnings.append(f"Row {number}: unrecognized status {full!r}"); continue
        follow=None
        try: follow=parse_date(row["follow-up"],today)
        except ValueError: warnings.append(f"Row {number}: malformed follow-up date {row['follow-up']!r}")
        counts[token]+=1; rows.append({"status":token,"status_full":full,"follow_up":follow.isoformat() if follow else None})
    active=sum(counts[key] for key in ("drafting","applied","screening","interview")); dates=[date.fromisoformat(row["follow_up"]) for row in rows if row["follow_up"]]
    upcoming=[value for value in dates if value>=today]; overdue=sorted(value.isoformat() for value in dates if value<today)
    return {"counts":counts,"active_total":active,"nearest_follow_up":min(upcoming).isoformat() if upcoming else None,"overdue_follow_ups":overdue,"rows":rows,"warnings":warnings,"source_mtime":path.stat().st_mtime}

READERS={"handoff":parse_handoff,"review":parse_review,"drop":parse_drop,"applications":parse_applications}

def load_snapshot():
    try:
        data=json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")); return data if isinstance(data,dict) else {}
    except (OSError,json.JSONDecodeError): return {}

def save_snapshot(snapshot):
    temporary=SNAPSHOT_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(snapshot,indent=2),encoding="utf-8"); os.replace(temporary,SNAPSHOT_PATH)

def widget_state(name, now):
    with CACHE_LOCK:
        cached=CACHE.get(name)
        if cached and now-cached[0]<CACHE_SECONDS: return cached[1]
    try:
        value=READERS[name](); read_at=datetime.now().astimezone().isoformat(); result={"status":"ok","stale":False,"read_at":read_at,"value":value}
        with CACHE_LOCK:
            snapshot=load_snapshot(); snapshot[name]={"read_at":read_at,"value":value}; save_snapshot(snapshot); CACHE[name]=(now,result)
        return result
    except Exception as error:
        stale=load_snapshot().get(name); result={"status":"error","stale":bool(stale),"error":str(error)}
        if stale: result.update(stale)
        with CACHE_LOCK: CACHE[name]=(now,result)
        return result

def state_payload():
    now=time.monotonic(); return {name:widget_state(name,now) for name in READERS}

def command_for(s):
    return {"site":[sys.executable,"-m","http.server","8399","--bind",HOST,"--directory",r"C:\Users\jmarg\work\olimazi-online"], "image-picker":[sys.executable,"-m","http.server","8642","--bind",HOST,"--directory",r"C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-landing\image-bucket"], "tracker-sample":[sys.executable,"-m","http.server","8744","--bind",HOST,"--directory",str(TRACKER_DIR)]}.get(s)

def check_service(s):
    _, port, path = SERVICES[s]; connection = http.client.HTTPConnection(HOST,port,timeout=TIMEOUT)
    try:
        connection.request("GET",path); response=connection.getresponse(); body=response.read(4096)
        if s == "site": return "running"
        if response.status != 200: return "wrong-service"
        if s == "mission-control":
            try: health=json.loads(body)
            except (UnicodeDecodeError,json.JSONDecodeError): return "wrong-service"
            if health != {"status":"ok","service":"mission-control"}: return "wrong-service"
        return "running"
    except ConnectionRefusedError: return "stopped"
    except (socket.timeout,TimeoutError): return "unresponsive"
    except (OSError,http.client.HTTPException): return "unknown"
    finally: connection.close()

def manifest():
    return [{"stem":s,"filename":f,"label":l,"url":f"http://localhost:8744/{f}"} for s,f,l in PAGES if (TRACKER_DIR/f).is_file()]

def start_service(s):
    if s not in SERVICES: return 404,{"error":"unknown service"}
    if check_service(s)=="running": return 200,{"id":s,"status":"running","started":False}
    command=command_for(s)
    if command is None: return 409,{"error":"service cannot be started here"}
    flags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS if os.name=="nt" else 0
    try: subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True,creationflags=flags)
    except OSError: return 500,{"error":"service failed to start"}
    return 202,{"id":s,"status":"starting","started":True}

def hero_values():
    text=HERO_CONTENT.read_text(encoding="utf-8-sig"); values={}
    headings=list(re.finditer(r"(?m)^# ([^\r\n]+)[ \t]*\r?$",text))
    for index,match in enumerate(headings):
        end=headings[index+1].start() if index+1<len(headings) else len(text)
        values[match.group(1).strip()]=text[match.end():end].strip()
    required=("Kicker","Headline Lead","Headline Accent","Sub","CTA Label","CTA Href")
    if any(not values.get(field) for field in required): raise ValueError("hero content has missing or empty fields")
    return values

def expected_hero(values,newline):
    escaped={key:html.escape(value,quote=True) for key,value in values.items()}
    lines=(f'          <div class="hero-kicker">{escaped["Kicker"]}</div>',f'          <h1>{escaped["Headline Lead"]} <span class="accent">{escaped["Headline Accent"]}</span></h1>',f'          <p class="hero-sub">{escaped["Sub"]}</p>',f'          <a class="btn" href="{escaped["CTA Href"]}">{escaped["CTA Label"]} <span class="arr" aria-hidden="true">→</span></a>')
    return newline+newline.join(lines)+newline+"          "

def live_has_sub(sub):
    request=Request(HERO_LIVE_URL,headers={"User-Agent":"Olimazi-Mission-Control/1"})
    with urlopen(request,timeout=8) as response:
        if response.status != 200: return False,f"live site returned HTTP {response.status}"
        body=response.read().decode("utf-8",errors="replace")
    present=html.escape(sub,quote=True) in body
    return present,None if present else "live site does not contain the current hero Sub"

def hero_status():
    try:
        content_bytes=HERO_CONTENT.read_bytes(); digest=hashlib.sha256(content_bytes).hexdigest()
        built=HERO_HASH.read_text(encoding="utf-8").strip(); target=HERO_TARGET.read_text(encoding="utf-8")
        payload={"content_mtime":HERO_CONTENT.stat().st_mtime,"last_build_time":HERO_HASH.stat().st_mtime,"content_hash":digest,"built_hash":built}
        if target.count(HERO_START)!=1 or target.count(HERO_END)!=1 or target.index(HERO_START)>=target.index(HERO_END):
            return {**payload,"status":"DRIFT","reason":"hero markers are missing, duplicated, or out of order"}
        if digest != built: return {**payload,"status":"EDITED"}
        start=target.index(HERO_START)+len(HERO_START); end=target.index(HERO_END)
        newline="\r\n" if "\r\n" in target[start:end] else "\n"
        values=hero_values()
        if target[start:end] != expected_hero(values,newline):
            return {**payload,"status":"DRIFT","reason":"index.html hero region does not match the renderer output"}
        deployed,reason=live_has_sub(values["Sub"])
        return {**payload,"status":"DEPLOYED" if deployed else "BUILT",**({"reason":reason} if reason else {})}
    except (OSError,ValueError,HTTPError,URLError,TimeoutError) as error:
        return {"status":"UNKNOWN","reason":str(error),"content_mtime":HERO_CONTENT.stat().st_mtime if HERO_CONTENT.exists() else None,"last_build_time":HERO_HASH.stat().st_mtime if HERO_HASH.exists() else None}

def run_renderer(mode):
    command=[sys.executable,str(HERO_RENDERER),"--content",str(HERO_CONTENT),"--mode",mode,"--target",str(HERO_TARGET)]
    result=subprocess.run(command,cwd=SITE_REPO,capture_output=True,text=True,timeout=30)
    if result.returncode: return 500,{"error":"hero render failed","detail":result.stderr.strip() or result.stdout.strip()}
    match=re.search(r"changed fields:\s*(.*)$",result.stdout.strip())
    changed=[] if not match or match.group(1)=="none" else [field.strip() for field in match.group(1).split(",")]
    return 200,{"ok":True,"mode":mode,"changed_fields":changed,"detail":result.stdout.strip()}

def hero_preview():
    before=HERO_TARGET.read_bytes()
    status,payload=run_renderer("preview")
    if status!=200: return status,payload
    if HERO_TARGET.read_bytes()!=before: return 500,{"error":"preview modified index.html"}
    service_status,service_payload=start_service("site")
    if service_status>=400: return service_status,service_payload
    for _ in range(20):
        if check_service("site")=="running": return 200,{**payload,"preview_url":HERO_PREVIEW_URL,"site_status":"running"}
        time.sleep(.1)
    return 503,{"error":"preview rendered but site server did not become reachable","preview_url":HERO_PREVIEW_URL}

def git_run(*args):
    return subprocess.run(["git","-c",f"safe.directory={SITE_REPO}","-C",str(SITE_REPO),*args],capture_output=True,text=True,timeout=60)

def hero_deploy():
    state=hero_status(); status=state["status"]
    scope=["index.html","tools/.hero-content-hash"]
    details={"commit_scope":scope,"staging":"whole files","warning":"index.html is staged whole; uncommitted packet-#11 carousel changes in it will ride along (no partial staging)."}
    if status=="DRIFT": return 409,{"error":"deploy refused: hero is in DRIFT",**details,"hero_status":state}
    if status!="BUILT": return 409,{"error":f"deploy refused: hero status is {status}, not BUILT",**details,"hero_status":state}
    branch=git_run("branch","--show-current")
    if branch.returncode or branch.stdout.strip()!="main": return 409,{"error":"deploy refused: site repo must be on main",**details,"branch":branch.stdout.strip()}
    diff=git_run("diff","--stat","--",*scope)
    details["diff_stat"]=diff.stdout.strip()
    for command in (("add",*scope),("commit","-m","Build home hero from content source"),("push","origin","main")):
        result=git_run(*command)
        if result.returncode: return 500,{"error":f"git {command[0]} failed","detail":result.stderr.strip() or result.stdout.strip(),**details}
    try: deployed,reason=live_has_sub(hero_values()["Sub"])
    except (OSError,ValueError,HTTPError,URLError,TimeoutError) as error: deployed,reason=False,str(error)
    if not deployed: return 502,{"status":"DEPLOYMENT_UNVERIFIED","reason":reason,**details}
    return 200,{"status":"DEPLOYED","live_url":HERO_LIVE_URL,**details}

def section_paths(section):
    if section not in SITE_SECTIONS: raise ValueError("unknown site section")
    if section=="library": return SECTION_CONTENT_ROOT/"library",SITE_REPO/"tools"/".library-content-hash"
    return SECTION_CONTENT_ROOT/f"{section}.md",SITE_REPO/"tools"/f".{section}-content-hash"

def section_renderer():
    spec=importlib.util.spec_from_file_location("olimazi_render_section",SECTION_RENDERER)
    if spec is None or spec.loader is None: raise ImportError("could not load section renderer")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    return module

def collection_renderer():
    spec=importlib.util.spec_from_file_location("olimazi_render_collection",COLLECTION_RENDERER)
    if spec is None or spec.loader is None: raise ImportError("could not load collection renderer")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    return module

def collection_status(content_path=None,target_path=None,hash_path=None):
    try:
        default_content,default_hash=section_paths("library")
        content=Path(content_path) if content_path else default_content
        target=Path(target_path) if target_path else HERO_TARGET
        built_path=Path(hash_path) if hash_path else default_hash
        renderer=collection_renderer(); items=renderer.load_items(content)
        digest=renderer.collection_digest(items); built=built_path.read_text(encoding="utf-8").strip()
        mtimes=[item.path.stat().st_mtime for item in items]
        payload={"content_mtime":max(mtimes) if mtimes else content.stat().st_mtime,"last_build_time":built_path.stat().st_mtime,"content_hash":digest,"built_hash":built}
        if digest!=built: return {**payload,"status":"EDITED"}
        target_text=renderer.read_text(target)
        if renderer.replace_region(target_text,"library",renderer.render_library(items))!=target_text:
            return {**payload,"status":"DRIFT","reason":"index.html library region does not match the renderer output"}
        return {**payload,"status":"BUILT"}
    except (OSError,ValueError,ImportError) as error:
        return {"status":"UNKNOWN","reason":str(error),"content_mtime":None,"last_build_time":Path(hash_path).stat().st_mtime if hash_path and Path(hash_path).exists() else None}

def section_status(section,content_path=None,target_path=None,hash_path=None):
    if section=="library": return collection_status(content_path,target_path,hash_path)
    try:
        default_content,default_hash=section_paths(section)
        content=Path(content_path) if content_path else default_content
        target=Path(target_path) if target_path else HERO_TARGET
        built_path=Path(hash_path) if hash_path else default_hash
        digest=hashlib.sha256(content.read_bytes()).hexdigest(); built=built_path.read_text(encoding="utf-8").strip()
        payload={"content_mtime":content.stat().st_mtime,"last_build_time":built_path.stat().st_mtime,"content_hash":digest,"built_hash":built}
        if digest!=built: return {**payload,"status":"EDITED"}
        renderer=section_renderer(); loaded_section,spec,values=renderer.load_content(content)
        if loaded_section!=section: return {**payload,"status":"DRIFT","reason":"content source section does not match requested section"}
        target_text=renderer.read_text(target); start,end=renderer.marker_bounds(target_text,section)
        if target_text[start:end]!=renderer.render_fragment(target_text[start:end],spec,values):
            return {**payload,"status":"DRIFT","reason":f"index.html {section} region does not match the renderer output"}
        return {**payload,"status":"BUILT"}
    except (OSError,ValueError,ImportError) as error:
        return {"status":"UNKNOWN","reason":str(error),"content_mtime":Path(content_path).stat().st_mtime if content_path and Path(content_path).exists() else None,"last_build_time":Path(hash_path).stat().st_mtime if hash_path and Path(hash_path).exists() else None}

def run_section_renderer(section,mode):
    content,_=section_paths(section)
    if section=="library": command=[sys.executable,str(COLLECTION_RENDERER),"--mode",mode,"--library-root",str(content)]
    else: command=[sys.executable,str(SECTION_RENDERER),"--content",str(content),"--mode",mode,"--target",str(HERO_TARGET)]
    result=subprocess.run(command,cwd=SITE_REPO,capture_output=True,text=True,timeout=30)
    if result.returncode: return 500,{"error":f"{section} render failed","detail":result.stderr.strip() or result.stdout.strip()}
    if section=="library":
        payload=json.loads(result.stdout); changed=[name for name,value in payload.get("changed",{}).items() if value]
    else:
        match=re.search(r"changed fields:\s*(.*)$",result.stdout.strip())
        changed=[] if not match or match.group(1)=="none" else [field.strip() for field in match.group(1).split(",")]
    return 200,{"ok":True,"section":section,"mode":mode,"changed_fields":changed,"detail":result.stdout.strip()}

def section_preview(section):
    before=HERO_TARGET.read_bytes(); status,payload=run_section_renderer(section,"preview")
    if status!=200: return status,payload
    if HERO_TARGET.read_bytes()!=before: return 500,{"error":"preview modified index.html"}
    service_status,service_payload=start_service("site")
    if service_status>=400: return service_status,service_payload
    for _ in range(20):
        if check_service("site")=="running": return 200,{**payload,"preview_url":HERO_PREVIEW_URL,"site_status":"running"}
        time.sleep(.1)
    return 503,{"error":"preview rendered but site server did not become reachable","preview_url":HERO_PREVIEW_URL}

def section_probe(section):
    if section=="library":
        content,_=section_paths(section); items=collection_renderer().load_items(content)
        values=[]
        for item in items:
            values.extend((item.title,item.card_title,item.subtitle,item.caption,*item.notes))
            values.extend(link.label for link in item.links)
            values.extend(value for image in item.images for value in (image.title,image.caption))
        return max(values,key=len)
    content,_=section_paths(section); loaded_section,_,values=section_renderer().load_content(content)
    if loaded_section!=section: raise ValueError("content source section does not match requested section")
    return max(values.values(),key=len)

def live_has_probe(section):
    probe=section_probe(section); request=Request(HERO_LIVE_URL,headers={"User-Agent":"Olimazi-Mission-Control/1"})
    with urlopen(request,timeout=8) as response:
        if response.status!=200: return False,f"live site returned HTTP {response.status}"
        body=response.read().decode("utf-8",errors="replace")
    present=html.escape(probe,quote=True) in body
    return present,None if present else f"live site does not contain the current {section} probe (longest field value)"

def section_deploy(section):
    state=section_status(section); status=state["status"]; _,hash_path=section_paths(section)
    scope=["index.html",f"tools/{hash_path.name}"]
    if section=="library": scope.append("content/library")
    details={"commit_scope":scope,"staging":"whole files","probe":"longest current field value"}
    if status=="DRIFT": return 409,{"error":f"deploy refused: {section} is in DRIFT",**details,"section_status":state}
    if status!="BUILT": return 409,{"error":f"deploy refused: {section} status is {status}, not BUILT",**details,"section_status":state}
    branch=git_run("branch","--show-current")
    if branch.returncode or branch.stdout.strip()!="main": return 409,{"error":"deploy refused: site repo must be on main",**details,"branch":branch.stdout.strip()}
    diff=git_run("diff","--stat","--",*scope); details["diff_stat"]=diff.stdout.strip()
    for command in (("add",*scope),("commit","-m",f"Build {section} from content source"),("push","origin","main")):
        result=git_run(*command)
        if result.returncode: return 500,{"error":f"git {command[0]} failed","detail":result.stderr.strip() or result.stdout.strip(),**details}
    try: deployed,reason=live_has_probe(section)
    except (OSError,ValueError,ImportError,HTTPError,URLError,TimeoutError) as error: deployed,reason=False,str(error)
    if not deployed: return 502,{"status":"DEPLOYMENT_UNVERIFIED","reason":reason,**details}
    return 200,{"status":"DEPLOYED","live_url":HERO_LIVE_URL,**details}

class Handler(BaseHTTPRequestHandler):
    server_version="MissionControl/1"
    def send_json(self,status,payload):
        data=json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(data)
    def source_allowed(self):
        hosts={f"{HOST}:{PORT}",f"localhost:{PORT}"}; origin=self.headers.get("Origin")
        return self.headers.get("Host","").lower() in hosts and (origin is None or origin.lower() in {f"http://{h}" for h in hosts})
    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        if path=="/api/health": self.send_json(200,{"status":"ok","service":"mission-control"})
        elif path=="/api/services": self.send_json(200,{"services":[{"id":k,"label":v[0],"port":v[1],"status":check_service(k),"startable":command_for(k) is not None} for k,v in SERVICES.items()]})
        elif path=="/api/tracker-pages": self.send_json(200,{"pages":manifest()})
        elif path=="/api/state": self.send_json(200,state_payload())
        elif path=="/api/hero/status": self.send_json(200,hero_status())
        elif re.fullmatch(r"/api/sections/[^/]+/status",path): self.send_json(200,section_status(path.split("/")[3]))
        elif path in {"/","/launchpad.html"}:
            data=(ROOT/"launchpad.html").read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
        elif path.startswith("/api/services/") and path.endswith("/start") or path.startswith("/api/hero/"): self.send_json(405,{"error":"use POST"})
        elif path.startswith("/api/sections/"): self.send_json(405,{"error":"use POST"})
        else: self.send_json(404,{"error":"not found"})
    def do_POST(self):
        path=unquote(urlparse(self.path).path); prefix,suffix="/api/services/","/start"
        if not self.source_allowed(): self.send_json(403,{"error":"request source rejected"}); return
        if self.headers.get("Content-Length","0") not in {"","0"}: self.send_json(400,{"error":"request body not accepted"}); return
        if path.startswith(prefix) and path.endswith(suffix): status,payload=start_service(path[len(prefix):-len(suffix)])
        elif path=="/api/hero/open":
            try: os.startfile(str(HERO_CONTENT)); status,payload=200,{"ok":True,"path":str(HERO_CONTENT.resolve())}
            except OSError as error: status,payload=500,{"error":"could not open hero content","detail":str(error)}
        elif path=="/api/hero/preview": status,payload=hero_preview()
        elif path=="/api/hero/build": status,payload=run_renderer("build")
        elif path=="/api/hero/deploy":
            if self.headers.get("X-Confirm-Deploy","").lower()!="yes": status,payload=400,{"error":"deploy confirmation required","required_header":"X-Confirm-Deploy: yes"}
            else: status,payload=hero_deploy()
        elif re.fullmatch(r"/api/sections/[^/]+/(?:open|preview|build|deploy)",path):
            section,action=path.split("/")[3:5]
            try:
                content,_=section_paths(section)
                if action=="open":
                    try: os.startfile(str(content)); status,payload=200,{"ok":True,"path":str(content.resolve())}
                    except OSError as error: status,payload=500,{"error":f"could not open {section} content","detail":str(error)}
                elif action=="preview": status,payload=section_preview(section)
                elif action=="build": status,payload=run_section_renderer(section,"build")
                elif self.headers.get("X-Confirm-Deploy","").lower()!="yes": status,payload=400,{"error":"deploy confirmation required","required_header":"X-Confirm-Deploy: yes"}
                else: status,payload=section_deploy(section)
            except ValueError as error: status,payload=404,{"error":str(error)}
        else: status,payload=404,{"error":"not found"}
        self.send_json(status,payload)

if __name__=="__main__":
    server=ThreadingHTTPServer((HOST,PORT),Handler); print(f"Mission Control listening on http://{HOST}:{PORT}/")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
