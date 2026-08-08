<div align="center">

<img src="fe/static/labproflix.png" width="420" alt="Labproflix">

**Movies on demand. Anytime, anywhere.**

A Netflix-style movie streaming platform — browse, buy, and watch.

[labproflix.faizath.com](https://labproflix.faizath.com) · [labproflix-api.faizath.com](https://labproflix-api.faizath.com)

</div>

---

## What is Labproflix?

Labproflix is a movie streaming platform. Visitors browse a catalogue of films, search it by title or director, buy individual titles using an in-app coin balance, and stream whatever they own. Accounts are real: registration is confirmed by email, passwords can be changed while signed in or reset by email if forgotten.

It ships as two surfaces over one backend. The first is a server-rendered Django frontend — the red-and-black interface in the gallery below. The second is a token-authenticated REST API served from its own subdomain, which lets an external admin client manage users, balances, and the film catalogue against the same data. The purple dashboard in the later screenshots is **Nelfix**, a third-party client pointed at the Labproflix API endpoint, included here to show the API working end to end.

### Why it exists

Labproflix was built as the **Project-Based Test submission for the STEI ITB Programming Laboratory Assistant (Asisten Laboratorium Pemrograman) recruitment**. The brief specified the core product and a set of optional bonus tasks — public deployment, live polling, a caching layer, additional account features, and object storage. All of them were attempted; each is documented under [Bonuses](#bonuses).

## Demo

<div align="center">
  <img src="assets/demo.gif" width="100%" alt="Labproflix demo">
</div>

## Screenshots

<table>
<tr>
<td width="50%"><img src="assets/screenshots/1.webp" width="100%" alt="Landing page"><br><sub><b>1.</b> Landing page — hero with Explore and Get Started calls to action</sub></td>
<td width="50%"><img src="assets/screenshots/2.webp" width="100%" alt="Sign in"><br><sub><b>2.</b> Sign in</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/3.webp" width="100%" alt="Browse"><br><sub><b>3.</b> Browse — featured title hero with the signed-in coin balance</sub></td>
<td width="50%"><img src="assets/screenshots/4.webp" width="100%" alt="Available movies"><br><sub><b>4.</b> Available movies grid with title and director search</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/5.webp" width="100%" alt="Movie detail"><br><sub><b>5.</b> Movie detail modal — purchase an unowned title</sub></td>
<td width="50%"><img src="assets/screenshots/6.webp" width="100%" alt="Bought movies"><br><sub><b>6.</b> Bought movies — the user's owned library</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/7.webp" width="100%" alt="Owned title modal"><br><sub><b>7.</b> Owned-title modal — Play replaces Buy</sub></td>
<td width="50%"><img src="assets/screenshots/8.webp" width="100%" alt="Streaming player"><br><sub><b>8.</b> Inline streaming player</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/9.webp" width="100%" alt="Search results"><br><sub><b>9.</b> Search results for "lord"</sub></td>
<td width="50%"><img src="assets/screenshots/10.webp" width="100%" alt="Change password"><br><sub><b>10.</b> Change password for the signed-in user</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/11.webp" width="100%" alt="Sign up"><br><sub><b>11.</b> Sign up</sub></td>
<td width="50%"><img src="assets/screenshots/12.webp" width="100%" alt="Activation sent"><br><sub><b>12.</b> Activation email sent</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/13.webp" width="100%" alt="Activation email"><br><sub><b>13.</b> The activation email as delivered — a signed confirmation link from <code>labproflix@mail.faizath.com</code></sub></td>
<td width="50%"><img src="assets/screenshots/14.webp" width="100%" alt="Email verified"><br><sub><b>14.</b> Email verified — account activated</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/15.webp" width="100%" alt="Password reset request"><br><sub><b>15.</b> Forgot password — request a reset link</sub></td>
<td width="50%"><img src="assets/screenshots/16.webp" width="100%" alt="Reset link sent"><br><sub><b>16.</b> Reset link sent</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/17.webp" width="100%" alt="Password reset email"><br><sub><b>17.</b> The password reset email as delivered — a single-use reset link</sub></td>
<td width="50%"><img src="assets/screenshots/18.webp" width="100%" alt="Enter new password"><br><sub><b>18.</b> Enter a new password from the reset link</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/19.webp" width="100%" alt="Password reset complete"><br><sub><b>19.</b> Password reset complete</sub></td>
<td width="50%"><img src="assets/screenshots/20.webp" width="100%" alt="Nelfix API endpoint"><br><sub><b>20.</b> Nelfix admin client pointed at the Labproflix API endpoint</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/21.webp" width="100%" alt="Nelfix login"><br><sub><b>21.</b> Nelfix — admin login against the API</sub></td>
<td width="50%"><img src="assets/screenshots/22.webp" width="100%" alt="Users management"><br><sub><b>22.</b> Users management — inspect accounts and top up balances</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/23.webp" width="100%" alt="Films management"><br><sub><b>23.</b> Films management — the full catalogue</sub></td>
<td width="50%"><img src="assets/screenshots/24.webp" width="100%" alt="Create film"><br><sub><b>24.</b> Create film</sub></td>
</tr>
<tr>
<td width="50%"><img src="assets/screenshots/25.webp" width="100%" alt="Edit film"><br><sub><b>25.</b> Edit film</sub></td>
<td width="50%"><img src="assets/screenshots/26.webp" width="100%" alt="Films search"><br><sub><b>26.</b> Films search for "lord"</sub></td>
</tr>
</table>

## Installation

1. Clone the repository.

   ```bash
   git clone https://github.com/faizathr/labproflix.git
   cd labproflix
   ```

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then sync the dependencies.

   ```bash
   uv sync
   ```

3. Create your environment file and fill in the variables.

   ```bash
   cp .env.example .env
   ```

4. Point `labpro.local` at localhost. The domain is used as a wildcard (`*.labpro.local`), so the API subdomain needs an entry too.

   ```
   # /etc/hosts
   127.0.0.1 labpro.local
   127.0.0.1 api.labpro.local
   ```

   Adjust `labpro/hosts.py` if you want to use different domains.

5. Start PostgreSQL and Redis.

   ```bash
   docker compose up -d
   ```

6. Seed the database.

   ```bash
   psql -h localhost -p 5432 -U admin labpro < top_10_movies.sql
   ```

   This includes a Django admin account:

   | Field | Value |
   | --- | --- |
   | Username | `admin` |
   | Password | `yvd5CC@y^lQ6!iIdV%!2W^ZnpRXhD5L&` |

7. Run the server.

   ```bash
   uv run manage.py runserver
   ```

## Design Pattern

**Facade** — Logging in is a complex procedure: receive credentials, verify them, create a token, check permissions, and so on. The `AUTH` class in `labpro/auth.py` puts a single simple interface in front of all of it.

**Iterator** — Search queries are cached in Redis to improve performance. Invalidating a stale cache entry means iterating over each cached search query to check whether it is a substring of a column in the newly updated row.

**Adapter** — The `data` attribute of the `Data` class (which constructs REST API output) is built as JSON. For `HttpResponse` to be able to return `Data.data`, it first has to be adapted into a string via the `.get_json()` method.

## Tech Stacks

| Layer | Choice |
| --- | --- |
| Package manager | uv |
| Backend | Django |
| Frontend | Vanilla HTML and JS with the Django template engine, CSS generated from Tailwind CSS |
| Database | PostgreSQL |
| Cache | Redis |
| Object storage | Cloudflare R2 |
| Static files | WhiteNoise |
| Deployment OS | Linux VPS |
| Containerization | Docker |
| HTTP gateway | Gunicorn and Nginx |

## Endpoints

### Backend

| Path | Purpose |
| --- | --- |
| `/` | Homepage |
| `/admin/` | Django administration |
| `/browse` | Browse movies |
| `/accounts/login/` | Login |
| `/accounts/password_reset/` | Request a password reset by email |
| `/accounts/password_reset/done/` | Reset link sent |
| `/accounts/password_reset/confirm/` | Enter a new password |
| `/accounts/password_reset/complete/` | Reset complete |
| `/accounts/password_change/` | Change password while signed in |
| `/accounts/password_change/done/` | Password changed |
| `/accounts/signup/` | Sign up |
| `/accounts/signup/activation-sent` | Activation email sent |
| `/activate/:uuid/:token/` | Activate an account from the emailed link |

### API

| Path | Purpose |
| --- | --- |
| `/` | API root |
| `/films` | List films |
| `/films/:film_id` | Retrieve a single film |
| `/login` | Obtain a token |
| `/self` | The authenticated user |
| `/users` | List users |
| `/users/:user_id` | Retrieve a single user |
| `/users/:user_id/balance` | Adjust a user's balance |
| `/bought` | Films the authenticated user owns |
| `/buy/:film_id` | Buy a film |

## Bonuses

### B02 — Deployment

| Surface | URL |
| --- | --- |
| Backend | https://labproflix.faizath.com |
| API | https://labproflix-api.faizath.com |

### B03 — Polling

Short polling every 1 minute, in `fe/browse.html`:

```javascript
movieListPoll = setInterval(listMovie, 1 * 60 * 1000);
```

### B04 — Caching

Backed by a Redis cache server.

**Reading movie data from the database — 8.17 s**

![Database read, 8.17 seconds](assets/cache-miss.webp)

**Reading the same data from cache — 54.44 ms**

![Cache read, 54.44 milliseconds](assets/cache-hit.webp)

### B10 — Additional features

- Email confirmation on registration
- Change password
- Forgot password via email

### B11 — Object storage

Cloudflare R2.

## Author

**Muhammad Faiz Atharrahman** — 18222063
