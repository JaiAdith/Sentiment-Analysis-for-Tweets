const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

app.get("/tweets", async (req, res) => {
  const { username, limit, include_replies, include_pinned } = req.query;

  const options = {
    method: "GET",
    url: "https://twitter154.p.rapidapi.com/user/tweets",
    params: {
      username,
      limit,
      include_replies,
      include_pinned,
    },
    headers: {
      "X-RapidAPI-Key": "70d3878e01msh2cbbd677f007d41p1b46e2jsn8eac06958d08",
      "X-RapidAPI-Host": "twitter154.p.rapidapi.com",
    },
  };

  try {
    const response = await axios.request(options);
    res.json(response.data);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Failed to fetch tweets" });
  }
});

app.listen(PORT, () => {
  console.log(Serverisrunningonport$ {PORT});
});