# Dummy Chatbot

A small Python/Tkinter scaffold for a future chatbot. The modules are connected
and runnable, with deliberately minimal placeholder responses so you can add your
own logic. Everything stays in memory and is discarded when a chat is closed.

## Run

Use Python 3.10 or later with Tkinter available. No pip dependencies are needed.

On Windows, from `chatbot_app`, launch the GUI with:

```powershell
.\run.cmd
```

The launcher checks for a project virtual environment, the Windows Python
launcher (`py`), and Python on PATH. On this machine it can also use the Python
runtime bundled with Codex, so the Microsoft Store `python` shortcut does not
prevent you from running the app. It does not install anything or change PATH.

If `python` already works, you can also run this from the repository directory:

```shell
cd chatbot_app
python main.py
```

The main menu offers **Start Chat** and **What can this chatbot do?**. Both open
the same chat screen with a new session; the second starts with an introduction.
Type a message and press **Send** or Enter for a dummy echo. **Back** returns to
the menu. Each new chat has its own ID, context, and message history.

To check Tkinter, run `python -m tkinter`. If it is unavailable, install the
Tcl/Tk component supplied by your Python installer or operating system.

## Structure and extension points

```text
main.py                         Window creation and event loop
app/
  ui/main_screen.py             Main menu, navigation, component wiring
  ui/chat_screen.py             Message display and input
  chat/chat_controller.py       Greeting and message flow
  chat/chat_session.py          Session ID, context, message history
  chat/chat_context.py          Generic per-session key/value storage
  logic/chatbot_engine.py       Stub response generation
  logic/rules.py                Placeholder for deterministic rules
  models/message.py             Message dataclass with timestamp
tests/                          Standard-library unit and wiring tests
```

The flow is `UI -> ChatController -> ChatSession / ChatbotEngine -> rules`.
The session owns its context and messages. UI code never generates replies.

Start implementing responses in `ChatbotEngine.process_message(text, context)`.
It calls `apply_rules(text, context)` first; a `None` result falls back to the
dummy echo. Put deterministic rules in `rules.py` and session data in
`ChatContext`. To use a different engine object, wire it into `MainScreen.start_chat`
with the same `process_message` interface. Change the opening messages in
`ChatController.start_session`.

There is no AI integration, domain logic, networking, authentication, database,
or persistent history.

## Test

On Windows, from `chatbot_app`:

```powershell
.\run.cmd test
```

This runs the unit tests; `.\run.cmd` without `test` opens the GUI.
With Python already on PATH, the equivalent test command is:

```shell
python -m unittest discover -s tests -v
```

These tests exercise context storage, session isolation, the engine, and the
controller's message flow without opening a GUI.
