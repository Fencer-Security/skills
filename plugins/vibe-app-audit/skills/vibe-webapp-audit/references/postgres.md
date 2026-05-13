# Plain Postgres + app-layer authz reference

Read this when the app uses Postgres (or another SQL database) directly with an ORM/query builder,
with authorization enforced in application code rather than via database RLS. Covers checks 2
(database access controls) and the app-layer half of check 4 (authorization).

The mental model is different from Supabase: there's no RLS doing automatic filtering. Every query
that returns user-scoped data must include the authenticated user's ID in its `WHERE` clause, and
the framework's middleware/decorator system must enforce that the user is authorized for the action
_before_ the query runs.

The headline failure mode: **endpoints that take a resource ID from the URL or body, fetch by ID,
and return without checking ownership.** This is IDOR and it's the single most common AI-generated
authorization bug.

## Step 1 — Map the request flow

Figure out how the app authenticates and authorizes requests. Detect the framework first:

```bash
# Express / Fastify / Next API routes
grep -E '"(express|fastify|next)"' package.json

# Django / FastAPI / Flask
grep -E "(django|fastapi|flask)" requirements.txt pyproject.toml

# Rails
[ -f Gemfile ] && grep -E "rails" Gemfile
```

For each framework, the authz patterns to look for:

**Express / Fastify / generic Node:**

- Auth middleware that verifies a JWT or session and attaches `req.user`.
- Per-route authorization — either in middleware (`requireOwner('post')`) or inline
  (`if (post.user_id !== req.user.id) return res.status(403)`).

**Next.js App Router (API routes / Server Actions):**

- `auth()` / `getServerSession()` calls at the top of each handler.
- Explicit `if (!session) return unauthorized()` AND
  `if (resource.userId !== session.user.id) return forbidden()`.

**Django:**

- `@login_required` and DRF permission classes (`IsAuthenticated`, `IsOwner`).
- `get_queryset()` overrides that filter by `request.user`.

**FastAPI:**

- `Depends(get_current_user)` on each endpoint.
- Explicit ownership check inside each handler.

**Rails:**

- `before_action :authenticate_user!`.
- Pundit or CanCan policies (or manual ownership checks).

## Step 2 — Audit each user-data endpoint

Find route handlers that touch user data:

```bash
# Next.js App Router routes
find . -name "route.ts" -o -name "route.js" 2>/dev/null | grep -v node_modules

# Express-style routes
grep -rE "(app|router)\.(get|post|put|patch|delete)\(" \
  --include="*.ts" --include="*.js" . 2>/dev/null | grep -v node_modules

# Django views/viewsets
grep -rE "class.*ViewSet|def get_queryset|@api_view" --include="*.py" . 2>/dev/null

# FastAPI endpoints
grep -rE "@(app|router)\.(get|post|put|patch|delete)" --include="*.py" . 2>/dev/null

# Rails controllers
find . -path "*/app/controllers/*.rb" 2>/dev/null
```

For each handler that takes a resource ID (params, query, body) and reads or writes user-scoped
data, verify:

1. **Authentication is enforced.** A user identity must be available to the handler.
2. **Ownership is checked.** Either the query filters by the user's ID, or the handler checks
   ownership after fetching.
3. **The check happens before the action.** Not after — by then it's too late for writes.

### The patterns to flag

**Pattern: fetch-by-id without ownership filter.**

```ts
// BUG: no ownership check
app.get("/api/orders/:id", requireAuth, async (req, res) => {
    const order = await db.order.findUnique({ where: { id: req.params.id } });
    res.json(order);
});
```

Severity: **High** to **Critical** (Critical if the data is sensitive — orders, messages, files).

**Pattern: ownership check on read but not on write.**

```ts
// BUG: GET checks ownership, but PATCH doesn't
app.patch("/api/orders/:id", requireAuth, async (req, res) => {
    await db.order.update({ where: { id: req.params.id }, data: req.body });
    res.json({ ok: true });
});
```

Severity: **Critical**. Writes without ownership checks are worse than reads.

**Pattern: trusting client-supplied user ID.**

```ts
// BUG: req.body.userId is attacker-controlled
app.post("/api/posts", requireAuth, async (req, res) => {
    const post = await db.post.create({
        data: { ...req.body, userId: req.body.userId },
    });
    res.json(post);
});
```

Should be `userId: req.user.id`. Severity: **Critical**.

**Pattern: ownership check via user-supplied data.**

```python
# BUG: filtering by request.data['user_id'] instead of request.user.id
queryset = Order.objects.filter(user_id=request.data['user_id'])
```

Severity: **Critical**.

**Pattern: `get_queryset` that doesn't filter (Django).**

```python
# BUG: ViewSet exposes all rows to any authenticated user
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
```

The `IsAuthenticated` permission only checks that _some_ user is logged in, not that they own the
row. Should override `get_queryset` to filter by `self.request.user`. Severity: **Critical**.

**Pattern: admin endpoints with no role check.**

```ts
// BUG: any authenticated user can call this
app.post('/api/admin/users/:id/ban', requireAuth, async (req, res) => { ... });
```

Severity: **Critical**.

## Step 3 — Check the database connection itself

```bash
# Connection string patterns
grep -rE "(postgres|postgresql|mysql)://" --include="*.ts" --include="*.js" --include="*.py" --include="*.env*" . 2>/dev/null

# ORM config
find . -name "schema.prisma" -o -name "drizzle.config*" -o -name "knexfile*" 2>/dev/null
```

Things to flag:

- Connection strings with embedded credentials in committed files: **Critical** (also caught by
  check 1).
- A single database role with all permissions used for both reads and writes from public-facing
  handlers: **Low** (defense-in-depth concern, not a vuln by itself).
- `sslmode=disable` or no SSL specified for a remote database: **Medium**.

## Step 4 — Check for raw SQL with string interpolation

```bash
grep -rnE "(query|execute|raw)\([\"\`].*\$\{|format\(.*%s" --include="*.ts" --include="*.js" --include="*.py" . 2>/dev/null | grep -v node_modules | head -20
```

Any SQL built with string concatenation or template interpolation of user input is a SQL injection
candidate. Severity: **Critical** if user input reaches it, **High** if input is "trusted" but still
concatenated. ORMs and parameterized queries are the fix.

## What to put in the report

Group findings by endpoint when possible — "5 endpoints in `routes/orders.ts` lack ownership checks"
is more useful than five separate findings. List the specific endpoints and the specific check
they're missing. Each finding gets one fix sentence ("Add `WHERE user_id = req.user.id` to the
query" or "Wrap with `requirePermission('order:read')` middleware").

If the codebase has a consistent pattern (e.g., uses Pundit policies everywhere) and a few endpoints
break the pattern, frame the finding that way: "Most endpoints use Pundit `authorize` calls; these
three skip it." That's more actionable than a generic "missing authz" note.
