#!/usr/bin/env python3

import os
import sys
import time
import itertools
import hashlib

ASCII_ART = r"""
=====================================
██╗  ██╗ █████╗ ███████╗██╗  ██╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║███████╗███████║██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║╚════██║██╔══██║██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║███████║██║  ██║╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
     By jsnulled (https://github.com/jsnulled)
=====================================
"""

CHARSETS = {
    "1": "abcdefghijklmnopqrstuvwxyz0123456789",
    "2": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#",
    "3": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
}


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def loading_bar(message, duration=1.5, steps=20):
    print(f"\n{message}")
    for i in range(steps):
        time.sleep(duration / steps)
        bar = '#' * (i + 1) + '-' * (steps - i - 1)
        sys.stdout.write(f"\r[{bar}]")
        sys.stdout.flush()
    print("\n")


def is_valid_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def detect_hash_type(hash_str):
    if not is_valid_hex(hash_str):
        return None

    return {
        32: "MD5",
        40: "SHA-1",
        64: "SHA-256",
        128: "SHA-512"
    }.get(len(hash_str))


def hash_word(word, hash_type):
    encoded = word.encode()

    if hash_type == "MD5":
        return hashlib.md5(encoded).hexdigest()
    elif hash_type == "SHA-1":
        return hashlib.sha1(encoded).hexdigest()
    elif hash_type == "SHA-256":
        return hashlib.sha256(encoded).hexdigest()
    elif hash_type == "SHA-512":
        return hashlib.sha512(encoded).hexdigest()

    return None


def brute_force(target_hash, prefix, max_len, charset, hash_type):
    start_time = time.time()
    attempts = 0
    prefix_len = len(prefix)

    for length in range(prefix_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length - prefix_len):
            word = prefix + ''.join(combo)
            attempts += 1

            if attempts % 100000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                sys.stdout.write(f"\rTried: {attempts:,} | {rate:.0f}/sec")
                sys.stdout.flush()

            if hash_word(word, hash_type) == target_hash:
                print()
                return word, time.time() - start_time

    return None, time.time() - start_time


def main():
    clear()
    print(ASCII_ART)

    try:
        target_hash = input("Paste hash: ").strip().lower()
        prefix = input("Prefix (optional): ").strip()

        length_input = input("Max length (default 6): ").strip()
        max_len = int(length_input) if length_input.isdigit() else 6

        if max_len <= 0:
            print("Length must be greater than 0.")
            return

        print("\nSelect charset:")
        print("1. Limited")
        print("2. Standard")
        print("3. Full")

        charset_choice = input("> ").strip()
        if charset_choice not in CHARSETS:
            print("Invalid option.")
            return

        charset = CHARSETS[charset_choice]

    except KeyboardInterrupt:
        print("\nExiting...")
        return

    hash_type = detect_hash_type(target_hash)
    if not hash_type:
        print("Invalid or unsupported hash.")
        return

    loading_bar("Starting brute force...")

    result, elapsed = brute_force(target_hash, prefix, max_len, charset, hash_type)

    print("\n========== RESULT ==========")
    print(f"Hash: {target_hash}")
    print(f"Result: {result if result else 'Not found'}")
    print(f"Time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()