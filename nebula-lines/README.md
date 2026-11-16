# Nebula Lines — Human vs AI

Created for TECH 3500 Week 6 AS1 Lab #6: Play with AI — Jalen Black.

**Live game:** https://nebula-lines-ai-game.onrender.com

**Source:** https://github.com/jkblack0706-jpg/StudyPilot-AI-Study-Coach/tree/main/nebula-lines

A self-contained HTML/CSS/JavaScript strategy game with no paid services or dependencies. Two sides alternate placing beacons on a 6×6 board with four permanently blocked asteroid cells. The first side to connect four horizontally, vertically, or diagonally wins. A filled board is a draw. The player goes first and can restart or play multiple games.

The computer opponent is an **algorithmic AI**, not a generative chatbot or Gemini API. It finds immediate wins and blocks, otherwise evaluates the board using depth-three minimax with alpha-beta pruning, candidate move ordering, and pattern-based scoring. The on-screen AI status reports decisions. The app runs entirely in the browser and retains score only during the active page session.

To test locally, open `index.html` in any modern browser; no setup or API key is necessary. To test a winning line, try placing four adjacent beacons while accounting for the AI's responses; the engine correctly stops when any of four orientations wins. Responsive layout includes accessible cell labels and score tracking.

**Original twist:** the four asteroid cells make an otherwise familiar connection mechanic into a tactical, constrained starfield with many possible blockades. **Disclosure:** built with assistance from OpenAI ChatGPT; user should review the code and disclose assistance according to the class rules.
