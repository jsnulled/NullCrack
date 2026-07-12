# HashCracker

A minimalistic CLI open-source free Python-based hash cracking tool that supports multiple hash types and attack methods.

## Description

HashCracker is a CLI tool designed for testing security. It can crack various hash types including MD5, SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512 using brute force, wordlist attacks, or a built-in rainbow table of common passwords.

## Features

- **Multi-hash support**: MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
- **Multiple attack modes**: Brute force, wordlist, and rainbow table
- **7 character sets**: From numeric-only to full special characters
- **Multi-threaded brute force**: Speed up cracking with parallel processing
- **Automatic hash detection**: Identifies hash type by length
- **Progress display**: Real-time attempt counter and rate

## Installation

No external dependencies required. Uses only Python standard library.

```bash
# Clone or download the script
python3 hashcracker.py --help
```

## Usage

### Basic Usage

```bash
# Crack a hash (interactive mode)
python3 hashcracker.py

# Crack with command-line arguments
python3 hashcracker.py -H <hash>

# Crack with rainbow table first
python3 hashcracker.py -H <hash> -r

# Crack with specific max length
python3 hashcracker.py -H <hash> -m 8

# Crack with specific character set
python3 hashcracker.py -H <hash> -c 1

# Use wordlist attack
python3 hashcracker.py -H <hash> -w /path/to/wordlist.txt

# Use multi-threading
python3 hashcracker.py -H <hash> -t 4
```

## Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--hash` | `-H` | Target hash to crack | (required) |
| `--prefix` | `-p` | Known prefix for the password | (empty) |
| `--max-length` | `-m` | Maximum password length to try | 6 |
| `--charset` | `-c` | Character set to use (1-7) | 2 |
| `--threads` | `-t` | Number of threads for brute force | 1 |
| `--wordlist` | `-w` | Path to wordlist file | (none) |
| `--rainbow` | `-r` | Try built-in rainbow table first | False |
| `--info` | `-i` | Show supported hash types | - |
| `--list-charsets` | `-l` | List available character sets | - |

## Character Sets

| ID | Description | Characters |
|----|-------------|------------|
| 1 | Lowercase + Numbers | `abcdefghijklmnopqrstuvwxyz0123456789` |
| 2 | Alphanumeric + Basic Symbols | `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#` |
| 3 | Full Character Set | `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'",.<>?/` |
| 4 | Numeric Only | `0123456789` |
| 5 | Lowercase Only | `abcdefghijklmnopqrstuvwxyz` |
| 6 | Uppercase Only | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| 7 | Hex Characters | `0123456789abcdef` |

## Supported Hash Types

| Hash Type | Length |
|-----------|--------|
| MD5 | 32 characters |
| SHA-1 | 40 characters |
| SHA-224 | 56 characters |
| SHA-256 | 64 characters |
| SHA-384 | 96 characters |
| SHA-512 | 128 characters |

## Examples

```bash
# View help
python3 hashcracker.py --help

# View supported hash types
python3 hashcracker.py --info

# View character sets
python3 hashcracker.py --list-charsets

# Crack MD5 hash of "password"
python3 hashcracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -r

# Crack SHA-256 hash with numeric charset, max 4 chars
python3 hashcracker.py -H 7110eda4d09e062aa5e4a390b0a572ac0d2c0220 -c 4 -m 4 -r

# Crack with wordlist
python3 hashcracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w rockyou.txt
```

## Disclaimer

**This tool is for educational and authorized security testing purposes only.**

- Do not use this tool to crack passwords you do not own or have explicit permission to test
- Unauthorized access to accounts or systems is illegal
- The author is not responsible for any misuse of this tool
- Always obtain proper authorization before testing password security
- This tool should only be used on systems you own or have written permission to test

## License

This project is licensed under GNU Affero General Public License v3.0 (see LICENSE file). Use responsibly.
