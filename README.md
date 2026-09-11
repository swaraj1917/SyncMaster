# SyncMaster 🧵

A hands-on simulator for OS-level thread synchronization — mutexes, semaphores, deadlocks, and race conditions, visualized live. Try it instantly in your browser, no installation needed.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

### 🔗 [Try it live — no install needed](https://syncmaster-ho1x.onrender.com)

*(Free hosting tier — the first load may take 20–30 seconds to wake up if it's been idle.)*

---

## 🎯 Problems Implemented

| Problem | Description |
| --- | --- |
| **Producer-Consumer** | Bounded buffer with Mutex + Semaphores |
| **Dining Philosophers** | Deadlock-free with asymmetric fork acquisition (plus a naive mode that deliberately deadlocks) |
| **Reader-Writer** | Reader-preferring with a `read_count` mutex |

---

## ✨ Features

- 🎨 **Animated Visualizations** — Live buffer boxes, philosopher circles, reader/writer slots
- 📊 **Real-time Throughput Graphs** — Powered by matplotlib
- ⏸️ **Pause / Resume / Stop** — Full control over running simulations
- ⚠️ **Deadlock Demo Mode** — Watch the classic deadlock happen live
- 🎚️ **Speed Control** — Slow down or speed up any simulation
- 🧪 **Unit Tests + Stress Tests** — Concurrent correctness verification

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/SyncMaster.git
cd SyncMaster
pip install -r requirements.txt
```

### Run the GUI

```bash
python gui.py
```

### Run the CLI version

```bash
python main.py
```

The CLI runs each problem with a small set of default parameters (e.g. 5 philosophers, a buffer size of 5) — it's meant as a quick text-only demo. Use the GUI for adjustable parameters and live visualizations.

### Run the tests

```bash
python -m unittest discover -s tests -v
```

---

## 📸 Screenshots

### Producer-Consumer

![Producer-Consumer](docs/producer_consumer.png)

### Dining Philosophers

![Dining Philosophers](docs/dining_philosophers.png)

### Reader-Writer

![Reader-Writer](docs/reader_writer.png)

---

## 🏗️ Project Structure

```text
SyncMaster/
├── main.py                    # CLI entry point
├── gui.py                     # Tkinter GUI
├── requirements.txt
├── .gitignore
├── primitives/                # Custom sync primitives
│   ├── __init__.py
│   ├── mutex.py
│   ├── semaphore.py
│   └── condition_variable.py
├── problems/                  # The three problems
│   ├── __init__.py
│   ├── producer_consumer.py
│   ├── dining_philosopher.py
│   └── reader_writer.py
├── utils/
│   ├── __init__.py
│   ├── control.py             # Pause/Stop controller
│   └── logger.py
└── tests/
    ├── __init__.py
    ├── test_mutex.py
    ├── test_semaphore.py
    ├── test_conditionalvar.py
    ├── test_prodconsum.py
    ├── test_diningphil.py
    └── test_readwrite.py
```

---

## 🧠 Concepts Demonstrated

- Mutual exclusion with **Mutex**
- Counting synchronization with **Semaphore**
- Signaling with **Condition Variables**
- **Deadlock** prevention via asymmetric lock ordering (and a naive mode that shows the deadlock itself)
- **Race conditions** and how to eliminate them
- Thread lifecycle: running / blocked / waiting

---

## 🧪 Testing

The project includes:

- **Unit tests** for each primitive
- **Integration tests** for each problem
- **Stress tests** verifying correctness under many concurrent operations

Running the tests will generate a local `.pytest_cache/` folder if you use `pytest` instead of `unittest` — this is already excluded via `.gitignore` and should never be committed.

---

## 📄 License

MIT