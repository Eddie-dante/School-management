# SRMS - School Resource Management System

A full-featured web application for managing school resources: library books, furniture, students, teachers, and internal staff communication. Built with **Streamlit** and powered by **Supabase** (PostgreSQL).

**Created by WeGEM (Edwin)**

---

## ✨ Features

- 🏫 **School Management** – Create and manage multiple schools with invite codes.
- 👥 **Staff Authentication** – Role‑based access (admin, teacher, librarian).
- 📚 **Library Management** – Book catalog, bulk/individual lending, returns, overdue tracking.
- 🪑 **Furniture Allocation** – Assign chairs and lockers to students per class.
- 📋 **Class Lists** – Import student rosters from Excel files.
- 📊 **Dashboard & Reports** – Real‑time stats, charts, and analytics.
- 💬 **Private Chat** – Staff messaging with file/emoji support.
- 📢 **Group Forum** – School‑wide announcements.
- 📝 **Shared Notepad** – Collaborative notes.
- 📱 **QR Code Generator** – For books, chairs, lockers.
- 🎨 **100+ Background Wallpapers** – Customizable UI themes.
- 🔐 **Audit Log** – Track all actions (admin only).
- 💾 **Backup & Restore** – Export/import data as JSON.

---

## 🛠️ Tech Stack

| Layer          | Technology                         |
|----------------|------------------------------------|
| Frontend       | Streamlit                          |
| Backend / DB   | Supabase (PostgreSQL)              |
| Data Analysis  | Pandas, Plotly                     |
| Authentication | SHA‑256 password hashing           |
| QR Codes       | qrcode + Pillow                    |
| Excel Export   | openpyxl, base64                   |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/srms.git
cd srms
