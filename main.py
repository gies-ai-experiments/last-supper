"""
The Last Supper at Rosetti's - A Murder Mystery SQL Game
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from game.engine import GameEngine


load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="The Last Supper at Rosetti's - A Murder Mystery SQL Game"
    )
    parser.add_argument(
        "--no-typewriter",
        action="store_true",
        help="Disable typewriter effect for faster text display",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    )
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required.")
        print("Set OPENAI_API_KEY environment variable or pass --api-key")
        sys.exit(1)

    engine = GameEngine(
        api_key=api_key,
        typewriter=not args.no_typewriter,
    )

    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n\nCase suspended. The mystery remains unsolved...")
    finally:
        engine.cleanup()


if __name__ == "__main__":
    main()
