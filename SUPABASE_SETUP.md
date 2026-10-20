# 🏋️ RV Fitness — Supabase Setup Guide

Follow these steps to set up the Supabase backend for this project.

---

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) → **New Project**
2. Pick an org, give it a name (e.g. `rv-fitness`), set a **strong database password** (save it!), and choose a region close to you (e.g. `ap-south-1` for India)
3. Wait for provisioning (~2 min)

---

## Step 2: Grab Your Environment Variables

Once the project is ready, go to **Project Settings → API** (left sidebar → ⚙️ Settings → API).

| What to copy | Where in Supabase | Goes into |
|---|---|---|
| **Project URL** | `Settings → API → Project URL` | `SUPABASE_URL` / `VITE_SUPABASE_URL` |
| **anon (public) key** | `Settings → API → Project API keys → anon` | `SUPABASE_ANON_KEY` / `VITE_SUPABASE_ANON_KEY` |
| **service_role key** | `Settings → API → Project API keys → service_role` | `SUPABASE_SERVICE_ROLE_KEY` |
| **JWT Secret** | `Settings → API → JWT Settings → JWT Secret` | `SUPABASE_JWT_SECRET` |
| **Database connection string** | `Settings → Database → Connection string → URI` | `DATABASE_URL` |

> ⚠️ For `DATABASE_URL`, replace `[YOUR-PASSWORD]` in the URI with the database password you set when creating the project.

### Create the `.env` files

**Backend** — copy `backend/.env.example` → `backend/.env` and fill in:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
DATABASE_URL=postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
SUPABASE_JWT_SECRET=your-jwt-secret-from-dashboard
APP_ENV=development
SECRET_KEY=any-random-string
```

**Frontend** — copy `frontend/.env.example` → `frontend/.env` and fill in:
```env
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_API_BASE_URL=http://localhost:8000
```

---

## Step 3: Create the Database Tables

Go to **SQL Editor** in the Supabase Dashboard (left sidebar) and run the following SQL in **one batch**:

```sql
-- =============================================
-- RV Fitness — Full Schema
-- Run this in Supabase SQL Editor
-- =============================================

-- 1. Custom ENUM types
CREATE TYPE user_role AS ENUM ('admin', 'trainer', 'member');
CREATE TYPE trainer_status AS ENUM ('active', 'inactive');
CREATE TYPE member_status AS ENUM ('pending', 'active', 'inactive');
CREATE TYPE gender_enum AS ENUM ('male', 'female', 'other');
CREATE TYPE membership_status AS ENUM ('active', 'expired', 'cancelled');
CREATE TYPE invoice_status AS ENUM ('pending', 'partially_paid', 'paid', 'overdue', 'cancelled');
CREATE TYPE payment_method AS ENUM ('cash', 'upi', 'bank_transfer', 'card', 'other');
CREATE TYPE notice_audience AS ENUM ('all', 'members', 'trainers');
CREATE TYPE notice_status AS ENUM ('active', 'archived');
CREATE TYPE event_status AS ENUM ('upcoming', 'completed', 'cancelled');
CREATE TYPE gym_status_enum AS ENUM ('OPEN', 'CLOSED', 'HOLIDAY', 'TEMPORARILY CLOSED');

