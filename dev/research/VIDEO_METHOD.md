# How to watch the course videos (steps W1–W11)

Any model doing a research step follows this so the notes come out the same. **No development**
during research steps — only notes in `docs/swref/screens/` and corrections to `docs/swref/*`.
The step list (which videos, which supplementary videos) is in `docs/swref/triage/00_README.md`.

## 0. Setup (once per session)
1. Load the built-in browser tools (`ToolSearch` query `mcp__remote-devices__Claude_Browser__`,
   max 64) after reading the `built-in-browser` skill. The pane runs in the owner's Claude
   desktop app; if it is offline, stop and say so.
2. Read the step's triage files (`docs/swref/triage/<playlist>.md`, plus `SUPPLEMENTARY.md` for
   S-A / S-E / S-I videos) and the catalogue files for the step's topic (e.g. 05/06 for
   sketching) so you know what is already known and what is `[K]`. The triage file gives, per
   video, the verdict, the ranges to watch and the timestamps to capture.

## 1. Per video
1. `navigate` to `https://www.youtube.com/watch?v=<id>`; wait ~3 s.
2. Install the helpers below (one `javascript_tool` call), then `fwHQ()` to force the highest
   quality, and `fwInfo()` for duration and resolution.
3. Transcript: already read during triage — start from the triage file's capture timestamps.
   If you need the wording around a moment, `fwTr[id]` (loaded from `localStorage.fwTr` by
   `fwLoadTr()`) or `await fwFetchTr(id)` returns `[[m:ss, text], …]` without touching the
   panel. SKIP videos are not opened; PARTIAL videos only in their listed ranges.
4. Change scan (runs in the page; poll it): `fwScanStart(2, regions)` with regions in video
   pixels — calibrate on the first frame: `left` = the Manager Pane (PropertyManager/tree),
   `top` = CommandManager + menu bar, `gfx` = graphics area. Poll `fwScanStatus()` every ~20 s
   until done; it returns `[t, region, score]` for each visible change.
5. Look at frames: for every left/top change, every transcript moment of interest, and at least
   one frame per 30 s otherwise:
   - `await fwSeek(t); fwShow(x, y, w, h)` draws that region of the frame over the page at full
     pane size; then `computer` → `zoom` on the drawn area (use scale ≈0.8; left-pane crops are
     ~250 image tokens, whole frames ~450). `fwHide()` afterwards.
   - Read the left pane **literally**: title, buttons row, message text, every group in order,
     every control with its label, value/default, state (checked, greyed, expanded/collapsed),
     icons (describe them), which selection box is active (colour).
   - Top pane: active CommandManager tab, highlighted button, flyout opened.
   - Graphics area: previews (colour, transparency), callouts, handles/arrows, rulers, pop-up
     toolbars, inference lines, pointer glyphs, context toolbars, breadcrumbs, dialogs.
6. Write `docs/swref/screens/<playlist>_<nn>_<slug>.md` with the template below **before** moving
   to the next video (context may be compacted at any time).
7. If something contradicts or adds to `docs/swref/*`, edit that file too, tag `[V <id> m:ss]`.
8. Commit after every 2–3 videos; push.

## 2. Note template
```
# <playlist> <nn> <title>  (<id>, <length>)
SOLIDWORKS version seen: <from title bar / splash, or "≈2020 UI">

## Timeline
| t | Action on screen | Left pane | Top pane | Graphics area / pop-ups / cursor | Transcript |
|---|---|---|---|---|---|

## Panels seen (literal layout, top to bottom)
### <Panel title> — state: <tool active / entity selected / editing>
- ...

## Interactions observed
- ...

## Corrections/additions to the catalogue
- <file §> ...

## Not shown in this video (still unverified)
- ...
```

