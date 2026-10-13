"""Builds prompts/college-schedule/index.html and links it from every page's nav and the home page."""
import html, os, re, glob, sys
ROOT = sys.argv[1]
E = html.escape

PROMPTS = [
 ("Map the 3–4 year path", """Act as a college academic planning advisor. Help map a 3–4 year pathway for a student considering [major/minor options].

Include:
- Student bio and learning style
- Degree requirements [insert URL(s)]
- Major interests: [insert]
- Minor interests: [insert]
- Career path: [insert]
- AP/IB/Dual Enrollment credits (scored and score not available)
- AP credit policy URL
- Study abroad timing
- Internship timing
- Test prep timing
- Greek life or extracurricular time demands
- Courses to prioritize early
- Courses to delay
- Freshman fall options that keep paths open

Student bio:
[Curious thinker, morning person/night owl, project-driven/problem-solving-driven, prefers small or large classes, exam style preferences, discussion vs lecture comfort, schedule needs, extracurricular plans]

Then narrow the plan to the best freshman fall strategy."""),
 ("Turn the pathway into fall course targets", """Using the 3–4 year pathway above, identify the best freshman fall course targets.

For each course, explain:
- Why it belongs in fall
- What requirement it satisfies
- What future path it keeps open
- What risk it creates
- Whether it depends on AP/IB/DE credit
- Whether it should be first choice, backup, or optional"""),
 ("Review available sections", """I am going to upload screenshots of available course sections.

Use the screenshots to compare:
- Course time
- Professor
- Location/building
- Back-to-back class distance
- Class format if shown
- Open, closed, full, or unavailable status
- Fit with the student's schedule preferences

Build the best possible schedule from the available options."""),
 ("Compare degree paths", """Compare [College/Major 1] versus [College/Major 2].

Identify:
- What overlaps
- What does not
- Language requirements
- AP/IB/DE credit impact
- Courses that keep both paths open
- Courses that could lock the student in too early"""),
 ("Plan around opportunities", """Using this degree path, identify where the student could fit:
- Study abroad
- Internships
- Research
- Leadership
- Greek life
- Test prep
- Application timelines

Tell me which freshman and sophomore courses should be prioritized to keep those options open."""),
 ("Evaluate professors and fit", """I am going to upload professor review screenshots.

Use them carefully. Rate My Professors is subjective, UF does not support it, and unhappy students may be more likely to post.

Do not treat reviews as fact.

Look for patterns about:
- Teaching style
- Workload
- Exam style
- Clarity
- Attendance expectations
- Communication
- Fit for this student's learning style

Summarize which professor may be the best fit and why."""),
 ("Check every course against every path", """For each course, tell me if it satisfies each path. Use yes, no, or maybe.

Paths:
- Major 1
- Major 2
- Minor 1
- Minor 2
- Gen Ed
- Quest
- Language
- Pre-law/pre-grad preparation

Courses:
- Course 1
- Course 2
- Course 3

Explain any uncertainty."""),
 ("Check conflicts, workload, and location", """Check this schedule for:
- Time conflicts
- Back-to-back class distance
- Early or late classes
- Lab conflicts
- Credit load
- Reading/writing load
- Exam risk
- Freshman adjustment
- Greek life or extracurricular conflicts

Tell me what works, what is risky, what should move, and what should be a backup."""),
 ("Build the final schedule with pivot options", """Create a final schedule table with:
- Class #
- Course
- Professor
- Credits
- Time
- Building
- Requirement purpose
- Why it fits
- Risk level
- Backup option
- What the backup replaces

Build at least two versions:
- Best-case schedule
- Backup schedule if key classes are full

Then rewrite it in student-friendly language."""),
]
FINAL = ("Make it student-friendly", """Rewrite this schedule so a student can understand it.
Explain why each class is there, what requirement it satisfies, and what risk it creates. Avoid academic jargon.""")

def card(num, title, body, bonus=False):
    pid = f"p{num}"
    tag = "Final prompt" if bonus else f"Prompt {num}"
    return (f'<article class="prompt" id="{pid}"><div class="prompt-head"><span class="label">{tag}</span>'
            f'<h3>{E(title)}</h3><button type="button" class="copy" data-target="{pid}-text">Copy prompt</button></div>'
            f'<pre class="prompt-text" id="{pid}-text">{E(body)}</pre></article>')

r = "../../"
nav = (f'<nav aria-label="Sections"><a href="{r}index.html#work">Work</a><a href="{r}blogs/industry-insights/index.html">Writing</a>'
       f'<a href="{r}prompts/college-schedule/index.html" aria-current="page">Prompts</a><a href="{r}index.html#about">About</a><a href="{r}index.html#contact">Contact</a></nav>')
header = (f'<header class="top"><a class="brand" href="{r}index.html" aria-label="Bean Hop home"><img class="mark" src="{r}images/bean-mark.png" alt="" width="212" height="240">'
          f'<span class="bh-word">bean hop<small>a leap of strategy</small></span></a>{nav}</header>')
