# 🎸 Zelda Ocarina Button Rockstar

Play almost any melody on Link's ocarina in *The Legend of Zelda: Ocarina of Time* (Nintendo Switch 2). Give your AI chatbot the notes or a song name, and it gives you the exact buttons to press, for both control layouts, ready to copy into a comment.

Works with **Claude**, **ChatGPT** and **Grok**. Free and unofficial.

**[⬇️ Download the latest version](https://github.com/AlexanderCato/zelda-ocarina-button-rockstar/releases/latest/download/can-i-play-it-on-zeldas-ocarina.zip)**

⭐ **Found it helpful?** Star the project at [github.com/AlexanderCato/zelda-ocarina-button-rockstar](https://github.com/AlexanderCato/zelda-ocarina-button-rockstar) so other players can find it too.

---

## What you get

Paste in some notes and you get back something like this:

```
🎵 Ode to Joy

Normal mode:
Y, Y, Y↗️, X | X, Y↗️, Y, A | R⬆️, R⬆️, A, Y | Y, A, A

Classic mode:
Y, Y, Y↗️, X | X, Y↗️, Y, A | B⬆️, B⬆️, A, Y | Y, A, A
```

Below that is a short summary: how hard it is, which key it's in, and which layout to use. If you want the details, there's a full explanation of how it worked it out.

It also:
- moves the tune to the easiest key that fits the ocarina, and still shows you the original key
- avoids playing one of Link's 12 songs by accident partway through, which would interrupt your performance
- checks every answer with a built-in calculator, so the buttons always play exactly the notes you gave it

## How to read the buttons

| Symbol | Meaning | Normal layout | Classic layout |
|---|---|---|---|
| ⬆️ ⬇️ | Whole step up / down | Left stick up / down | Left stick up / down |
| ↗️ ↘️ | Half step up / down | D-pad up / down | L / ZL |

Hold the arrow first, then press the button. `X⬆️↗️` means hold both, then press X. Change arrows between notes, never while a note is playing.

To switch layouts in the game, go to **+ → Options → Input Options → Swap Ocarina-Playing Controls**.

## Example inputs

Paste the notes in order. Here are three different example inputs, and all three work. Each one is the opening of Ode to Joy:

```
F# F# G A A G F# E D D E F# F# E E
```

```
F# – F# – G – A – A – G – F# – E – D – D – E – F# – F# – E – E
```

```
F♯ – F♯ – G – A – A – G – F♯ – E | D – D – E – F♯ – F♯ – E – E
```

- Sharps can be written `#` or `♯`, and flats `b` or `♭`.
- Octave numbers are optional (`D5`). Add one to any note that jumps further than it looks.
- `|` or a new line starts a new phrase.
- You can also just ask: "Can I play [song] on the ocarina?" If it can't find or provide the notes for a song, it will ask you to paste them. It never makes notes up.

## Install

First, [download `can-i-play-it-on-zeldas-ocarina.zip`](https://github.com/AlexanderCato/zelda-ocarina-button-rockstar/releases/latest/download/can-i-play-it-on-zeldas-ocarina.zip).

### Claude
1. Go to **Settings → Capabilities** and turn on **Code execution and file creation**. Skills need this setting.
2. Go to **Customize → Skills**, click **+**, then **Create skill → Upload a skill**.
3. Upload the zip as it is. Don't unzip it.

### Grok
1. Open **Skills** in Grok.
2. Import the zip as it is. Don't unzip it.

You may need a paid Grok plan to add skills.

### ChatGPT
1. Unzip the file.
2. Create a new **Project**.
3. Open `chatgpt-project-instructions.txt`, copy everything in it, and paste it into the project's **Instructions**.
4. Add these three files to the project: `SKILL.md`, `ocarina_check.py` and `self_test.py`.
5. Start your chats inside that project.

### Check that it works
In a new chat, type **self-test**. You should see **32/32 passed**. If any check fails, don't trust that install.

Then type **hi**. You should get a welcome message with the example inputs.

## Using it

1. Paste your notes, or ask about a song by name.
2. It asks what you'd like to call the tune. Give it a name, or say **skip**.
3. Copy the block at the top, then play it or paste it into a comment to share.

If you'd like a step-by-step practice guide, ask "How do I play this?".

## Good to know

- The ocarina covers 18 semitones, from B4 to F6. If a tune doesn't fit, you get a playable excerpt or a clearly labelled approximation.
- Rhythm isn't included unless you add it, as beats after each note (`E4:1 F4:0.5`). Hold each button for as long as the note lasts.
- Link can hold one note for about 6 seconds before he takes a breath.
- The game behaviour this relies on was tested on Switch 2 in November 2026.

## Other chatbots

Attach `prompt/ocarina_song_analyzer_v4.4.txt` to a chat and say "Follow these instructions." It works best with chatbots that can run Python.

## What's in this repo

| Path | What it is |
|---|---|
| `can-i-play-it-on-zeldas-ocarina/` | The skill: instructions, checker and self-test. It's the same as the download. |
| `prompt/` | The full instructions as one file, for other chatbots |

## Updating

Download the latest zip. On Claude and Grok, upload it to replace the old skill. On ChatGPT, replace the instructions and the three project files. Then type **self-test** again.

---

Unofficial fan project, not affiliated with or endorsed by Nintendo. *The Legend of Zelda* and *Ocarina of Time* are trademarks of Nintendo.
