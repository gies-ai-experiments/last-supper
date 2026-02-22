# The Last Supper at Rosetti's

A murder mystery SQL game powered by OpenAI.

## Prerequisites

- Python 3.11+
- An OpenAI API key

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/gies-ai-experiments/last-supper.git
   cd last-supper
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create your environment file from the template:

   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and set your API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-5.2
   ```

## Run

Start the game:

```bash
python main.py --no-typewriter
```

You can also pass the API key directly:

```bash
python main.py --api-key "your_openai_api_key_here" --no-typewriter
```

## Notes

- `.env` is ignored by git and should never be committed.
- If you change dependencies, reinstall with `pip install -r requirements.txt`.
