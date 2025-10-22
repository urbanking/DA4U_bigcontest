# Headless Marketplace Automation

This folder contains the non-interactive (headless) runner for the Seoul marketplace (골목상권분석) automation.

## Quick start (Windows)

- One click (headless): double-click `상권분석_실행_headless.bat`
- Or run from a terminal:

```
cd /d %~dp0
set HEADLESS=1
set PLAYWRIGHT_MCP_HEADLESS=true
python 상권분석_자동화.py --headless --no-pause "왕십리역" "외식업" 500M
```

Notes:
- `--headless` disables browser UI. `--no-pause` removes `pause` at the end.
- Address/industry/radius are positional; omit industry/radius to use defaults.
- Outputs:
  - PNG screenshots: `.playwright-mcp`
  - PDF downloads: `상권분석리포트`

## How the backend uses headless

The backend wrapper (`wrappers/marketplace_wrapper.py`) now:
- Forces headless by default (unless `HEADLESS=0` is set)
- Passes `--headless --no-pause` flags to `상권분석_자동화.py`
- Sets `HEADLESS=1` in the child process environment
- Polls `.playwright-mcp` and copies results into `agents_new/test_output`

To temporarily show the browser (for debugging):

```
set HEADLESS=0
set PLAYWRIGHT_MCP_HEADLESS=false
python ..\wrappers\marketplace_wrapper.py "왕십리역"
```

Make sure your Gemini CLI and Playwright MCP are configured on this machine, and that your Anaconda path in the BAT file is valid.
