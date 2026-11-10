# Ocarina of Time (Switch 2) checker, v4.4. Sounding pitch as MIDI numbers (C4 = 60).
NORMAL = {"L": 74, "R": 77, "A": 81, "Y": 83, "X": 86}      # D5 F5 A5 B5 D6
CLASSIC = {"R": 74, "B": 77, "A": 81, "Y": 83, "X": 86}
LAYOUTS = {"Normal": NORMAL, "Classic": CLASSIC}
# Output notation: arrows after the button, whole step first (X⬆️↗️ = +3).
WHOLE = {2: "⬆️", -2: "⬇️"}      # ⬆️ ⬇️  left stick
HALF = {1: "↗️", -1: "↘️"}       # ↗️ ↘️  D-pad (Normal) / L, ZL (Classic)
# Physical inputs for each arrow, per layout:
MODIFIER_INPUTS = {"Normal":  {HALF[1]: "D-pad Up", HALF[-1]: "D-pad Down",
                               WHOLE[2]: "Left stick Up", WHOLE[-2]: "Left stick Down"},
                   "Classic": {HALF[1]: "L", HALF[-1]: "ZL",
                               WHOLE[2]: "Left stick Up", WHOLE[-2]: "Left stick Down"}}
LOW, HIGH = 71, 89                                          # B4 .. F6
BUTTON_OF = {v: k for k, v in NORMAL.items()}
NAMES = "C C# D D# E F F# G G# A A# B".split()
SONGS = {"Zelda's Lullaby": "YXAYXA", "Epona's Song": "XYAXYA",
         "Saria's Song": "RAYRAY", "Sun's Song": "ARXARX",
         "Song of Time": "ALRALR", "Song of Storms": "LRXLRX",
         "Minuet of Forest": "LXYAYA", "Bolero of Fire": "RLRLARAR",
         "Serenade of Water": "LRAAY", "Nocturne of Shadow": "YAALYAR",
         "Requiem of Spirit": "LRLARL", "Prelude of Light": "XAXAYX"}

def name(m): return f"{NAMES[m % 12]}{m // 12 - 1}"
def sign(x): return (x > 0) - (x < 0)
def key_change(T): return min(T % 12, (-T) % 12)
def is_normal(layout): return "L" in layout
def pitch_of(f, layout=NORMAL): return layout[f[0]] + f[1] + f[2]
ALL_SONGS = tuple(SONGS)

def intervals(pitches): return [b - a for a, b in zip(pitches, pitches[1:])]

def verify(mel, T, path, layout=NORMAL):
    """Round-trip and interval invariant: every played pitch is exactly the
    melody note + T, so the ordered interval sequence is unchanged."""
    return len(path) == len(mel) and all(pitch_of(f, layout) == n + T
                                         for f, n in zip(path, mel))

# ---------- Fingerings ----------
def fingerings(p, layout=NORMAL):
    """All (button, whole, half) giving pitch p. Whole step = +/-2 (stick),
    half step = +/-1 (D-pad in Normal, L/ZL in Classic). Both may be held
    at once in either direction: same direction = +/-3, opposite = +/-1."""
    out = [(b, s, d) for b, v in layout.items() for s in (0, -2, 2)
           for d in (0, -1, 1) if v + s + d == p]
    return sorted(out, key=lambda f: ((f[1] != 0) + (f[2] != 0),
                                      f[1] * f[2] < 0, abs(f[1])))

def nmods(f): return (f[1] != 0) + (f[2] != 0)

def token(f):
    """Button, then arrows (whole step first): ("X", 2, 1) -> "X⬆️↗️"."""
    b, s, d = f
    return b + WHOLE.get(s, "") + HALF.get(d, "")

def sequence(path):
    """Output form of a fingering: tokens separated by commas."""
    return ", ".join(token(f) for f in path)

# ---------- Ergonomic cost (judgment-based weights, not game facts) ----------
# Normal: the stick (whole step) and the D-pad (half step) are both worked by
# the left thumb, so using both on one note is a clash, and moving the thumb
# between them takes time. Classic: half steps are on L/ZL (left index finger),
# so the stick and the half step can be held together comfortably.
CHANGE_COST = 0.5    # each modifier state change between consecutive notes
THUMB_TRAVEL = 0.5   # Normal: left thumb moves between stick and D-pad
THUMB_CLASH = 3.0    # Normal: stick + D-pad on the same note

def _thumb(f):
    return "both" if f[1] and f[2] else "stick" if f[1] else "dpad" if f[2] else None

