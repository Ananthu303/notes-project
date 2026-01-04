# Real-Time Collaborative Notes App

## Objective
Build a real-time collaborative notes application with features including live updates, version control, and multi-user collaboration. The project leverages Django REST Framework, Redis, and Django Channels to provide a responsive, collaborative experience.

---

## Tech Stack
- **Backend Framework:** Django + Django REST Framework (DRF)  
- **Real-Time Communication:** Django Channels (WebSockets)  
- **Caching & Messaging:** Redis  
- **Database:**   SQLite3
- **Authentication:** JWT Authentication  

---

## Features

### 1. User Authentication
- Users can register and log in using JWT authentication.  
- Each user can create, edit, and share notes.  

### 2. Notes Management
- Each note includes:
  - **Title**
  - **Content**
  - **Owner**
  - **Last updated timestamp**
- Notes can be shared with multiple collaborators using a Many-to-Many relationship with the User model.

### 3. Versioning & Pagination
- Every note update creates a new version while preserving previous versions.  
- Custom paginated API to retrieve version history, sorted with the most recent version first.  
- Redis caching improves response time for frequently accessed recent versions.

### 4. Real-Time Collaboration
- Live updates via WebSockets whenever a note is modified by any collaborator.  
- Typing indicators show when a user is editing a note.
---

---

## Installation

1. Clone the repository:  
```bash
git clone https://github.com/Ananthu303/notes-project.git
cd collab_notes
```

2. Create a virtual environment and activate it:  
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:  
```bash
pip install -r requirements.txt
```

4. Set up the database:  
```bash
python manage.py migrate
```

5. Start Redis server (for caching and Channels backend).

6. Create Superuser (Super Admin)

You need to create a superuser.
Run the following command to create the superuser:

```bash
python manage.py createsuperuser
```

You will be prompted to enter the following information:

- Username
- Email
- Password

This superuser is the SUPERADMIN having full control over the system

### 7. Run the Development Server

Once everything is set up, you can run the server:

**Django's development server:**
```bash
python manage.py runserver
```

**Run Daphne ASGI server in another terminal:**
```bash
daphne -b 0.0.0.0 -p 8001 collab_notes.asgi:application
```
---

## Testing Instructions

Follow these step-by-step instructions to test the collaborative notes application:

### Step 1: Log in using superuser credentials

1. Obtain your superuser credentials (created during installation).
2. Make a POST request to the token authentication endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_superuser_username",
    "password": "your_superuser_password"
  }'
```

Or using a tool like Postman or HTTPie:
- **URL:** `POST http://127.0.0.1:8000/api/token/`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "username": "your_superuser_username",
    "password": "your_superuser_password"
  }
  ```

3. Save the `access` token from the response. You'll need it for subsequent API calls.

**Example Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 2: Create two new users

1. Create the first user:

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_ACCESS_TOKEN" \
  -d '{
    "username": "user1",
    "email": "user1@example.com",
    "password": "securepassword123"
  }'
```

2. Create the second user:

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_ACCESS_TOKEN" \
  -d '{
    "username": "user2",
    "email": "user2@example.com",
    "password": "securepassword123"
  }'
```

3. Save the `id` values from both user creation responses. You'll need these IDs to assign them as collaborators.

**Example Response:**
```json
{
  "id": 2,
  "username": "user1",
  "email": "user1@example.com"
}
```

### Step 3: Create a note via the Notes API and assign collaborators

1. Using the superuser's access token, create a note and assign the two newly created users as collaborators:

```bash
curl -X POST http://127.0.0.1:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_ACCESS_TOKEN" \
  -d '{
    "title": "Test Collaborative Note",
    "content": "This is a test note for collaboration.",
    "collaborators": [USER1_ID, USER2_ID]
  }'
```

Replace `USER1_ID` and `USER2_ID` with the actual IDs from Step 2.

**Example:**
```json
{
  "title": "Test Collaborative Note",
  "content": "This is a test note for collaboration.",
  "collaborators": [2, 3]
}
```

2. Save the `id` of the created note from the response. You'll need it to access the note's index page.

**Example Response:**
```json
{
  "id": 1,
  "title": "Test Collaborative Note",
  "content": "This is a test note for collaboration.",
  "owner": 1,
  "collaborators": [2, 3],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Step 4: Ensure new users can log in using token authentication

1. Test login for the first user:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "securepassword123"
  }'
```

2. Test login for the second user:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user2",
    "password": "securepassword123"
  }'
```

3. Save the `access` tokens for both users. You'll need these tokens to connect to the WebSocket.

### Step 5: Open the note's index page by ID and using access token for connection

1. Using a collaborator's access token (user1 or user2), access the note's index page:

**URL:** `http://127.0.0.1:8000/api/note-index/NOTE_ID/`

Replace `NOTE_ID` with the note ID from Step 3.

**Example:** `http://127.0.0.1:8000/api/note-index/1/`


### Step 6: Test real-time features

1. **Typing Indicators:**
   - Open the note's index page in two different browser windows/tabs (or use two different browsers).
   - Log in as different collaborators (user1 in one window, user2 in another).
   - Start typing in one window. The other window should display a typing indicator showing that a user is currently editing the note.

2. **Live Updates:**
   - With both collaborators connected via WebSocket:
     - Have one user make changes to the note (edit title or content).
     - The other user should see the changes appear in real-time without refreshing the page.
     - Test updating the note via the API:

```bash
curl -X PATCH http://127.0.0.1:8000/api/notes/NOTE_ID/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content with real-time sync."
  }'
```

   - The connected collaborators should see the update appear automatically in their browser windows.

3. **Version History:**
   - After making updates, you can view the version history:

```bash
curl -X GET http://127.0.0.1:8000/api/notes/NOTE_ID/versions/?page=1 \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

---

## API Endpoints Summary

- **Token Authentication:** `POST /api/token/`
- **Token Refresh:** `POST /api/token-refresh/`
- **Users:** `GET/POST /api/users/`
- **Notes:** `GET/POST/PATCH/DELETE /api/notes/`
- **Note Versions:** `GET /api/notes/<note_id>/versions/`
- **Note Index Page:** `GET /api/note-index/<note_id>/`
---