## 3. Helpers (paste into one javascript_tool call)
```js
window.fwHQ=async()=>{const p=document.querySelector('#movie_player');p.setPlaybackQualityRange(p.getAvailableQualityLevels()[0]);const v=document.querySelector('video');v.muted=true;await v.play();await new Promise(r=>setTimeout(r,4000));v.pause();return [v.videoWidth,v.videoHeight,p.getPlaybackQuality()];};
window.fwInfo=()=>{const v=document.querySelector('video');return [v.duration,v.videoWidth,v.videoHeight];};
window.fwSeek=async(t)=>{const v=document.querySelector('video');v.pause();v.currentTime=t;await new Promise(r=>v.addEventListener('seeked',r,{once:true}));await new Promise(r=>setTimeout(r,400));return v.currentTime;};
window.fwShow=(sx,sy,sw,sh)=>{const v=document.querySelector('video');let c=document.getElementById('fwcap');if(!c){c=document.createElement('canvas');c.id='fwcap';c.style.cssText='position:fixed;left:0;top:0;z-index:2147483647;background:#000';document.body.appendChild(c);}const s=Math.min(innerWidth/sw,innerHeight/sh);c.width=Math.round(sw*s);c.height=Math.round(sh*s);c.style.width=c.width+'px';c.style.height=c.height+'px';c.style.display='block';c.getContext('2d').drawImage(v,sx,sy,sw,sh,0,0,c.width,c.height);return [c.width,c.height];};
window.fwHide=()=>{const c=document.getElementById('fwcap');if(c)c.style.display='none';};
window.fwPanelTranscript=async()=>{fwHide();const e=document.querySelector('#description-inline-expander #expand');if(e)e.click();await new Promise(r=>setTimeout(r,800));const b=document.querySelector('ytd-video-description-transcript-section-renderer button');if(!b)return 'no transcript';b.click();for(let i=0;i<20;i++){await new Promise(r=>setTimeout(r,500));const s=document.querySelectorAll('ytd-transcript-segment-renderer');if(s.length)return Array.from(s).map(x=>(x.querySelector('.segment-timestamp')||{}).textContent.trim()+' '+(x.querySelector('.segment-text')||{}).textContent.trim()).join('\n');}return 'transcript did not load';};
window.fwScanStart=(step,regions)=>{window.fwScan={done:false,t:0,out:[]};(async()=>{const v=document.querySelector('video');const c=document.createElement('canvas');c.width=32;c.height=48;const g=c.getContext('2d',{willReadFrequently:true});const sig=r=>{g.drawImage(v,r[0],r[1],r[2],r[3],0,0,32,48);return g.getImageData(0,0,32,48).data;};const d=(a,b)=>{let s=0;for(let i=0;i<a.length;i+=4)s+=Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2]);return s/(a.length/4)/3;};const prev={};for(let t=0;t<v.duration;t+=step){await fwSeek(t);fwScan.t=t;for(const k in regions){const s=sig(regions[k]);if(prev[k]){const x=d(prev[k],s);if(x>6)fwScan.out.push([Math.round(t),k,Math.round(x)]);}prev[k]=s;}}fwScan.done=true;})();return 'started';};
window.fwScanStatus=()=>[fwScan.done,Math.round(fwScan.t),fwScan.out];
```
Transcript helpers (YouTube moved transcripts to the "modern transcript view" in 2026: the
`get_transcript` API answers FAILED_PRECONDITION and the panel shows the *previous* video's text
after in-page navigation; the `get_panel` call below works for any video id):
```js
window.fwParams=(id)=>btoa(String.fromCharCode(0xaa,0x09,0x0f,0x0a,0x0b)+id+String.fromCharCode(0x18,0x02));
window.fwFetchTr=async(id)=>{const r=await fetch('/youtubei/v1/get_panel?prettyPrint=false',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({context:ytcfg.get('INNERTUBE_CONTEXT'),panelId:'PAmodern_transcript_view',params:fwParams(id)})});if(r.status!==200)return {err:'http '+r.status};const j=await r.json();const segs=[];const walk=(o)=>{if(!o||typeof o!=='object')return;if(o.timelineItemViewModel){const v=o.timelineItemViewModel;const t=(v.contentItems||[]).map(c=>c.transcriptSegmentViewModel?(c.transcriptSegmentViewModel.simpleText||''):'').join(' ').replace(/\s+/g,' ').trim();if(t)segs.push([v.timestamp,t]);return;}for(const k in o)walk(o[k]);};walk(j);return {segs};};
window.fwLoadTr=()=>{try{window.fwTr=JSON.parse(localStorage.getItem('fwTr')||'{}');}catch(e){window.fwTr={};}return Object.keys(fwTr).length;};
```
`fwPanelTranscript` above is obsolete (old panel markup). Large `javascript_tool` results are
saved to a file in the workspace automatically — use that to move bulk text out of the browser.

Notes: `fwScanStart` is untested at scale (verify in W1; if the hidden pane throttles timers,
use step 3–4 s). Canvas reads work on YouTube's own video (same origin). Screenshots are not
committed (third-party frames) — the notes describe them.

## Capture timing fix (W1, 2026-11-08)
With the pane hidden, `fwShow` right after `fwSeek` can draw a stale frame. Use these instead
(then `computer` → `zoom` on the drawn region; the pane is ~762×796 px, so crop small regions):
```js
window.fwSeek=async(t)=>{const v=document.querySelector('video');v.pause();const p=new Promise(r=>v.addEventListener('seeked',r,{once:true}));v.currentTime=t;await p;await Promise.race([new Promise(r=>v.requestVideoFrameCallback(()=>r())),new Promise(r=>setTimeout(r,1500))]);await new Promise(r=>setTimeout(r,1200));return v.currentTime;};
window.fwGo=async(t,x,y,w,h)=>{await fwSeek(t);fwShow(x,y,w,h);await new Promise(r=>setTimeout(r,900));return fwShow(x,y,w,h);};
```
Whole 1280×720 frames are barely legible at pane size: crop the top bar (0,0,1280,170), the left pane
(0,150,420,570) or a dialog separately.

## Frame economy (owner feedback, 2026-11-08)
Do not take frames at fixed times. Run `fwScanStart` first; look only at moments where the left pane,
top bar or a dialog changes AND the transcript names something not yet in the catalogue. One crop per
new panel/dialog/option list (small region, not whole frames). Behaviour fully described in the
transcript (zoom, pan, wheel, simple clicks) is recorded from the transcript without frames.