def note_cost(f, layout=NORMAL):
    c = nmods(f)
    if is_normal(layout) and f[1] and f[2]:
        c += THUMB_CLASH
    return c

def change_cost(g, f, layout=NORMAL):
    c = CHANGE_COST * ((g[1] != f[1]) + (g[2] != f[2]))
    if is_normal(layout):
        a, b = _thumb(g), _thumb(f)
        if a and b and a != b:
            c += THUMB_TRAVEL
    return c

def path_cost(path, layout=NORMAL):
    return (sum(note_cost(f, layout) for f in path) +
            sum(change_cost(g, f, layout) for g, f in zip(path, path[1:])))

def best_fingering(pitches, layout=NORMAL):
    """Minimise note costs + change costs over the whole passage."""
    layers = [fingerings(p, layout) for p in pitches]
    if any(not l for l in layers):
        return None
    cost, back = {f: note_cost(f, layout) for f in layers[0]}, [{}]
    for prev, cur in zip(layers, layers[1:]):
        nc, bk = {}, {}
        for f in cur:
            c, g = min(((cost[g] + change_cost(g, f, layout), g) for g in prev),
                       key=lambda t: t[0])
            nc[f], bk[f] = c + note_cost(f, layout), g
        cost = nc
        back.append(bk)
    f = min(cost, key=cost.get)
    total, path = cost[f], [f]
    for bk in reversed(back[1:]):
        f = bk[f]
        path.append(f)
    return total, path[::-1]

# ---------- Performance difficulty (heuristic) ----------
RATINGS = ["Easy", "Moderate", "Hard", "Expert"]
FAST_S = 0.25        # less time than this to set a modifier counts as fast

def difficulty(path, layout=NORMAL, beats=None, bpm=None):
    """Return (rating, reasons). beats/bpm are optional; without them the
    rating is structural only and says so."""
    n = len(path)
    combos = [i for i, f in enumerate(path) if nmods(f) == 2]
    clashes = [i for i in combos if is_normal(layout)]
    # "Set" changes: the next note needs a modifier state different from the last.
    sets = [i for i in range(1, n) if nmods(path[i]) and
            (path[i][1], path[i][2]) != (path[i - 1][1], path[i - 1][2])]
    travel = [i for i in range(1, n) if is_normal(layout) and
              _thumb(path[i]) and _thumb(path[i - 1]) and
              _thumb(path[i]) != _thumb(path[i - 1])]
    timed = bool(beats) and bool(bpm)
    fast = [i for i in sets if timed and beats[i - 1] * 60.0 / bpm < FAST_S]
    reasons = []
    if not any(nmods(f) for f in path):
        r = 0
    else:
        r = 1
        if combos:
            r = 2; reasons.append(f"{len(combos)} note(s) need whole + half step together")
        if len(sets) > n / 2:
            r = 2; reasons.append(f"modifier changes on {len(sets)} of {n} notes")
        if fast:
            r = 2; reasons.append(f"{len(fast)} modifier change(s) in under {FAST_S} s")
        if travel:
            reasons.append(f"left thumb moves between stick and D-pad {len(travel)} time(s)")
            if len(travel) > n / 4:
                r = max(r, 2)
        if clashes and (len(clashes) >= 3 or set(clashes) & set(fast)):
            r = 3; reasons.append("stick + D-pad on one note with the left thumb (Normal), repeatedly or at speed")
        elif clashes:
            reasons.append("stick + D-pad on one note with the left thumb (Normal)")
    if not timed:
        reasons.append("tempo unknown: rating ignores speed")
    return RATINGS[r], reasons

# ---------- Exact test (modifiers allowed): full pipeline ----------
# For every valid shift T: optimal fingering -> fix learned-song conflicts ->
# verify pitches -> recompute cost, level and difficulty -> rank. Conflict
# fixes happen BEFORE ranking, so a conflict-free transposition can beat a
# fixed-up original key.
def analyze(mel, prefer="easiest", layout=NORMAL, beats=None, bpm=None,
            learned=ALL_SONGS, keep_songs=False):
    """All valid shifts T, best first ([] if range > 18 semitones).
    learned: built-in songs Link knows (default all). keep_songs=True when
    the requested melody IS a Zelda song and should trigger.
    Each result is a dict: T, level, cost, path, rating, reasons,
    conflicts_avoided, plain_path, key."""
    if max(mel) - min(mel) > HIGH - LOW:
        return []
    res = []
    for T in range(LOW - min(mel), HIGH - max(mel) + 1):
        _, plain = best_fingering([n + T for n in mel], layout)
        avoided = sorted({sg for sg, _ in song_conflicts(plain, layout, learned)})
        path = plain if keep_songs or not avoided else break_conflicts(plain, layout, learned)
        assert verify(mel, T, path, layout), "fingering does not reproduce the melody"
        cost = path_cost(path, layout)
        level = 1 + max(nmods(f) for f in path)
        rating, reasons = difficulty(path, layout, beats, bpm)
        if avoided and not keep_songs:
            reasons.insert(0, "alternative fingering avoids " + ", ".join(avoided))
        rk, kc = RATINGS.index(rating), key_change(T)
        key = (rk, cost, kc, abs(T)) if prefer == "easiest" else (kc, rk, cost, abs(T))
        res.append({"key": key, "T": T, "level": level, "cost": cost, "path": path,
                    "rating": rating, "reasons": reasons,
                    "conflicts_avoided": [] if keep_songs else avoided,
                    "plain_path": plain})
    return sorted(res, key=lambda r: r["key"])