-- 2. profiles (mirrors Supabase auth.users)
CREATE TABLE profiles (
    id          TEXT PRIMARY KEY,
    full_name   VARCHAR(200) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    role        user_role NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. trainers
CREATE TABLE trainers (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    profile_id      TEXT UNIQUE NOT NULL REFERENCES profiles(id),
    mobile          VARCHAR(10) NOT NULL,
    experience      VARCHAR(255),
    specialization  VARCHAR(255),
    status          trainer_status NOT NULL DEFAULT 'active',
    photo_url       TEXT
);

-- 4. members
CREATE TABLE members (
    id                TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    member_code       VARCHAR(20) UNIQUE NOT NULL,
    profile_id        TEXT UNIQUE NOT NULL REFERENCES profiles(id),
    dob               DATE,
    gender            gender_enum,
    mobile            VARCHAR(10) NOT NULL,
    address           TEXT,
    emergency_contact VARCHAR(200),
    joining_date      DATE NOT NULL,
    status            member_status NOT NULL DEFAULT 'pending',
    trainer_id        TEXT REFERENCES trainers(id),
    weight            NUMERIC(5,2),
    height            NUMERIC(5,2),
    photo_url         TEXT
);

-- 5. membership_plans
CREATE TABLE membership_plans (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name            VARCHAR(200) NOT NULL,
    duration_days   INTEGER NOT NULL,
    price           NUMERIC(10,2) NOT NULL,
    description     TEXT,
    benefits        TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- 6. memberships
CREATE TABLE memberships (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    member_id   TEXT NOT NULL REFERENCES members(id),
    plan_id     TEXT NOT NULL REFERENCES membership_plans(id),
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL,
    status      membership_status NOT NULL DEFAULT 'active'
);

-- 7. invoices
CREATE TABLE invoices (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    invoice_no      VARCHAR(50) UNIQUE NOT NULL,
    member_id       TEXT NOT NULL REFERENCES members(id),
    membership_id   TEXT REFERENCES memberships(id),
    issue_date      DATE NOT NULL,
    due_date        DATE NOT NULL,
    amount          NUMERIC(10,2) NOT NULL,
    discount        NUMERIC(10,2) NOT NULL DEFAULT 0,
    tax             NUMERIC(10,2) NOT NULL DEFAULT 0,
    final_amount    NUMERIC(10,2) NOT NULL,
    status          invoice_status NOT NULL DEFAULT 'pending'
);

-- 8. invoice_items
CREATE TABLE invoice_items (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    invoice_id  TEXT NOT NULL REFERENCES invoices(id),
    description VARCHAR(300) NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1,
    unit_price  NUMERIC(10,2) NOT NULL
);

-- 9. payments
CREATE TABLE payments (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    invoice_id      TEXT NOT NULL REFERENCES invoices(id),
    amount          NUMERIC(10,2) NOT NULL,
    method          payment_method NOT NULL,
    reference_no    VARCHAR(100),
    paid_on         DATE NOT NULL,
    received_by     TEXT REFERENCES profiles(id)
);

-- 10. receipts
CREATE TABLE receipts (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    receipt_no  VARCHAR(50) UNIQUE NOT NULL,
    payment_id  TEXT UNIQUE NOT NULL REFERENCES payments(id),
    issued_on   DATE NOT NULL
);

-- 11. workout_plans
CREATE TABLE workout_plans (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    member_id   TEXT NOT NULL REFERENCES members(id),
    trainer_id  TEXT NOT NULL REFERENCES trainers(id),
    title       VARCHAR(200) NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 12. workout_exercises
CREATE TABLE workout_exercises (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    plan_id         TEXT NOT NULL REFERENCES workout_plans(id),
    workout_day     VARCHAR(50) NOT NULL,
    exercise_name   VARCHAR(200) NOT NULL,
    muscle_group    VARCHAR(100),
    sets            INTEGER,
    reps            VARCHAR(50),
    duration        VARCHAR(50),
    rest_time       VARCHAR(50),
    instructions    TEXT
);

-- 13. diet_plans
CREATE TABLE diet_plans (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    member_id   TEXT NOT NULL REFERENCES members(id),
    trainer_id  TEXT NOT NULL REFERENCES trainers(id),
    title       VARCHAR(200) NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 14. diet_items
CREATE TABLE diet_items (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    plan_id     TEXT NOT NULL REFERENCES diet_plans(id),
    meal        VARCHAR(100) NOT NULL,
    food_items  TEXT NOT NULL,
    quantity    VARCHAR(100),
    calories    INTEGER,
    timing      VARCHAR(100),
    notes       TEXT
);

-- 15. progress_records
CREATE TABLE progress_records (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    member_id       TEXT NOT NULL REFERENCES members(id),
    recorded_by     TEXT NOT NULL REFERENCES profiles(id),
    record_date     DATE NOT NULL,
    weight          NUMERIC(5,2),
    height          NUMERIC(5,2),
    measurements    TEXT,
    observations    TEXT,
    photo_url       TEXT
);

-- 16. notices
CREATE TABLE notices (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title       VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    audience    notice_audience NOT NULL DEFAULT 'all',
    status      notice_status NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 17. events
CREATE TABLE events (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name        VARCHAR(300) NOT NULL,
    description TEXT,
    event_date  DATE NOT NULL,
    event_time  VARCHAR(50),
    location    VARCHAR(300),
    image_url   TEXT,
    status      event_status NOT NULL DEFAULT 'upcoming'
);

-- 18. posts
CREATE TABLE posts (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title       VARCHAR(300) NOT NULL,
    body        TEXT NOT NULL,
    category    VARCHAR(100),
    created_by  TEXT NOT NULL REFERENCES profiles(id),
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 19. gym_status
CREATE TABLE gym_status (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    status      gym_status_enum NOT NULL DEFAULT 'OPEN',
    updated_by  TEXT REFERENCES profiles(id),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- 20. audit_logs
CREATE TABLE audit_logs (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id     TEXT REFERENCES profiles(id),
    action      VARCHAR(100) NOT NULL,
    entity      VARCHAR(100) NOT NULL,
    entity_id   TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

---

## Step 4: Create the Auto-Profile Trigger

Run this in the SQL Editor. It auto-creates a `profiles` row when a user signs up via Supabase Auth:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, role)
    VALUES (
        NEW.id::text,
        COALESCE(NEW.raw_user_meta_data ->> 'full_name', 'Unnamed'),
        NEW.email,
        COALESCE(NEW.raw_user_meta_data ->> 'role', 'member')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
```

---

## Step 5: Set Up Authentication

1. Go to **Authentication → Providers** — make sure **Email** is enabled
2. Go to **Authentication → Settings → Email Auth** — turn **OFF** "Enable email confirmations" (for development)

### Create the first admin user

Go to **Authentication → Users → Add User**:
- **Email:** admin email
- **Password:** strong password
- **User Metadata:**
  ```json
  { "full_name": "Admin Name", "role": "admin" }
  ```

The trigger from Step 4 will auto-create the matching `profiles` row.

---

## Step 6: Create the Storage Bucket

1. Go to **Storage** → **New Bucket**
2. Name: **`rv-fitness`**
3. Toggle **Public bucket** = **ON**
4. Click **Create**

### Storage Policies

On the `rv-fitness` bucket, add these policies:

| Policy Name | Operation | Target Roles | Definition |
|---|---|---|---|
| Allow authenticated uploads | INSERT | `authenticated` | `true` |
| Allow public reads | SELECT | `public` | `true` |

---

## Step 7: Enable Row Level Security (RLS)

```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trainers ENABLE ROW LEVEL SECURITY;
ALTER TABLE members ENABLE ROW LEVEL SECURITY;
ALTER TABLE membership_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE diet_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE diet_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE notices ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE gym_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Basic policy: let users read their own profile
CREATE POLICY "Users can read own profile"
    ON profiles FOR SELECT
    USING (auth.uid()::text = id);

-- Admin can do everything on profiles
CREATE POLICY "Admins full access to profiles"
    ON profiles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles p
            WHERE p.id = auth.uid()::text AND p.role = 'admin'
        )
    );
```

---

## Step 8: Seed Initial Data (Optional)

```sql
-- Default gym status
INSERT INTO gym_status (id, status)
VALUES (gen_random_uuid()::text, 'OPEN');

-- Sample membership plans
INSERT INTO membership_plans (id, name, duration_days, price, description, benefits) VALUES
(gen_random_uuid()::text, 'Monthly',     30,  1000.00, '1 Month gym access',  'Gym access\nLocker facility'),
(gen_random_uuid()::text, 'Quarterly',   90,  2500.00, '3 Months gym access', 'Gym access\nLocker facility\n1 Free PT session'),
(gen_random_uuid()::text, 'Half Yearly', 180, 4500.00, '6 Months gym access', 'Gym access\nLocker facility\n3 Free PT sessions'),
(gen_random_uuid()::text, 'Annual',      365, 8000.00, '1 Year gym access',   'Gym access\nLocker facility\n6 Free PT sessions\nDiet plan');
```

---

## ✅ Checklist

- [ ] Create Supabase project
- [ ] Copy API keys to `backend/.env` and `frontend/.env`
- [ ] Run the full schema SQL (Step 3)
- [ ] Run the auto-profile trigger SQL (Step 4)
- [ ] Disable email confirmation for dev (Step 5)
- [ ] Create first admin user with metadata (Step 5)
- [ ] Create `rv-fitness` public storage bucket (Step 6)
- [ ] Add storage upload/read policies (Step 6)
- [ ] Enable RLS + basic policies (Step 7)
- [ ] Seed initial data (Step 8) — optional

---

## ⚠️ Important Reminders

- **NEVER commit `.env` files** — they contain secrets. Both `.env` files are already in `.gitignore`.
- After setup, share the API keys with teammates through a **secure channel** (DM, password manager), not Git.
- The `service_role` key has **full database access** — treat it like a password.