start = ["Degree path", "AP credit", "Study abroad", "Internships", "LSAT prep", "Course availability", "Freshman workload"]
toc = "".join(f'<li><a href="#p{i}">{i}. {E(t)}</a></li>' for i, (t, _) in enumerate(PROMPTS, 1)) + '<li><a href="#p10">Final: Make it student-friendly</a></li>'
cards = "".join(card(i, t, b) for i, (t, b) in enumerate(PROMPTS, 1)) + card(10, FINAL[0], FINAL[1], bonus=True)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Freshman Schedule Prompts | Bean Hop</title>
<meta name="description" content="9 AI prompts (plus a final rewrite) a parent used to help plan a University of Florida freshman schedule, from 4-year degree path down to fall classes.">
<meta property="og:title" content="9 AI prompts to build a freshman college schedule">
<meta property="og:description" content="Start with the 3–4 year path, then narrow to fall. AI doesn't replace the advisor; it helps the student show up with better questions.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Graduate&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{r}style.css">
</head>
<body>
<div class="wrap">{header}
<article>
<div class="article-head"><span class="label">Prompt library · College planning</span>
<h1>9 AI prompts to build a freshman college schedule</h1>
<span class="byline">Ashley Schultz · October 2026</span></div>
<div class="prose">
<p>I used AI to help build my son's freshman college schedule at the University of Florida.</p>
<p>We didn't start with "What classes should he take this fall?" We started bigger:</p>
<ul class="start">{"".join(f"<li>{E(s)}</li>" for s in start)}</ul>
<p>Then we narrowed it down to fall.</p>
<p class="pull">AI didn't replace the advisor. It helped him show up with better questions for a 30-minute scheduling meeting.</p>
<div class="note"><strong>Before you use these:</strong> AI can get requirements wrong. Check every course against your school's official catalog and confirm the plan with an academic advisor. Leave out student ID numbers and other private details when you paste or upload anything.</div>
</div>
<nav class="toc" aria-label="Prompts"><span class="label">The prompts</span><ol>{toc}</ol></nav>
<div class="prompts">{cards}</div>
<div class="article-foot"><span class="crumb"><a href="{r}index.html">← Back to Bean Hop</a></span></div>
</article>
<footer>© 2026 Bean Hop Consulting, LLC</footer></div>
<script>
document.querySelectorAll('.copy').forEach(function(b){{b.addEventListener('click',function(){{
 var t=document.getElementById(b.dataset.target), txt=t.textContent;
 var done=function(){{b.textContent='Copied';setTimeout(function(){{b.textContent='Copy prompt'}},1600)}};
 var sel=function(){{var r=document.createRange();r.selectNodeContents(t);var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected, press Ctrl+C'}};
 try{{navigator.clipboard.writeText(txt).then(done,sel)}}catch(e){{sel()}}
}})}});
</script>
</body>
</html>
"""
os.makedirs(os.path.join(ROOT, "prompts/college-schedule"), exist_ok=True)
open(os.path.join(ROOT, "prompts/college-schedule/index.html"), "w").write(page)

css = """
/* Prompt library */
.prompts { display: grid; gap: 1.25rem; margin-top: 1.5rem; }
.prompt { border: 1px solid var(--line); border-radius: 10px; background: var(--surface); overflow: hidden; scroll-margin-top: 1rem; }
.prompt-head { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem 1rem; padding: .9rem 1rem .6rem; }
.prompt-head .label { flex-basis: 100%; }
.prompt-head h3 { flex: 1 1 14rem; min-width: 0; font-size: 1.15rem; }
.prompt-text { margin: 0; padding: .9rem 1rem 1.1rem; border-top: 1px solid var(--line); background: var(--bg); font-family: var(--mono); font-size: .82rem; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }
.toc { margin-top: 2rem; display: grid; gap: .5rem; }
.toc ol { margin: 0; padding-left: 0; list-style: none; columns: 2 16rem; column-gap: 2rem; }
.toc li { break-inside: avoid; padding: .2rem 0; font-family: var(--display); font-weight: 600; font-size: .98rem; }
.toc a { text-decoration: none; }
.toc a:hover { text-decoration: underline; }
.prose .pull { font-family: var(--display); font-weight: 600; font-size: 1.2rem; line-height: 1.35; color: var(--ink); border-left: 3px solid var(--accent); padding-left: 1rem; }
.prose ul.start { columns: 2 12rem; }
nav a[aria-current="page"] { color: var(--accent); }
"""
st = os.path.join(ROOT, "style.css")
s = open(st).read()
if "/* Prompt library */" not in s:
    open(st, "w").write(s + css)

# nav link on every other page
for p in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
    if "prompts/college-schedule" in p: continue
    s = open(p).read()
    if "prompts/college-schedule" in s and "<nav" in s and ">Prompts<" in s: continue
    m = re.search(r'<a href="([^"]*)blogs/industry-insights/index\.html">Writing</a>', s)
    if not m: continue
    pre = m.group(1)
    s = s.replace(m.group(0), m.group(0) + f'<a href="{pre}prompts/college-schedule/index.html">Prompts</a>', 1)
    open(p, "w").write(s)

# home page feature, before Recent articles
hp = os.path.join(ROOT, "index.html")
s = open(hp).read()
if 'id="prompts"' not in s:
    feat = ('<section id="prompts"><div class="sec-head"><span class="label">Prompt library</span><h2>Free prompts</h2></div>'
            '<div class="posts"><a class="post-row" href="prompts/college-schedule/index.html"><span class="pd">Oct 2026</span>'
            '<span><span class="pt">9 AI prompts to build a freshman college schedule</span>'
            '<span class="px">How we mapped a 3–4 year degree path first, then narrowed it to fall classes. Copy-ready prompts for parents and students.</span></span></a></div></section>')
    s = s.replace('<section id="writing">', feat + '<section id="writing">', 1)
    open(hp, "w").write(s)
print("ok")