def recommend_layout(mel, prefer="easiest", beats=None, bpm=None,
                     learned=ALL_SONGS, keep_songs=False):
    """Analyze both layouts. Returns (pick, best_per_layout, why). Normal is
    the default (no settings change); pick Classic only if it rates easier,
    or rates the same while Normal needs stick + D-pad on one note."""
    best = {}
    for nm, lay in LAYOUTS.items():
        r = analyze(mel, prefer, lay, beats, bpm, learned, keep_songs)
        best[nm] = r[0] if r else None
    if best["Normal"] is None:
        return None, best, "range too wide for an exact performance"
    n, c = best["Normal"], best["Classic"]
    rn, rc = RATINGS.index(n["rating"]), RATINGS.index(c["rating"])
    clashes = sum(nmods(f) == 2 for f in n["path"])
    if rc < rn:
        return "Classic", best, f"Classic rates {c['rating']}, Normal {n['rating']}"
    if rc == rn and clashes:
        return "Classic", best, (f"both rate {n['rating']}, but Normal needs stick + D-pad "
                                 f"on {clashes} note(s) with the left thumb")
    if rn < rc:
        return "Normal", best, f"Normal rates {n['rating']}, Classic {c['rating']}"
    return "Normal", best, f"both rate {n['rating']}; Normal needs no settings change"

def exact_fragments(mel, min_len=4):
    """Maximal contiguous windows (0-based start, end exclusive) within 18 semitones."""
    out, n = [], len(mel)
    for i in range(n):
        for j in range(n, i + min_len - 1, -1):
            if max(mel[i:j]) - min(mel[i:j]) <= HIGH - LOW:
                if not any(a <= i and j <= b for a, b in out):
                    out.append((i, j))
                break
    return out

def octave_fold(mel):
    """For passages wider than 18 semitones: choose T that folds the fewest
    notes by an octave into range. Returns (folded_count, T, pitches)."""
    best = None
    for T in range(LOW - max(mel), HIGH - min(mel) + 1):
        out = []
        for n in mel:
            p = n + T
            while p < LOW: p += 12
            while p > HIGH: p -= 12
            out.append(p)
        folded = sum(p != n + T for p, n in zip(out, mel))
        k = (folded, key_change(T), abs(T))
        if best is None or k < best[0]:
            best = (k, T, out)
    return best[0][0], best[1], best[2]

# ---------- No-modifier (five-button) mode ----------
P5 = sorted(NORMAL.values())

def five_button_transpositions(mel):
    lo = min(mel)
    return sorted({p - lo for p in P5 if all(n + p - lo in BUTTON_OF for n in mel)},
                  key=lambda T: (key_change(T), abs(T)))

def _shape_breaks(mel, out):
    return sum(sign(b - a) != sign(d - c) for a, b, c, d in zip(mel, mel[1:], out, out[1:]))

def five_button_approx(mel, goal="closest"):
    """Best five-note arrangement over all shifts and all note choices (DP).
    goal="closest": fewest semitones changed, then fewest shape breaks.
    goal="shape":   keep every up / down / repeat first, then fewest semitones.
    Shape break = an adjacent pair whose direction (up, down, same) changed.
    Returns ((breaks, displacement, changed, |T|), T, pitches)."""
    n = len(mel)
    W = 1.0 / (n + 1)                     # makes the DP lexicographic
    wb, wd = (W, 1.0) if goal == "closest" else (float(n * 24 + 1), 1.0)
    best = None
    for T in range(62 - min(mel), 87 - min(mel)):
        sh = [x + T for x in mel]
        def pc(i, p):
            d = abs(p - sh[i])
            return wd * d + W * W * (d != 0)
        cost = {p: (pc(0, p), [p]) for p in P5}
        for i in range(1, n):
            want = sign(mel[i] - mel[i - 1])
            nc = {}
            for p in P5:
                c, q = min((cost[q][0] + wb * (sign(p - q) != want), q) for q in P5)
                nc[p] = (c + pc(i, p), cost[q][1] + [p])
            cost = nc
        _, out = min(cost.values())
        k = (_shape_breaks(mel, out), sum(abs(a - b) for a, b in zip(out, sh)),
             sum(a != b for a, b in zip(out, sh)), abs(T))
        rank = k if goal == "shape" else (k[1], k[0], k[2], k[3])
        if best is None or rank < best[0]:
            best = (rank, k, T, out)
    return best[1], best[2], best[3]

