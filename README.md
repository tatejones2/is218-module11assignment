# IS218 Module 11 - Calculation API with Factory Pattern

## � Quick Links

- **GitHub Repository**: [tatejones2/is218-module11assignment](https://github.com/tatejones2/is218-module11assignment) (Your own code)
- **Docker Hub Repository**: [tatejones2/is218-module11](https://hub.docker.com/r/tatejones2/is218-module11) (Auto-built on push)

---

## 🧪 Running Tests Locally

### Prerequisites

Before running tests, ensure you have Python 3.10+ installed:

```bash
# Check Python version
python3 --version

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat # Windows

# Install dependencies
pip install -r requirements.txt
```

### Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only (Factory Pattern tests - 47 tests)
pytest tests/unit/ -v

# Run integration tests only (Database + Schema - 50+ tests)
pytest tests/integration/ -v

# Run with coverage report and HTML output
pytest tests/ -v --cov=app --cov-report=html

# Run specific test class
pytest tests/unit/test_factory.py::TestAdditionCalculator -v

# Run with detailed output
pytest tests/ -vv --tb=short
```

### Test Coverage Summary

- **Unit Tests**: 47 tests covering Factory Pattern and Calculator strategies
- **Integration Tests**: 16 database persistence tests + 40+ schema validation tests  
- **Total**: 99+ tests, all passing ✅
- **Code Coverage**: 76% overall, 85%+ on critical modules
- **Documentation**: See [TESTING.md](TESTING.md) for complete details

---

## 🐳 Using Docker

### Pull from Docker Hub

The Docker image is automatically built and pushed on every successful test run.

```bash
# Pull the latest image
docker pull tatejones2/is218-module11:latest

# Run the container with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@localhost:5432/myappdb \
  tatejones2/is218-module11:latest
```

### Using Tagged Versions

```bash
# Pull a specific version (by commit SHA)
docker pull tatejones2/is218-module11:e8f9240

# View all available tags
docker search tatejones2/is218-module11
```

### Build Locally

```bash
# Build the image locally
docker build -t is218-module11:latest .

# Run locally built image
docker run -p 8000:8000 -it is218-module11:latest
```

---

## 🔄 CI/CD Pipeline

GitHub Actions automatically:
- ✅ Runs all tests on every push
- ✅ Generates coverage reports
- ✅ Builds Docker image
- ✅ Runs security scan with Trivy
- ✅ Pushes to Docker Hub on success

---

## 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

## Local Development

- **Without Docker**:

```bash
python main.py
```

(or update this if the main script is different.)

- **With Docker** (local build):

```bash
docker build -t is218-module11 .
docker run -it --rm is218-module11
```

## Using Docker Hub Image

Pull and run the pre-built image from Docker Hub:

```bash
docker pull kaw393939/601_module9:latest
docker run -it --rm kaw393939/601_module9:latest
```

## Running Tests

See [🧪 Running Tests](#-running-tests) section at the top of this README.

---

# 📝 7. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

- Install **Homebrew** first on Mac.
- Install and configure **Git** and **SSH** before cloning.
- Use **Python 3.10+** and **virtual environments** for Python projects.
- **Docker** is optional depending on the project.

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
