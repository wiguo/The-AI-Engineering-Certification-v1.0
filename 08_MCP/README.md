<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 8: Model Context Protocol (MCP)</h1>

### [Quicklinks]()

| Session Sheet | Recording | Slides | Repo | Homework | Feedback |
|:--------------|:----------|:-------|:-----|:---------|:---------|
| [Session 8: MCP](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/08_MCP) |[Recording!](https://us02web.zoom.us/rec/share/rqw5I5hwbOOHy8TrGjnu0IjDJi53ykHb0k897jYfyHqZpgRhUuFP4A18d4NrcEKS.18sNk6Do9XwyaVUy) <br> passcode: `E56&^V+8`| [Session 8 Slides](https://canva.link/k8cixqgkfeghdsn) |You are here! | [Session 8 Assignment](https://forms.gle/TcjjChq38ydMjuqn8) | [Feedback 6/25](https://forms.gle/DvcWDgBXatBWCXqi7) |

## Useful Resources

**MCP (Model Context Protocol)**
- [MCP Official Docs](https://modelcontextprotocol.io/) — Spec, tutorials, and guides
- [MCP-UI](https://mcpui.dev/) — Official standard for interactive UI in MCP
- [MCP Auth Guide (Auth0)](https://auth0.com/blog/mcp-specs-update-all-about-auth/) — Deep dive into MCP auth spec updates

## Main Assignment

In this session, you will build an MCP server with OAuth authentication — a cat
shop application that exposes tools for browsing products, managing a cart, and
checking out.

The main entry point is:

```text
server.py
```

The server implementation lives in:

```text
app/
```

Available MCP tools:

- `list_products`
- `get_product`
- `search_products` *(added in Activity 1)*
- `add_to_cart`
- `update_cart_quantity` *(added in Activity 1)*
- `view_cart`
- `remove_from_cart`
- `checkout`

## Setup

From this folder:

```bash
uv sync
```

Copy the example env file and fill in your OpenAI API key:

```bash
cp .env.example .env
```

## Running the MCP Server

Run the server locally:

```bash
uv run server.py
```

The server starts on `http://localhost:8000`.

### Expose the server with ngrok

In a separate terminal, start an ngrok tunnel:

```bash
ngrok http 8000
```

Copy the ngrok forwarding URL (e.g. `https://xxxx-xx-xx-xx-xx.ngrok-free.app`) and
restart the server with it:

```bash
ISSUER_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app uv run server.py
```

> **Note:** The `ISSUER_URL` must match the public URL clients use to reach the
> server, otherwise OAuth authentication will fail.

## Outline

### Breakout Room #1

- Set up the MCP server with OAuth and the product database
- Explore the MCP tools: `list_products`, `get_product`, `add_to_cart`, `view_cart`, `remove_from_cart`, `checkout`

### Breakout Room #2

- Connect an MCP client to the server
- Build an end-to-end interaction flow using the MCP tools

## Ship

The completed MCP server and client integration!

### Deliverables

- A short Loom of either:
  - the MCP server you built and a demo of the client interacting with it; or
  - the notebook you created for the Advanced Build

## Share

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped an MCP server with OAuth authentication! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and tool integration. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#MCP #ModelContextProtocol #OAuth #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework 

Follow these steps to prepare and submit your homework assignment:

1. Review the MCP server code in `server.py` and the `app/` directory
2. Run the MCP server locally using `uv run server.py`
3. Connect to the server using an MCP client (e.g., Claude Desktop, or a custom client)
4. Test all available tools: browsing products, adding to cart, viewing cart, removing items, and checkout
5. Record a Loom video reviewing what you have learned from this session

## Questions

### Question #1

Why is OAuth important for MCP servers, and what security considerations should you keep in mind when exposing tools to AI clients?

#### Answer

An MCP server exposes **tools that act on real systems and data** — in this app a user's cart, and a `checkout` that places an order. Once that server is reachable over the network, OAuth matters for two reasons:

- **Identity & isolation.** Every cart operation here is keyed by the authenticated username (the `token_users` table maps an access token → user). Without auth the server would have no idea *whose* cart a request touches, and anyone who could reach the endpoint could call the tools. OAuth gives each request a verified user identity so users only see and mutate their own data.
- **Delegated, scoped, revocable access.** The user signs in and consents once; the AI client receives a short-lived (1 hour here), scoped (`read`/`write`) access token plus a refresh token — never the user's password or a long-lived secret. Tokens can be revoked, limiting the blast radius of a leak.

Security considerations when exposing tools to AI clients:

- **Authenticate and authorize every tool call** — never trust the client. Enforce scopes per tool so a read-only client can't reach `checkout`.
- **Use PKCE** on the authorization-code flow (this server/client do) to stop code interception, and **validate redirect URIs strictly**.
- **Bind tokens to the right audience:** `ISSUER_URL` / resource-server URL must match the public URL clients use, or audience validation breaks and tokens can be replayed against the wrong server.
- **Serve over HTTPS** (ngrok provides TLS) so bearer tokens aren't sent in cleartext; keep access tokens short-lived and support revocation.
- **Treat tool inputs as adversarial** — they come from an LLM and may be steered by prompt injection. Use parameterized SQL (the tools do) to prevent injection, and validate arguments.
- **Least privilege + guard high-impact tools.** Tools can mutate state or spend money (`checkout`), so gate destructive/irreversible actions, avoid over-broad scopes, and consider rate limiting. This also limits the "confused deputy" risk where the model is tricked into calling a tool: auth caps the damage to what the user actually authorized.

### Question #2

What is Streamable HTTP transport in MCP, and why might you expose a server publicly with OAuth instead of using a local stdio connection?

#### Answer

**Streamable HTTP** is MCP's network transport (the successor to the older HTTP+SSE transport). The client talks to a single HTTP endpoint — `/mcp` here — sending JSON-RPC requests over POST, and the server can **stream** responses and notifications back over the same connection (SSE-style chunked streaming) when a call is long-running or produces progress. Because it's plain HTTP, it supports many concurrent remote clients and rides on standard infrastructure: TLS, load balancers, proxies, and `Authorization` headers. This server runs it via `mcp.run(transport="streamable-http")`.

**stdio**, by contrast, runs the server as a **subprocess on the same machine** as the client (e.g., Claude Desktop launching a local command) and communicates over stdin/stdout. It's ideal for local, single-user, trusted tools but can't be reached over a network and has no concept of network authentication.

You'd expose the server publicly with OAuth instead of stdio when you want a **hosted, multi-user service** — exactly the cat-shop scenario:

- A single deployment can serve many remote users (web/cloud AI clients that can't spawn a local process), each with their own cart.
- The moment the server is reachable over the network, **authentication becomes mandatory**, and OAuth provides delegated, per-user, scoped, revocable access over standard HTTP headers.
- It enables real hosting concerns — HTTPS/TLS (ngrok here), horizontal scaling, and integration with clients that only speak HTTP.

In short: **stdio = local, trusted, single-user, no network; Streamable HTTP + OAuth = remote, multi-user, internet-exposed**, where per-user identity and authorization are required.

## Activity 1: Extend the MCP Server

Add at least one new tool to the cat shop MCP server (e.g., `search_products`, `update_cart_quantity`, or `get_order_history`). Ensure the new tool integrates properly with the existing database and OAuth authentication. Demo the new tool through an MCP client and include it in your Loom video.

#### Implementation

Two new tools were added to `app/tools.py`, registered automatically through the existing `@mcp.tool()` decorator and `app/__init__.py` import:

- **`search_products(query, category=None, max_price=None)`** — keyword search across product `name` and `description` (parameterized `LIKE`), with optional category and price-ceiling filters, ordered by price. Read-only, so like `list_products`/`get_product` it does not require a user identity.
- **`update_cart_quantity(product_id, quantity)`** — sets the exact quantity of an item already in the cart; a quantity of `0` or less removes it. Like the other cart tools it is **authenticated**: it calls `_get_username()` (which resolves the OAuth access token to a user) so it only ever mutates the caller's own `cart_items` row, and it uses parameterized SQL.

Both tools reuse `oauth_provider._get_db()` and the existing schema, so they inherit the same database and OAuth integration as the original tools.

## Advanced Activity: Build a Custom MCP Client

Build a custom MCP client that connects to the cat shop server over Streamable HTTP, authenticates via OAuth, and orchestrates a multi-step shopping flow (browse → add to cart → checkout). Compare the developer experience of MCP-based tool integration vs. traditional REST API calls.

Include your findings and a demo in your Loom video.
