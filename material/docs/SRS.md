# Software Requirements Specification

| Field | Detail |
|---|---|
| **Project** | JobRadar - Australian Job Market Analytics Pipeline |
| **Version** | 1.0 |
| **From** | 2026-03-01 |
| **Author** | Kiet Nguyen |
| **Status** | Coding |

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Objectives & Goals](#2-objectives--goals)
3. [Tech Stack](#3-tech-stack)
4. [Data Source](#4-data-source)
5. [System Architecture & Flow](#5-system-architecture--flow)
6. [Model](#6-model)
7. [Pipeline Schedule](#7-pipeline-schedule)
8. [Folder Structure](#8-folder-structure)

---

## 1. Project Overview

**JobRadar** is a data engineering portfolio project that collects, processes, stores, and visualises Australian job market data. The system ingests job listings daily from the Adzuna REST API, transforms and enriches the data using Python and dbt Cloud, stores it in Snowflake, and presents insights via Power BI dashboards.

| Field | Detail |
|---|---|
| **Project Name** | JobRadar |
| **Target Market** | Australian job market (nationwide) |
| **Data Source** | Adzuna AU — Official public REST API (free tier) |
| **Purpose** | Personal learning & portfolio showcase |

---

## 2. Objectives & Goals

### Primary Goals

1. Build a fully automated end-to-end data pipeline for job market data
2. Track salary trends over time by role and industry
3. Identify in-demand skills using NLP on job descriptions
4. Analyse job volume by location across Australia
5. Monitor hiring trends over time across industries

### Success Criteria

- Pipeline runs daily without bug or failure for 30 consecutive days

---

## 3. Tech Stack

| Layer | Tool | Purpose | Cost |
|---|---|---|---|
| Data Source | Adzuna REST API | Job listings data | Free |
| Ingestion | Python 3.11 | Extract, transform, load | Free |
| Orchestration | GitHub Actions | Pipeline scheduling (2000 min/month) | Free |
| Data Warehouse | Snowflake | Cloud data warehouse | Updating |
| Transformation | dbt Cloud | SQL models, tests, docs | Free tier |
| Visualisation | Power BI Desktop | Dashboards & reports | Free |
| | Power BI Service | Publishing & sharing | Updating |
| Alerting | Gmail | Failure notifications | Free |
| Version Control | GitHub | Code & raw data archive | Free |

---

## 4. Data Source

| Field | Detail |
|---|---|
| **Platform** | Adzuna Australia (https://www.adzuna.com.au) |
| **API Type** | RESTful JSON API |
| **Auth Method** | App ID + App Key (register free at developer.adzuna.com) |
| **Base URL** | `https://api.adzuna.com/v1/api/jobs/au/` |

---

## 5. System Architecture & Flow

![Flowchart](../diagram/Flowchart.png)
`Last Updated: 2026-03-19`
---

## 6. Model

### Snowflake Schema Structure

```
Updating
```

---

## 7. Pipeline Schedule

| Field | Value |
|---|---|
| **Schedule** | Updating |
| **Cron expression** | Updating |
| **Manual trigger** | `workflow_dispatch` via GitHub UI or API |

### Step-by-step Execution

```
Updating
```

---

## 8. Folder Structure

```
Updating
```

---

*JobRadar SRS v1.0 — Prepared for portfolio & development reference*