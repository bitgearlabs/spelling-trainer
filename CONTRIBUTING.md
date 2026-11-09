# Contributing

Thanks for your interest in Spelling Trainer!

## Report a problem or suggest an idea

Open an [issue](../../issues/new/choose) and pick a template. For bugs, please include:

- what you did and what you expected to happen,
- the voice engine you used (Edge, gTTS or Offline),
- your Windows and browser versions.

## Send a change

1. Fork the repository and create a branch.
2. Set up the project (see **Quick start** in the README).
3. Make your change and try it in the browser.
4. Open a pull request that explains what changed and why.

## Where things live

| File | What it does |
|---|---|
| `generators.py` | Random question generators |
| `checker.py` | Answer checking |
| `tts_engines.py` | Text-to-speech engines |
| `server.py` | Local web server and API |
| `web/index.html` | The interface |

Please never commit tokens, passwords or personal settings files.
