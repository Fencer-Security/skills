# Supabase audit reference

Read this when Supabase is detected in the stack. Covers checks 2 (database access controls) and the
Supabase half of check 4 (authorization).

The headline failure mode in Supabase apps: **the anon key is in the client (correctly) but RLS is
off, so the anon key grants read/write to every row in every table.** The well-publicized Lovable
RLS incident in early 2026 was exactly this — generated apps shipped with anon keys that worked
because RLS was disabled across many user databases at once.

## Step 1 — Enumerate tables and check RLS state

The source of truth is the running database, not the code. If the user can give you access to query
Supabase (via `psql`, the dashboard, or `supabase` CLI), prefer that. If not, fall back to reading
migration files.

### Via SQL (preferred)

```sql
-- Tables in the public schema and whether RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Tables with RLS enabled but zero policies (this BLOCKS all access via anon/authenticated,
-- but more importantly, AI tools sometimes "fix" this by disabling RLS again)
SELECT t.tablename
FROM pg_tables t
LEFT JOIN pg_policies p ON p.tablename = t.tablename AND p.schemaname = t.schemaname
WHERE t.schemaname = 'public' AND t.rowsecurity = true
GROUP BY t.tablename
HAVING COUNT(p.policyname) = 0;

-- All policies, what they apply to, and the USING/WITH CHECK clauses
SELECT tablename, policyname, cmd, roles, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Via migrations (fallback)

```bash
find . -path "*/supabase/migrations/*.sql" -type f | sort
# or
find . -path "*/migrations/*.sql" -type f | sort
```

For each migration file, look for:

- `CREATE TABLE` statements — the tables that exist.
- `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` — which tables have RLS turned on.
- `CREATE POLICY ...` — the policies.

Map tables → RLS state → policies. Tables with `CREATE TABLE` but no corresponding
`ENABLE ROW LEVEL SECURITY` are the high-risk set.

## Step 2 — Classify each table

For each table in the public schema:

| State                                                                   | Severity                                                    | Note                                                                                                                                                                                                      |
| ----------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RLS off, table contains user data                                       | **Critical**                                                | Anon key reads/writes everything. The headline finding.                                                                                                                                                   |
| RLS off, table is reference data (countries, plans, etc.) and read-only | **Low**                                                     | Still flag, but lower risk if writes are blocked at the app layer.                                                                                                                                        |
| RLS on, zero policies                                                   | **High**                                                    | Currently safe (blocks everything) but fragile — next migration could "fix" this by disabling RLS. Also probably means the app is hitting these tables via the service role key, which has its own risks. |
| RLS on, policy is `USING (true)` for SELECT                             | **Critical**                                                | The policy exists but doesn't restrict anything. Worse than no RLS because it looks safe.                                                                                                                 |
| RLS on, policy uses `auth.uid() = user_id` (or similar)                 | **OK** (verify the column actually exists and is populated) | The good pattern.                                                                                                                                                                                         |
| RLS on, INSERT/UPDATE policy without `WITH CHECK`                       | **High**                                                    | Users can insert rows attributing them to other users. Common AI-generated bug.                                                                                                                           |
| RLS on, but a permissive policy applies to `public` role                | **High**                                                    | Anonymous users get whatever the policy allows. Usually a mistake.                                                                                                                                        |

## Step 3 — Check policy logic for the common bugs

Read the actual policy expressions. The bugs to look for:

**Bug 1 — `USING (true)` policies.** Often added by AI tools as a "make it work" fix. The policy
exists, RLS is on, but every row passes the check.

**Bug 2 — Missing `WITH CHECK` on writes.** A SELECT policy with `USING (auth.uid() = user_id)` is
fine for reads, but if there's no separate INSERT policy with `WITH CHECK (auth.uid() = user_id)`,
an authenticated user can insert rows with `user_id` set to someone else's UUID. Look for this
pattern specifically:

```sql
-- BUG: only restricts reads
CREATE POLICY "users_own_data" ON profiles
  FOR ALL USING (auth.uid() = user_id);
-- The FOR ALL is misleading — without WITH CHECK, INSERTs are unrestricted.
```

**Bug 3 — Policies referencing columns that don't exist or aren't enforced.** If a policy says
`auth.uid() = user_id` but the `user_id` column is nullable and the application doesn't always set
it, rows with `NULL user_id` may behave unexpectedly.

**Bug 4 — Service role key used in client code paths.** Search the codebase:

```bash
grep -rE "service_role|SUPABASE_SERVICE_ROLE" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" .
```

The service role key bypasses RLS entirely. It should appear ONLY in server-side code (API routes,
server actions, edge functions). If you find it in:

- A `'use client'` component → **Critical**.
- A file imported by a `'use client'` component → **Critical**.
- A page or layout without `'use server'` → **Critical** (will be bundled to the client).
- An environment variable prefixed `NEXT_PUBLIC_*`, `VITE_*`, etc. → **Critical**.

## Step 4 — Authorization patterns (check 4)

In a properly-configured Supabase app, RLS _is_ the authorization layer. If RLS is healthy, check 4
is largely satisfied. The remaining concerns:

**Server-side queries that bypass RLS.** Any code path using the service role key needs to do its
own authorization. Look for service-role queries that don't check `auth.uid()` against the resource
being accessed:

```ts
// BUG: service role key bypasses RLS, but the code doesn't check ownership
const { data } = await supabaseAdmin.from("orders").select("*").eq("id", req.query.orderId);
```

This is IDOR — change the orderId, get someone else's order. Flag any service-role query against a
user-owned resource that doesn't filter by the authenticated user. **Severity: High to Critical**
depending on the data.

**Edge functions / API routes that re-implement authz.** If an endpoint uses the user's JWT to query
(good — RLS enforces), it's fine. If it uses the service role key, it must do explicit
authorization. Read each edge function and route handler that handles user data and verify.

**Storage policies.** Supabase Storage has its own RLS-style policies on buckets. If the app uploads
files (avatars, attachments), check `storage.objects` policies the same way as table policies:

```sql
SELECT * FROM pg_policies WHERE schemaname = 'storage';
```

Buckets without policies are publicly readable if the bucket is set to public — **Critical** if the
bucket holds user-uploaded content.

## What to put in the report

For each table, one finding (don't write a finding per row of the classification table — group "8
tables with RLS disabled" into one Critical finding listing the tables). For each policy bug, one
finding with the table name, policy name, and the specific bug. For service-role-in-client, one
finding per file (these need individual fixes).

Cross-reference: a single tier of findings ("RLS off on `users`, `orders`, `payments`") is more
actionable than scattering them across the report.
