# Napster-Style Peer-to-Peer (P2P) File Sharing App

## Overview
A **Napster-style P2P file-sharing** application allows users to share and download files directly from other users over a network. Unlike centralized cloud storage, this system relies on a **hybrid P2P model** where a central index server keeps track of available files, and peer nodes (clients) communicate directly for file transfers.

## Features
### 1. **User Authentication (Optional)**
   - Users can sign in with a username.
   - Authentication can be kept simple (e.g., a local database or file storage).

### 2. **File Indexing System**
   - A **centralized server** maintains a database of available files and their corresponding peers.
   - Each client registers its shared files with the central server upon connection.
   - Clients can search for files using keywords.

### 3. **Peer Discovery**
   - When a user searches for a file, the central server returns a list of peers that have the requested file.

### 4. **Direct Peer-to-Peer File Transfer**
   - Once a peer is identified, file transfer happens **directly between peers** using TCP sockets.
   - If multiple peers have the same file, the client can choose the fastest/nearest one.

### 5. **Resumable Downloads**
   - Files can be downloaded in chunks.
   - If a connection is interrupted, it can resume from where it stopped.

### 6. **Download Prioritization & Queueing**
   - Users can prioritize downloads and queue multiple files.

### 7. **Basic Chat/Notification System (Optional)**
   - Users can send basic messages or notifications (e.g., "File shared successfully").

### 8. **Security & Permissions**
   - Basic encryption for metadata.
   - Users can control what files they share.
   - Restrict access to sensitive directories.

---

## Application Flow
### **1. User Connection to Central Server**
1. A client starts and connects to the **central index server**.
2. The client registers its shared files with the server.
3. The server stores the list of available files and the IP addresses of peers sharing them.

### **2. Searching for a File**
1. A user searches for a file by sending a query to the central server.
2. The central server checks its database and returns a **list of peers** that have the file.

### **3. Establishing a Peer-to-Peer Connection**
1. The client selects a peer from the list and **requests the file directly** via a TCP socket connection.
2. The peer verifies the request and begins streaming the file in chunks.
3. The receiving client **assembles the file** as chunks are received.

### **4. Handling File Transfers & Resumable Downloads**
1. If a download is interrupted, the client can request the remaining chunks.
2. If multiple peers have the file, the client can **switch to another peer** in case of failure.

### **5. Updating File Index**
1. When a user disconnects, their files are removed from the central index.
2. When a user adds new files, they notify the central server to update the database.

---

## Technical Stack
### **Backend (Central Server)**
- **Language**: Python (Flask/FastAPI) or Node.js
- **Database**: SQLite or PostgreSQL (for indexing files and peer details)
- **Networking**: TCP sockets for client-server communication

### **Client (Peer Node)**
- **Language**: Python (Socket programming)
- **Networking**: TCP sockets for file transfer
- **Storage**: Local filesystem for storing and managing shared/downloaded files
- **UI**: Simple CLI-based or lightweight GUI (Tkinter/PyQt)

---

## Future Enhancements
- **Decentralized Model**: Removing the central index server for a fully decentralized network.
- **Blockchain Integration**: Using smart contracts for tracking file-sharing history.
- **Improved Security**: Implementing end-to-end encryption for file transfers.
- **Web Interface**: Allowing users to share/download files through a web-based UI.

---

This document provides a structured guide to developing a **Napster-style P2P file-sharing app** using TCP sockets, aligning with the user's interest in software testing, automation, and embedded C/C++. 🚀


##Implementation Steps:


**1. Setup Central Server**
       
    python p2p_server.py

**2. First Peer (Terminal 1)**
       
    mkdir shared downloads

    echo "Hello from Peer 1" > shared/file1.txt

    python p2p_client.py

**3. Second Peer (Terminal 2)**

    mkdir shared downloads

    echo "Hello from Peer 2" > shared/file2.txt

    python p2p_client.py