# ---------- Built-in song conflicts ----------
# Tested in-game: a song triggers only when every one of its notes is played
# on its own primary button with no modifier. A modified note breaks the match.
def _plain(path, layout):
    return "".join(BUTTON_OF[layout[f[0]]] if nmods(f) == 0 else "?" for f in path)

def song_conflicts(path, layout=NORMAL, learned=ALL_SONGS):
    """Return [(song, start_index)] for every learned built-in song the path
    would trigger."""
    seq = _plain(path, layout)
    return [(name_, i) for name_ in (learned or ()) for i in range(len(seq))
            if seq.startswith(SONGS[name_], i)]

def break_conflicts(path, layout=NORMAL, learned=ALL_SONGS):
    """Inside each conflict, swap one note for an alternative fingering of the
    same pitch (sounds identical, breaks recognition). Picks the swap with the
    lowest total path cost. Returns a new path."""
    path = list(path)
    while True:
        hits = song_conflicts(path, layout, learned)
        if not hits:
            return path
        song, i = hits[0]
        best = None
        for j in range(i, i + len(SONGS[song])):
            for alt in fingerings(pitch_of(path[j], layout), layout):
                if nmods(alt):
                    cand = path[:j] + [alt] + path[j + 1:]
                    c = path_cost(cand, layout)
                    if best is None or c < best[0]:
                        best = (c, cand)
        path = best[1]

# ---------- Breath check ----------
# Tested in-game: one breath lasts about 6 s of continuous sound. Any release
# followed by a brief pause resets it, whichever button is played next. It does
# not reset when a held note is bent with a modifier, or when the player switches
# instantly (no pause) to the same pitch on another button. Both are legato.
BREATH_LIMIT_S = 6.0

def breath_warnings(beats, bpm, legato_groups=()):
    """beats: note durations; legato_groups: (first, last) index ranges played
    with no pause (bends or instant switches). Returns [(first, last, seconds)]
    for any breath longer than the limit."""
    joined = {i for a, b in legato_groups for i in range(a + 1, b + 1)}
    out, a = [], 0
    for i in range(1, len(beats) + 1):
        if i == len(beats) or i not in joined:
            secs = sum(beats[a:i]) * 60.0 / bpm
            if secs > BREATH_LIMIT_S:
                out.append((a, i - 1, round(secs, 2)))
            a = i
    return out

# ---------- Comment-ready block (both layouts, copy-paste) ----------
# Arrows mean the same in both layouts; only the note letters differ.
# The block holds only the nickname and the two lines. The legend is shown
# separately, in the Ocarina Key Legend section (LEGEND).
LEGEND = ("⬆️⬇️ = hold stick up/down (whole step)\n"
          "↗️↘️ = hold half step up/down (Normal: D-pad ↑↓ · Classic: L / ZL)\n"
          "Hold the arrow first, then press the button. Change it between notes, not during.")

def phrase_line(path, breaks=()):
    """Comma-separated tokens, with ' | ' before each note index in breaks."""
    return "".join((" | " if i in breaks else ", " if i else "") + token(f)
                   for i, f in enumerate(path))

def comment_block(mel, T, nickname, breaks=(), learned=ALL_SONGS, keep_songs=False):
    """Comment-ready text: the user's nickname, then Normal and Classic lines
    for the same shift T, each with its own best fingering (song conflicts
    already avoided)."""
    lines = ["\U0001f3b5 " + nickname.strip(), ""]
    for nm, lay in LAYOUTS.items():
        r = next(x for x in analyze(mel, "easiest", lay, learned=learned,
                                    keep_songs=keep_songs) if x["T"] == T)
        assert verify(mel, T, r["path"], lay)
        lines += [f"{nm} mode:", phrase_line(r["path"], breaks), ""]
    return "\n".join(lines).rstrip()
