/**
 * Node.js/Express proxy for fetching tweets.
 *
 * Why a proxy: the RapidAPI key must stay on the server. If the browser
 * called RapidAPI directly, the key would be visible to anyone using the app.
 *
 * Endpoint:
 *   GET /tweets?username=<name>&limit=<1-20>
 *
 * Run:
 *   npm install
 *   copy .env.example to .env and add your key
 *   npm start
 */

require("dotenv").config();

const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;
const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY;
const RAPIDAPI_HOST = "twitter154.p.rapidapi.com";

if (!RAPIDAPI_KEY) {
  console.error("Missing RAPIDAPI_KEY. Add it to Backend/.env (see .env.example).");
  process.exit(1);
}

app.use(cors());

// Twitter usernames: letters, numbers, underscore, 1-15 characters
const USERNAME_PATTERN = /^[A-Za-z0-9_]{1,15}$/;

app.get("/tweets", async (req, res) => {
  const username = (req.query.username || "").replace(/^@/, "").trim();
  const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 10, 1), 20);

  if (!USERNAME_PATTERN.test(username)) {
    return res.status(400).json({ message: "Invalid username" });
  }

  try {
    const response = await axios.get(`https://${RAPIDAPI_HOST}/user/tweets`, {
      params: {
        username,
        limit,
        include_replies: "false",
        include_pinned: "false",
      },
      headers: {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
      },
      timeout: 15000,
    });
    res.json(response.data);
  } catch (error) {
    console.error("Failed to fetch tweets:", error.message);
    res.status(502).json({ message: "Failed to fetch tweets" });
  }
});

app.listen(PORT, () => {
  console.log(`Tweet proxy running on http://localhost:${PORT}`);
});
