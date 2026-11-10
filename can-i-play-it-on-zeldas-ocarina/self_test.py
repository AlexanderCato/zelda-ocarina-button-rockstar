# Ocarina of Time (Switch 2) checker self-test, v4.4.
# Runs every case in Section 12 of the skill against ocarina_check.py.
# Usage: python3 self_test.py   (ocarina_check.py must be in the same folder)
# Every line must say PASS. Any FAIL means this install is not at parity.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocarina_check import *

results = []
def check(label, got, want):
    ok = got == want
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f"\n     got:  {got!r}\n     want: {want!r}"))

def best(mel, layout=NORMAL, **kw):
    return analyze(mel, layout=layout, **kw)[0]

def summary(r):
    return (r["T"], r["level"], r["rating"], sequence(r["path"]))

SOS = [74, 77, 86, 74, 77, 86]                       # D5 F5 D6 D5 F5 D6
check("Song of Storms, none learned, Normal", summary(best(SOS, learned=())),
      (0, 1, "Easy", "L, R, X, L, R, X"))
check("Song of Storms, none learned, Classic", summary(best(SOS, CLASSIC, learned=())),
      (0, 1, "Easy", "R, B, X, R, B, X"))
check("Song of Storms, all learned, Normal", summary(best(SOS)),
      (-1, 2, "Moderate", "L↘️, R↘️, X↘️, L↘️, R↘️, X↘️"))
check("Song of Storms, all learned, Classic", summary(best(SOS, CLASSIC)),
      (-1, 2, "Moderate", "R↘️, B↘️, X↘️, R↘️, B↘️, X↘️"))
check("Song of Storms, all learned, original key", summary(analyze(SOS, "original")[0]),
      (0, 3, "Hard", "R⬇️↘️, R, X, L, R, X"))
check("Song of Storms, keep_songs=True", sequence(best(SOS, keep_songs=True)["path"]),
      "L, R, X, L, R, X")

SOS5 = [69, 72, 81, 69, 72, 81]                      # A4 C5 A5 A4 C5 A5
check("Storms down 5, none learned", summary(best(SOS5, learned=())),
      (5, 1, "Easy", "L, R, X, L, R, X"))
check("Storms down 5, all learned", summary(best(SOS5)),
      (3, 2, "Moderate", "L⬇️, R⬇️, X⬇️, L⬇️, R⬇️, X⬇️"))

ZL = [83, 86, 81, 83, 86, 81]                        # B5 D6 A5 B5 D6 A5
for nm, lay in LAYOUTS.items():
    check(f"Zelda's Lullaby, all learned, {nm}", summary(best(ZL, lay)),
          (0, 2, "Moderate", "A⬆️, X, A, Y, X, A"))

ODE = [78, 78, 79, 81, 81, 79, 78, 76, 74, 74, 76, 78, 78, 76, 76]
check("Ode to Joy, valid shifts", sorted(r["T"] for r in analyze(ODE)), list(range(-3, 9)))
check("Ode to Joy, no song conflicts", any(r["conflicts_avoided"] for r in analyze(ODE)), False)
pick, b, why = recommend_layout(ODE)
check("Ode to Joy, layout", (pick, why), ("Normal", "both rate Moderate; Normal needs no settings change"))
check("Ode to Joy, easiest, Normal", summary(best(ODE)),
      (5, 2, "Moderate", "Y, Y, Y↗️, X, X, Y↗️, Y, A, R⬆️, R⬆️, A, Y, Y, A, A"))
check("Ode to Joy, easiest, Classic", sequence(best(ODE, CLASSIC)["path"]),
      "Y, Y, Y↗️, X, X, Y↗️, Y, A, B⬆️, B⬆️, A, Y, Y, A, A")
check("Ode to Joy, original key, Normal", summary(analyze(ODE, "original")[0]),
      (0, 2, "Moderate", "R↗️, R↗️, R⬆️, A, A, R⬆️, R↗️, R↘️, L, L, R↘️, R↗️, R↗️, R↘️, R↘️"))
check("Ode to Joy, original key, Classic", sequence(analyze(ODE, "original", CLASSIC)[0]["path"]),
      "B↗️, B↗️, B⬆️, A, A, B⬆️, B↗️, B↘️, R, R, B↘️, B↗️, B↗️, B↘️, B↘️")
check("Ode to Joy, five-button exact", five_button_transpositions(ODE), [])
k, T, out = five_button_approx(ODE, "closest")
check("Ode to Joy, five-button closest", (T, out, k[2], k[0]),
      (5, [83, 83, 83, 86, 86, 83, 83, 81, 77, 77, 81, 83, 83, 81, 81], 4, 2))
k, T, out = five_button_approx(ODE, "shape")
check("Ode to Joy, five-button shape kept", (T, out, k[2], k[0]),
      (3, [81, 81, 83, 86, 86, 83, 81, 77, 74, 74, 77, 81, 81, 77, 77], 10, 0))

CCD = [72, 73, 74]
k, T, out = five_button_approx(CCD, "closest")
check("C5 C#5 D5, five-button closest", (out, k[0]), ([81, 81, 83], 1))
k, T, out = five_button_approx(CCD, "shape")
check("C5 C#5 D5, five-button shape kept", (out, k[0], k[2]), ([81, 83, 86], 0, 2))

FULL = [71, 74, 77, 81, 83, 86, 89]                  # B4 .. F6
check("Full range, Normal", summary(best(FULL)),
      (0, 3, "Hard", "L⬇️↘️, L, R, A, Y, X, X⬆️↗️"))
check("Full range, Classic", summary(best(FULL, CLASSIC)),
      (0, 3, "Hard", "R⬇️↘️, R, B, A, Y, X, X⬆️↗️"))
check("Full range, layout", recommend_layout(FULL)[0], "Classic")
beats = [0.5] * 7
check("Full range, eighths at 160 BPM",
      (best(FULL, beats=beats, bpm=160)["rating"], best(FULL, CLASSIC, beats=beats, bpm=160)["rating"]),
      ("Expert", "Hard"))

ARP = [62, 66, 69, 74, 78, 81, 86]                   # D-major arpeggio, range 24
check("D-major arpeggio, range filter", analyze(ARP), [])
check("D-major arpeggio, octave fold", octave_fold(ARP)[:2], (2, 11))

check("key_change(60)", key_change(60), 0)
check("token +3", token(("X", 2, 1)), "X⬆️↗️")
check("token +1 (opposite)", token(("A", 2, -1)), "A⬆️↘️")
check("comment_block format", comment_block(SOS, -1, "Storm test"),
      "🎵 Storm test\n\nNormal mode:\nL↘️, R↘️, X↘️, L↘️, R↘️, X↘️\n\n"
      "Classic mode:\nR↘️, B↘️, X↘️, R↘️, B↘️, X↘️")

print(f"\n{sum(results)}/{len(results)} passed" + ("" if all(results) else " — DO NOT USE this install"))
sys.exit(0 if all(results) else 1)
