---
created: '2024-12-29'
lastmod: '2024-12-29'
tags:
  - Python
  - pdga
  - disc golf
  - api
  - scraper
---

# PDGA Data

A Python ETL pipeline application designed to extract, transform, and load data from [PDGA.com](https://pdga.com), focusing on public data related to discs, companies, players, and events.

![Build Status](https://img.shields.io/github/actions/workflow/status/DuaneR5280/pdga-data/main.yml)
![License](https://img.shields.io/github/license/yourusername/pdga-data)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Extract](#extract)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**PDGA Data** is an ETL (Extract, Transform, Load) pipeline application built in Python. It is designed to collect data from the Professional Disc Golf Association (PDGA) website and APIs, process it, and use it for further analysis or use in other applications.

---

## Features

- 🥏 Extract disc data, company, player stats, and event information from PDGA.
- 🛠 Transform data into structured formats for easier analysis.
- 💾 Load data into a database for persistence and queryability.
- 📊 Suitable for data visualization and analytics pipelines.

---

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/DuaneR5280/pdga-data.git
   cd pdga-data
