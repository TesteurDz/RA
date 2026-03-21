"""
Account Pool — Rotate between multiple Instagram accounts to avoid detection.
Each account does max DAILY_LIMIT requests/day with rotating IPs.
"""
from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

POOL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ig_accounts.json")
DAILY_LIMIT = 50  # Max requests per account per day


@dataclass
class AccountState:
    username: str
    password: str
    session_file: str = ""
    daily_count: int = 0
    last_reset: str = ""
    is_blocked: bool = False
    blocked_until: float = 0
    last_used: float = 0


class AccountPool:
    """Pool of Instagram accounts with automatic rotation."""

    def __init__(self):
        self.accounts: list[AccountState] = []
        self._current_index = 0
        self._load_pool()

    def _load_pool(self):
        """Load accounts from JSON file."""
        if not os.path.exists(POOL_FILE):
            logger.info(f"No account pool file at {POOL_FILE}")
            return
        try:
            with open(POOL_FILE, "r") as f:
                data = json.load(f)
            for acc in data.get("accounts", []):
                self.accounts.append(AccountState(
                    username=acc["username"],
                    password=acc["password"],
                    session_file=acc.get("session_file", ""),
                    daily_count=acc.get("daily_count", 0),
                    last_reset=acc.get("last_reset", ""),
                    is_blocked=acc.get("is_blocked", False),
                    blocked_until=acc.get("blocked_until", 0),
                ))
            logger.info(f"Loaded {len(self.accounts)} accounts in pool")
        except Exception as e:
            logger.error(f"Failed to load account pool: {e}")

    def _save_pool(self):
        """Save account states to JSON."""
        try:
            data = {"accounts": []}
            for acc in self.accounts:
                data["accounts"].append({
                    "username": acc.username,
                    "password": acc.password,
                    "session_file": acc.session_file,
                    "daily_count": acc.daily_count,
                    "last_reset": acc.last_reset,
                    "is_blocked": acc.is_blocked,
                    "blocked_until": acc.blocked_until,
                })
            with open(POOL_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save account pool: {e}")

    def _reset_daily_if_needed(self, acc: AccountState):
        """Reset daily counter if it's a new day."""
        today = date.today().isoformat()
        if acc.last_reset != today:
            acc.daily_count = 0
            acc.last_reset = today
            # Unblock if cooldown expired
            if acc.is_blocked and time.time() > acc.blocked_until:
                acc.is_blocked = False
                logger.info(f"Account {acc.username} unblocked after cooldown")

    def get_next_account(self) -> Optional[AccountState]:
        """Get next available account (not blocked, under daily limit)."""
        if not self.accounts:
            return None

        # Shuffle to randomize selection
        candidates = list(range(len(self.accounts)))
        random.shuffle(candidates)

        for idx in candidates:
            acc = self.accounts[idx]
            self._reset_daily_if_needed(acc)

            if acc.is_blocked:
                continue
            if acc.daily_count >= DAILY_LIMIT:
                continue

            acc.daily_count += 1
            acc.last_used = time.time()
            self._save_pool()
            return acc

        logger.warning("All accounts exhausted or blocked!")
        return None

    def mark_blocked(self, username: str, cooldown_hours: int = 2):
        """Mark an account as blocked with cooldown."""
        for acc in self.accounts:
            if acc.username == username:
                acc.is_blocked = True
                acc.blocked_until = time.time() + (cooldown_hours * 3600)
                logger.warning(f"Account {username} blocked for {cooldown_hours}h")
                self._save_pool()
                return

    def add_account(self, username: str, password: str) -> bool:
        """Add a new account to the pool."""
        # Check if already exists
        for acc in self.accounts:
            if acc.username == username:
                acc.password = password
                self._save_pool()
                return True

        session_dir = os.path.dirname(POOL_FILE)
        session_file = os.path.join(session_dir, f"ig_session_{username}.json")

        self.accounts.append(AccountState(
            username=username,
            password=password,
            session_file=session_file,
        ))
        self._save_pool()
        logger.info(f"Account {username} added to pool ({len(self.accounts)} total)")
        return True

    def get_stats(self) -> dict:
        """Get pool statistics."""
        for acc in self.accounts:
            self._reset_daily_if_needed(acc)

        return {
            "total_accounts": len(self.accounts),
            "available": sum(1 for a in self.accounts if not a.is_blocked and a.daily_count < DAILY_LIMIT),
            "blocked": sum(1 for a in self.accounts if a.is_blocked),
            "exhausted": sum(1 for a in self.accounts if a.daily_count >= DAILY_LIMIT),
            "total_requests_today": sum(a.daily_count for a in self.accounts),
            "max_capacity_today": len(self.accounts) * DAILY_LIMIT,
            "accounts": [
                {
                    "username": a.username,
                    "daily_count": a.daily_count,
                    "is_blocked": a.is_blocked,
                    "available": not a.is_blocked and a.daily_count < DAILY_LIMIT,
                }
                for a in self.accounts
            ],
        }


# Singleton
pool = AccountPool()
