# Enterprise Engineering & Disaster-Recovery Reconstruction Specification

> **Standard Operating Procedure (SOP) & Reconstruction Manifest**  
> **Repository**: [`PainWorry/gps-ticket-generator`](https://github.com/PainWorry/gps-ticket-generator)  
> **Benchmark Standards**: Modeled after Google Engineering Practices, Google SRE Standards, and the Universal [Well-Document Playbook](https://github.com/PainWorry/HerrenK_skill.md).  
> **System Purpose**: Autonomous, client-side, zero-backend ticket generator for Dynamics 365 Support tickets and downstream automated GPS data sync runners.

---

## 1. Executive Summary & Problem Statement

### 1.1 Context
Customer Support (Tier 1 CS) routinely handles requests from clients requesting GPS location data reruns. Prior workflows required repetitive manual form entries and produced inconsistent clipboard text formatting (inconsistent field names, accidental character entries in numerical fields, lowercase casing, and copy-paste errors when multiple vehicles shared identical dates).

### 1.2 Delivered Engineering Improvements
1. **Strict Input Sanitization**:
   - `ticketNo` and `companyId`: Strictly numbers only (`/[^0-9]/g`).
   - `serverIp`: Valid IPv4 characters and dots (`/[^0-9.]/g`).
   - `mid`: Numeric characters, commas, semicolons, and spaces (`/[^0-9,;\s]/g`). Letters strictly rejected.
2. **Batch Multi-MID Parsing**:
   - Allows comma/space-separated batch input (e.g., `1111, 2222, 3333`) sharing the same date range without clicking `+ เพิ่ม` repeatedly.
   - Automatic deduplication and array expansion in both clipboard text and the machine-readable `[SYSTEM_DATA]` JSON payload.
3. **Field Standardization & Precedence**:
   - Capitalized `Company ID` and `Company Name` in the UI and clipboard text.
   - Strict precedence: If both `Company ID` and specific MIDs are provided, omit generic `"ALL"` placeholder lines from the clipboard output.

---

## 2. Disaster-Recovery Reconstruction Specification (Zero-Code AI Rebuild Standard)

If this repository and all hosting instances are completely destroyed, an autonomous AI agent or engineer can reconstruct the application using this specification.

### 2.1 Wire Formats & Data Contracts

#### Machine-Readable Tag: `[SYSTEM_DATA]`
Embedded at the end of the clipboard text output to allow lossless extraction by downstream automation:

```typescript
interface GPSTicketPayload {
  ticket_no?: string;          // Optional ticket number, e.g. "12345"
  ip: string;                 // Target PostgreSQL Database Server IP, e.g. "122.155.12.70"
  company_id?: string;        // Optional company ID, e.g. "888"
  requests: Array<{
    mid: string;              // Specific numeric MID (e.g. "1111") or "ALL"
    start: string;            // ISO-8601 Date string "YYYY-MM-DD"
    end: string;              // ISO-8601 Date string "YYYY-MM-DD"
  }>;
}
```

### 2.2 Golden Test Vectors (Ground Truth Pairs)

#### Test Case 1: Batch MIDs + Company ID
* **Input State**:
  - Ticket No: `9001`
  - Server IP: `122.155.12.70`
  - Server Name: `Onetrack`
  - Company ID: `555`
  - Company Name: `Bangkok Logistics`
  - MIDs Input: `101, 102, 103`
  - Start Date: `01/10/2026`
  - End Date: `05/10/2026`
* **Exact Clipboard Text Output**:
```text
รายละเอียด
เลข Ticket : 9001
Server Name : Onetrack
Server IP : 122.155.12.70
Company Name : Bangkok Logistics
Company ID : 555

MID : 101
วันที่ 01/10/2026 - 05/10/2026
MID : 102
วันที่ 01/10/2026 - 05/10/2026
MID : 103
วันที่ 01/10/2026 - 05/10/2026

[SYSTEM_DATA]
{"ticket_no":"9001","ip":"122.155.12.70","company_id":"555","requests":[{"mid":"101","start":"2026-10-01","end":"2026-10-05"},{"mid":"102","start":"2026-10-01","end":"2026-10-05"},{"mid":"103","start":"2026-10-01","end":"2026-10-05"}]}
[/SYSTEM_DATA]
```

#### Test Case 2: Entire Company (No MID Specified)
* **Input State**:
  - Server IP: `122.155.12.70`
  - Company ID: `888`
  - MID: *(Blank)*
  - Start Date: `12/10/2026`
  - End Date: `12/10/2026`
* **Exact Clipboard Text Output**:
```text
รายละเอียด
Server IP : 122.155.12.70
Company ID : 888

วันที่ 12/10/2026 - 12/10/2026

[SYSTEM_DATA]
{"ip":"122.155.12.70","company_id":"888","requests":[{"mid":"ALL","start":"2026-10-12","end":"2026-10-12"}]}
[/SYSTEM_DATA]
```

### 2.3 Hermetic Runtime Environment & Dependencies

| Component | Manifest Specification | Purpose |
| :--- | :--- | :--- |
| **Python Runtime** | `3.12` (pinned in `.python-version`) | Server container wrapper |
| **Streamlit Framework** | `streamlit>=1.30.0` (in `requirements.txt`) | Container presentation engine |
| **Frontend Runtime** | Standalone HTML5 / CSS3 / Vanilla ES6 (`cs_ticket_generator.html`) | 100% Client-side DOM computation |
| **Datepicker CDN** | Flatpickr `https://cdn.jsdelivr.net/npm/flatpickr` | Forced `dd/mm/yyyy` input without native browser variation |
| **Font Asset** | Google Fonts `https://fonts.googleapis.com/css2?family=Inter` | UI typography |

---

## 3. Standardized Problem-Fix-Learning Log

### [ISSUE RECORD #TICKET-001]
- **Date & Environment**: 2026-10-12 | Linux / Browser Client / HTML5
- **Summary**: Alphabetical characters permitted in MID field; generic `"ALL"` MID retained in output when company ID and specific MIDs both existed.
- **Severity**: Medium (Downstream Automation Extraction Distortion)

#### 1. Symptoms & Detection
- Tier 1 CS typed characters into numeric fields, causing downstream database SQL queries to error out.
- When selecting both a company ID and MIDs, clipboard text included unnecessary `วันที่ ...` under generic company rules, confusing Tier 2 engineers.

#### 2. Root Cause Analysis (RCA)
- **Why 1**: The `<input id="mid">` element did not enforce `inputmode` or input sanitization handlers.
- **Why 2**: The iteration logic over `midGroups` printed `dates.forEach(...)` unconditionally for the `"ALL"` key regardless of whether specific MIDs had already been recorded.

#### 3. Resolution & Patch
1. Added regex sanitization:
   ```javascript
   this.value = this.value.replace(/[^0-9,;\s]/g, '')
   ```
2. Refactored output loop to verify `hasSpecificMid` before outputting general company dates:
   ```javascript
   const hasSpecificMid = finalRequests.some(r => r.mid && r.mid !== "ALL");
   for (const [m, dates] of Object.entries(midGroups)) {
       if (m !== "ALL") {
           txt += `MID : ${m}\n`;
           dates.forEach(d => txt += `วันที่ ${d}\n`);
       } else if (!hasSpecificMid) {
           dates.forEach(d => txt += `วันที่ ${d}\n`);
       }
   }
   ```

#### 4. Key Learnings & Junior Guidance
- Always decouple UI entry from output serialization: sanitize inputs aggressively on keyup/input while ensuring multi-value delimiters (commas/spaces) are preserved for power users.
